#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
obj=json.loads((root/"ECOLOGICAL_FIGURE_HASHES_V0_1.json").read_text())
bad=[]
for rel,exp in obj["figures"].items():
    p=root/rel
    got=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    if got!=exp:
        bad.append({"path":rel,"expected":exp,"got":got})
if bad:
    raise SystemExit("ecological figure hash mismatch: "+json.dumps(bad,sort_keys=True))
print({"figures_verified":len(obj["figures"]),"status":"PASS"})
