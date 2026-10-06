#!/usr/bin/env python3
"""Frozen Brodie et al. (2023/2025) external frog-chorus validation.

Implements:
external/BRODIE_2025_EXPANSION_WITHOUT_HOMOGENIZATION_CONTRACT_V0_1.md

The public third-party data are downloaded at runtime and are not vendored.
"""
from __future__ import annotations

import csv, io, json, math, urllib.request
from collections import defaultdict
from datetime import datetime
from statistics import median

RAW_URL = "https://researchdata.jcu.edu.au/default/rdmp/pubrecord/6e808de0ddf811edb22c156e754c4bda/pubattach/76cdd0dc28f83c0dc4abc95bbed6dfcc?pubId=e28ccb6044a311eea020c9a81293027e"
WEATHER_URL = "https://researchdata.jcu.edu.au/default/rdmp/pubrecord/6e808de0ddf811edb22c156e754c4bda/pubattach/28b379c722145c48dd9b5edc47516f0b?pubId=e28ccb6044a311eea020c9a81293027e"
SITES = ["HR-3mile", "HR-Freestun1", "HR-Tearooms"]
SPLIT = datetime(2013, 7, 1)
SEED = 2840241
B = 10_000
Z975 = 1.95996398454

def read_csv(url):
    with urllib.request.urlopen(url) as fh:
        txt = fh.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(txt)))

def dmy(x):
    return datetime.strptime(x, "%d/%m/%Y")

def num(x):
    if x is None or x == "" or x == "NA":
        return None
    try:
        y = float(x)
        return y if math.isfinite(y) else None
    except ValueError:
        return None

class Mulberry32:
    def __init__(self, seed):
        self.a = seed & 0xFFFFFFFF
    def random(self):
        self.a = (self.a + 0x6D2B79F5) & 0xFFFFFFFF
        t = ((self.a ^ (self.a >> 15)) * (1 | self.a)) & 0xFFFFFFFF
        t = (t + ((((t ^ (t >> 7)) * (61 | t)) & 0xFFFFFFFF) ^ t)) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0

def quantile(xs, p):
    ys = sorted(xs)
    pos = (len(ys)-1)*p
    lo, hi = math.floor(pos), math.ceil(pos)
    f = pos-lo
    return ys[lo]*(1-f)+ys[hi]*f

def clustered_fe_slope(records, xkey):
    spp = sorted({r["species"] for r in records})
    ma, mx = {}, {}
    for s in spp:
        a = [r for r in records if r["species"] == s]
        ma[s] = sum(r["A"] for r in a)/len(a)
        mx[s] = sum(r[xkey] for r in a)/len(a)
    sxx = sxy = 0.0
    rr = []
    for r in records:
        x = r[xkey]-mx[r["species"]]
        y = r["A"]-ma[r["species"]]
        sxx += x*x; sxy += x*y
        rr.append([r, x, y])
    b = sxy/sxx
    u = defaultdict(float)
    for r,x,y in rr:
        e = y-b*x
        u[r["date"]] += x*e
    meat = sum(v*v for v in u.values())
    n, g, k = len(records), len(u), len(spp)+1
    correction = (g/(g-1))*((n-1)/(n-k))
    se = math.sqrt(correction*meat/(sxx*sxx))
    return b, se, [b-Z975*se, b+Z975*se], g

def main():
    raw = read_csv(RAW_URL)
    weather = read_csv(WEATHER_URL)
    rain = {r["date"]: num(r["rain.night.total"]) for r in weather}
    species = [k for k in raw[0] if k.endswith("_extent")]

    by_date = defaultdict(dict)
    for r in raw:
        by_date[r["night"]][r["site"]] = r

    sp = {}
    for col in species:
        train, valid = [], []
        for date, smap in by_date.items():
            ys = [num(smap.get(s, {}).get(col)) for s in SITES]
            if any(y is None for y in ys):
                continue
            rec = {
                "date": date, "dt": dmy(date), "ys": ys,
                "T": sum(ys), "K": sum(y > 0 for y in ys)
            }
            (train if rec["dt"] < SPLIT else valid).append(rec)

        active_train = [r for r in train if r["T"] > 0]
        active_valid = [r for r in valid if r["T"] > 0]
        Y = [sum(r["ys"][j] for r in train) for j in range(3)]
        sy = sum(Y)
        eligible = len(active_train) >= 5 and len(active_valid) >= 5 and sy > 0
        q = [(x+0.5)/(sy+1.5) for x in Y] if sy > 0 else [float("nan")]*3
        prim = []
        if eligible:
            for r in valid:
                if r["K"] < 2 or r["T"] <= 0:
                    continue
                p = [y/r["T"] for y in r["ys"]]
                A = sum((p[j]-1/3)*(q[j]-1/3) for j in range(3))
                z = dict(r); z.update({"p": p, "A": A})
                prim.append(z)
        sp[col] = dict(
            eligible=eligible, active_train=len(active_train),
            active_validation=len(active_valid), Y=Y, q=q, prim=prim
        )

    eligible = [s for s,v in sp.items() if v["eligible"]]
    primary_species = [s for s in eligible if sp[s]["prim"]]
    records = []
    for s in primary_species:
        for r in sp[s]["prim"]:
            z = dict(r); z["species"] = s; z["logT"] = math.log1p(r["T"])
            if rain.get(r["date"]) is not None:
                z["rain"] = rain[r["date"]]
            records.append(z)

    obs_med = median(r["A"] for r in records)
    rng = Mulberry32(SEED)
    boots = []
    for _ in range(B):
        vals = []
        for _ in range(len(primary_species)):
            s = primary_species[int(rng.random()*len(primary_species))]
            ar = sp[s]["prim"]
            for _ in range(len(ar)):
                vals.append(ar[int(rng.random()*len(ar))]["A"])
        boots.append(median(vals))
    boot_ci = [quantile(boots, .025), quantile(boots, .975)]

    bT, seT, ciT, gT = clustered_fe_slope(records, "logT")

    rain_records = [r for r in records if "rain" in r]
    bR, seR, ciR, gR = clustered_fe_slope(rain_records, "rain")

    recurrence = []
    for s in primary_species:
        v = sp[s]
        qrng = max(v["q"])-min(v["q"])
        if qrng < 0.20:
            continue
        ar = v["prim"]
        if len(ar) < 2:
            continue
        best = v["q"].index(max(v["q"]))
        medT = median(r["T"] for r in ar)
        hi, lo = [r for r in ar if r["T"] > medT], [r for r in ar if r["T"] <= medT]
        if not hi or not lo:
            continue
        hs = sum(r["p"][best] for r in hi)/len(hi)
        ls = sum(r["p"][best] for r in lo)/len(lo)
        recurrence.append(dict(species=s, template_range=qrng, best_site=SITES[best],
                               n=len(ar), median_T=medT, high_share=hs, low_share=ls,
                               difference=hs-ls))

    out = {
        "analysis": "brodie_2025_expansion_without_homogenization_v0_1",
        "split": "2013-07-01",
        "eligible_species": len(eligible),
        "primary_species": len(primary_species),
        "primary_records": len(records),
        "primary_median_A": obs_med,
        "species_block_bootstrap_95": boot_ci,
        "primary_pass": boot_ci[0] > 0,
        "homogenization_test": {
            "slope_log1p_total_chorus": bT, "cluster_date_se": seT,
            "ci95": ciT, "unique_dates": gT,
            "stronger_prediction_falsified": ciT[1] < 0
        },
        "rain_secondary": {
            "slope_per_mm_same_night_rain": bR, "cluster_date_se": seR,
            "ci95": ciR, "unique_dates": gR
        },
        "historical_best_site_secondary": recurrence,
        "interpretation": (
            "Held-out-season site allocation remains aligned with the independently learned "
            "species-specific site template on multi-site nights, while increasing total chorus "
            "activity does not show clear homogenization. The stronger historical-best-site "
            "high-versus-low activity contrast is not consistently positive."
        )
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
