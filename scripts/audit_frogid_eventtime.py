#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, re, urllib.request, zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

URL="https://dwca-exports.ala.org.au/dr14760.zip"
SHA="f5dd70ed07956e3e37de4fb04692b83a9d726eae2312767c9eda2dcbf61f759d"
NS={"dwc":"http://rs.tdwg.org/dwc/text/"}

def fetch():
    q=urllib.request.Request(URL,headers={"User-Agent":"frogcs-time-semantics/0.1"})
    with urllib.request.urlopen(q,timeout=180) as r:
        b=r.read()
    if hashlib.sha256(b).hexdigest()!=SHA:
        raise RuntimeError("FrogID source SHA drift")
    return b

def local_term(x):
    return x.rsplit("/",1)[-1].rsplit("#",1)[-1] if x else ""

def decode_sep(x,default):
    if x is None:return default
    return bytes(x,"utf-8").decode("unicode_escape")

def classify(t):
    s=t.strip()
    if not s:return "blank"
    if re.fullmatch(r"\d{1,2}:\d{2}(?::\d{2}(?:\.\d+)?)?",s):
        return "bare_time"
    if re.search(r"Z$",s,re.I):
        return "utc_Z"
    if re.search(r"[+-]\d{2}:?\d{2}$",s):
        return "explicit_offset"
    if "T" in s and re.search(r"\d{1,2}:\d{2}",s):
        return "datetime_like"
    return "other"

def parse_hour(t):
    m=re.search(r"(\d{1,2}):(\d{2})(?::(\d{2}(?:\.\d+)?))?",t.strip())
    if not m:return None
    h=int(m.group(1))+int(m.group(2))/60
    if m.group(3):h+=float(m.group(3))/3600
    return h if 0<=h<24 else None

def main():
    b=fetch()
    zf=zipfile.ZipFile(io.BytesIO(b))
    meta=ET.fromstring(zf.read("meta.xml"))
    core=meta.find("dwc:core",NS)
    files=core.find("dwc:files",NS)
    loc=files.find("dwc:location",NS)
    fields={local_term(f.attrib.get("term","")):int(f.attrib["index"]) for f in core.findall("dwc:field",NS)}
    for required in ("eventID","eventTime","eventDate"):
        if required not in fields:raise RuntimeError("missing "+required)
    delim=decode_sep(core.attrib.get("fieldsTerminatedBy"),"\t")
    quote=decode_sep(core.attrib.get("fieldsEnclosedBy"),'"')
    ignore=int(core.attrib.get("ignoreHeaderLines","0"))
    enc=core.attrib.get("encoding","UTF-8").replace("-","")
    reader=csv.reader(io.StringIO(zf.read(loc.text.strip()).decode(enc,errors="replace")),delimiter=delim,quotechar=quote or '"')
    for _ in range(ignore):next(reader,None)

    seen={}
    for row in reader:
        eid=row[fields["eventID"]].strip()
        if not eid or eid in seen:continue
        t=row[fields["eventTime"]].strip()
        d=row[fields["eventDate"]].strip()
        seen[eid]=(t,d)

    classes=Counter()
    parse_fail=0
    hour_min=24.0;hour_max=-1.0
    for t,d in seen.values():
        classes[classify(t)]+=1
        h=parse_hour(t)
        if h is None:
            parse_fail+=1
        else:
            hour_min=min(hour_min,h);hour_max=max(hour_max,h)

    explicit=classes["utc_Z"]+classes["explicit_offset"]
    n=len(seen)
    result={
      "audit":"frogid_eventtime_semantics_v0_1",
      "contract":"FROGID_TIME_SEMANTICS_CONTRACT_V0_1.json",
      "source_sha256":SHA,
      "distinct_events":n,
      "format_counts":dict(sorted(classes.items())),
      "explicit_offset_or_Z_events":explicit,
      "explicit_offset_or_Z_fraction":explicit/n if n else None,
      "parse_failures":parse_fail,
      "parsed_hour_range":[hour_min if hour_max>=0 else None,hour_max if hour_max>=0 else None],
      "interpretation":(
        "eventTime contains explicit timezone information; cyclic-hour code requires timezone-aware repair"
        if explicit else
        "eventTime values contain no explicit UTC/offset marker; cyclic-hour covariate is wall-clock time as supplied and should not be described as independently verified local solar time"
      ),
      "weather_effect_values_read":False
    }
    Path("frogid_eventtime_semantics_v0_1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":main()
