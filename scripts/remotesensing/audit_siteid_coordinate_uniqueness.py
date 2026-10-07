#!/usr/bin/env python3
import csv,hashlib,io,json,urllib.request
from collections import defaultdict
URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
req=urllib.request.Request(URL,headers={"User-Agent":"frogcs-siteid-uniqueness/0.1"})
with urllib.request.urlopen(req,timeout=180) as r:b=r.read()
assert hashlib.sha256(b).hexdigest()==SHA
d=defaultdict(list)
for r in csv.DictReader(io.StringIO(b.decode("utf-8-sig"))):
    sid=(r.get("SiteID") or "").strip()
    if sid:d[sid].append((r.get("RouteNumber"),r.get("lat"),r.get("lon")))
dup={k:v for k,v in d.items() if len(v)>1}
conf={k:v for k,v in dup.items() if len(set(v))>1}
out={"rows":sum(len(v) for v in d.values()),"unique_siteids":len(d),"duplicate_siteids":len(dup),"conflicting_duplicate_siteids":len(conf),"examples":dict(list(conf.items())[:20])}
print(json.dumps(out,indent=2))
