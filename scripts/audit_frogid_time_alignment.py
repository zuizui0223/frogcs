#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, math, re, urllib.request, zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from timezonefinder import TimezoneFinder

URL="https://dwca-exports.ala.org.au/dr14760.zip"
SHA="f5dd70ed07956e3e37de4fb04692b83a9d726eae2312767c9eda2dcbf61f759d"
NS={"dwc":"http://rs.tdwg.org/dwc/text/"}

def fetch():
    q=urllib.request.Request(URL,headers={"User-Agent":"frogcs-time-alignment/0.2"})
    with urllib.request.urlopen(q,timeout=180) as r:b=r.read()
    if hashlib.sha256(b).hexdigest()!=SHA:raise RuntimeError("source SHA drift")
    return b

def local_term(x):return x.rsplit("/",1)[-1].rsplit("#",1)[-1] if x else ""
def decode_sep(x,default):return default if x is None else bytes(x,"utf-8").decode("unicode_escape")
def selected(eid):return hashlib.sha256(eid.encode()).digest()[0]<16

def parse_dt(d,t):
    d0=str(d).strip()[:10]
    t0=str(t).strip()
    if "T" in t0:
        s=t0
    else:
        s=d0+"T"+t0
    if s.endswith("Z"):s=s[:-1]+"+00:00"
    dt=datetime.fromisoformat(s)
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("eventTime lacks usable offset")
    return dt

def circ_hour_diff(a,b):
    d=abs(a-b)%24
    return min(d,24-d)

def main():
    zf=zipfile.ZipFile(io.BytesIO(fetch()))
    meta=ET.fromstring(zf.read("meta.xml"));core=meta.find("dwc:core",NS)
    loc=core.find("dwc:files",NS).find("dwc:location",NS).text.strip()
    fields={local_term(f.attrib.get("term","")):int(f.attrib["index"]) for f in core.findall("dwc:field",NS)}
    req={"eventID","eventDate","eventTime","decimalLatitude","decimalLongitude","coordinateUncertaintyInMeters"}
    if req-set(fields):raise RuntimeError("missing fields "+str(sorted(req-set(fields))))
    reader=csv.reader(
        io.StringIO(zf.read(loc).decode(core.attrib.get("encoding","UTF-8").replace("-",""),errors="replace")),
        delimiter=decode_sep(core.attrib.get("fieldsTerminatedBy"),"\t"),
        quotechar=decode_sep(core.attrib.get("fieldsEnclosedBy"),'"') or '"',
    )
    for _ in range(int(core.attrib.get("ignoreHeaderLines","0"))):next(reader,None)

    events={}
    for row in reader:
        eid=row[fields["eventID"]].strip()
        if not eid or eid in events or not selected(eid):continue
        try:
            lat=float(row[fields["decimalLatitude"]].strip());lon=float(row[fields["decimalLongitude"]].strip())
            unc=float(row[fields["coordinateUncertaintyInMeters"]].strip())
            if not(-90<=lat<=90 and -180<=lon<=180) or not math.isfinite(unc) or unc>25000:continue
            d=row[fields["eventDate"]].strip()
            t=row[fields["eventTime"]].strip()
            dt=parse_dt(d,t)
        except Exception:
            continue
        events[eid]=(lat,lon,d,t,dt)

    tf=TimezoneFinder(in_memory=True)
    offset_match=0;date_match=0;hour_match=0
    tz_fail=0;parse_n=len(events)
    diff_hist=Counter();offset_diff=Counter()
    for lat,lon,d,t,dt in events.values():
        tzname=tf.timezone_at(lng=lon,lat=lat)
        if not tzname:
            tz_fail+=1;continue
        local=dt.astimezone(ZoneInfo(tzname))
        supplied_offset=int(dt.utcoffset().total_seconds()//60)
        expected_offset=int(local.utcoffset().total_seconds()//60)
        if supplied_offset==expected_offset:offset_match+=1
        offset_diff[expected_offset-supplied_offset]+=1

        raw_date=date.fromisoformat(str(d)[:10])
        if local.date()==raw_date:date_match+=1

        rawhour=dt.hour+dt.minute/60+dt.second/3600+dt.microsecond/3.6e9
        localhour=local.hour+local.minute/60+local.second/3600+local.microsecond/3.6e9
        hd=circ_hour_diff(rawhour,localhour)
        if hd<1e-9:hour_match+=1
        bucket=round(hd,3)
        diff_hist[bucket]+=1

    denom=parse_n-tz_fail
    result={
      "audit":"frogid_time_alignment_v0_2",
      "contract":"FROGID_TIME_ALIGNMENT_CONTRACT_V0_2.json",
      "source_sha256":SHA,
      "retained_deterministic_events":parse_n,
      "timezone_resolution_failures":tz_fail,
      "comparable_events":denom,
      "supplied_offset_matches_coordinate_timezone":offset_match,
      "offset_match_fraction":offset_match/denom if denom else None,
      "converted_local_date_matches_eventDate":date_match,
      "date_match_fraction":date_match/denom if denom else None,
      "converted_local_hour_matches_supplied_wall_clock":hour_match,
      "hour_match_fraction":hour_match/denom if denom else None,
      "offset_difference_minutes":{str(k):v for k,v in sorted(offset_diff.items())},
      "circular_hour_difference_counts":{str(k):v for k,v in sorted(diff_hist.items())},
      "weather_values_read":False,
      "frogid_effect_values_read":False
    }
    Path("frogid_time_alignment_v0_2.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":main()
