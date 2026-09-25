#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SRC=ROOT/"run_naamp_secondary.py"
spec=importlib.util.spec_from_file_location("naamp_secondary",SRC)
base=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

PRIMARY_FORMULA="prop ~ rain_z * shoulder + C(State) + C(RunNumber) + C(RouteType) + year_z"
FOUR_FORMULA="prop ~ rain_z * shoulder + C(State) + C(RouteType) + year_z"

def main():
    df,state_last=base.base_frame(base.load())
    hdf=df[df.state_last_window.isin([3,4])].copy()

    primary=base.fit(hdf,PRIMARY_FORMULA,"rain_z:shoulder")
    primary["support_rule_pass_descriptive_only"]=bool(
        primary["beta"]<0 and primary["p_value"]<0.05 and primary["ci95_beta"][1]<0
    )

    four=hdf[hdf.state_last_window==4].copy()
    four_result=base.fit(four,FOUR_FORMULA,"rain_z:shoulder")
    four_result["support_rule_pass_descriptive_only"]=bool(
        four_result["beta"]<0 and four_result["p_value"]<0.05 and four_result["ci95_beta"][1]<0
    )

    result={
      "analysis":"naamp_h3_specification_repair_v0_1",
      "contract":"NAAMP_H3_SPECIFICATION_REPAIR_CONTRACT_V0_1.json",
      "status":"post_opening_specification_repair_not_confirmatory",
      "original_h3_result_reused":False,
      "primary":{"formula":PRIMARY_FORMULA,"result":primary},
      "four_window_sensitivity":{"formula":FOUR_FORMULA,"result":four_result},
      "state_last_window_counts":{str(k):int(v) for k,v in __import__("pandas").Series(state_last).value_counts().sort_index().items()},
      "manuscript_rule":"Do not report the original H3 p-value as confirmatory evidence; use this repair only as a secondary robustness boundary.",
      "causal_claim_authorized":False
    }
    Path("frog_naamp_h3_specification_repair_v0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
