#!/usr/bin/env python3
import json, re, urllib.request

PARENT="609955c9d34ea221ce33c534"
BASE="https://www.sciencebase.gov/catalog"
def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-dswemod-year-files/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode())

children=get_json(f"{BASE}/items?parentId={PARENT}&format=json&max=100").get("items") or []
years={}
for x in children:
    title=x.get("title") or ""
    m=re.search(r"\b(20(?:0[3-9]|1[0-5]))\b",title)
    if not m:
        continue
    y=int(m.group(1))
    item=get_json(f"{BASE}/item/{x['id']}?format=json")
    files=[]
    for f in item.get("files") or []:
        files.append({
          "name":f.get("name"),"size":f.get("size"),"contentType":f.get("contentType"),
          "downloadUri":f.get("downloadUri"),"url":f.get("url")
        })
    years[str(y)]={"id":x["id"],"title":title,"files":files}

print(json.dumps({
 "analysis":"dswemod_year_file_preflight_v0_1",
 "years":years,
 "expected_years":list(range(2003,2016)),
 "complete_year_set":sorted(map(int,years))==list(range(2003,2016)),
 "raster_values_read":False,"frog_data_used":False
},indent=2))
