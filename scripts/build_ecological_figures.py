#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"figures_ecology_v0_5"
OUT.mkdir(parents=True,exist_ok=True)

FONT="Arial,Helvetica,sans-serif"

def esc(x):
    return html.escape(str(x))

def text(x,y,s,size=18,weight="normal",anchor="start"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="font-family:{FONT};font-size:{size}px;font-weight:{weight};">{esc(s)}</text>'

def line(x1,y1,x2,y2,w=2,dash=None):
    ds=f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#111" stroke-width="{w}"{ds}/>'

def circle(x,y,r=6):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#111"/>'

def rect(x,y,w,h,rx=0,fill="white",stroke="#111",sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def svg_wrap(width,height,els):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="{int(180*height/width)}mm" viewBox="0 0 {width} {height}">\n<rect width="{width}" height="{height}" fill="white"/>\n'+"\n".join(els)+"\n</svg>\n"

def load_json(name):
    return json.loads((ROOT/name).read_text(encoding="utf-8"))

def figure1():
    d=load_json("NAAMP_ECOLOGICAL_PULSE_RECEIPT_V0_1.json")
    p=d["primary_models"]["richness_gain"]
    s=d["exact_consecutive_year_sensitivity"]["richness_gain"]
    summ=d["primary_pair_summary"]

    els=[
      text(55,48,"Figure 1. Rainfall contrast predicts active-community richness gain",28,"bold"),
      text(60,95,"A  Matched community design",23,"bold"),
      rect(65,125,300,135,16,"#f7f7f7"), rect(450,125,300,135,16,"#f7f7f7"), rect(835,125,300,135,16,"#f7f7f7"),
      text(215,165,"Same route",22,"bold","middle"), text(215,200,"same RunNumber",19,"normal","middle"), text(215,232,"adjacent observed years",18,"normal","middle"),
      text(600,165,"Orient pair",22,"bold","middle"), text(600,200,"wetter ↔ drier",20,"normal","middle"), text(600,232,"by DaysSinceRain",18,"normal","middle"),
      text(985,165,"Compare assemblages",22,"bold","middle"), text(985,200,"richness · turnover",19,"normal","middle"), text(985,232,"species identity",18,"normal","middle"),
      line(365,192,450,192,3), line(750,192,835,192,3),
      text(60,320,"B  Rainfall-contrast effect on wet − dry richness",23,"bold"),
    ]
    xmin,xmax=0.0,0.5
    x0,x1=360,1080
    def sx(v): return x0+(v-xmin)/(xmax-xmin)*(x1-x0)
    els += [line(x0,510,x1,510,2)]
    for v in [0,.1,.2,.3,.4,.5]:
        x=sx(v); els += [line(x,503,x,517,2),text(x,545,f"{v:.1f}",16,"normal","middle")]
    for yy,label,res in [(390,"All adjacent observed years",p),(455,"Exact consecutive years",s)]:
        lo,hi=res["ci95_beta"]; b=res["beta_rain_contrast"]
        els += [
          text(65,yy+6,label,20,"bold"),
          line(sx(lo),yy,sx(hi),yy,5),
          line(sx(lo),yy-8,sx(lo),yy+8,2),line(sx(hi),yy-8,sx(hi),yy+8,2),
          circle(sx(b),yy,7),
          text(1130,yy+6,f"β={b:.3f}",18,"bold","end")
        ]
    els += [
      text(720,580,"Wet − dry richness change per unit log-rain contrast",18,"normal","middle"),
      text(60,635,f"{summ['n_pairs']:,} matched pairs · {summ['n_routes']} routes · {summ['n_states']} states",19,"bold"),
      text(60,672,f"Mean richness: wet {summ['richness']['wet_mean']:.3f} · dry {summ['richness']['dry_mean']:.3f}",18),
      text(60,704,"Greater rainfall contrast → larger active-species richness gain",20,"bold")
    ]
    (OUT/"FIGURE_1_ECO_RICHNESS_V0_1.svg").write_text(svg_wrap(1200,740,els),encoding="utf-8")

def figure2():
    d=load_json("NAAMP_SPECIES_PULSE_HETEROGENEITY_RECEIPT_V0_1.json")
    rows=sorted(d["species_results"],key=lambda z:z["wet_gain_share"])
    h=1040
    top=105
    dy=28
    x0,x1=475,1040
    xmin,xmax=.25,.80
    def sx(v): return x0+(v-xmin)/(xmax-xmin)*(x1-x0)

    els=[
      text(55,48,"Figure 2. Species differ sharply in wet-versus-dry recruitment",28,"bold"),
      text(55,78,"Discordant matched pairs: wet gain share; q = Benjamini–Hochberg FDR",17),
      line(sx(.5),95,sx(.5),940,2,"6 6"),
    ]
    for v in [.3,.4,.5,.6,.7,.8]:
        x=sx(v); els += [line(x,940,x,952,2),text(x,980,f"{v:.1f}",15,"normal","middle")]
    for i,r in enumerate(rows):
        y=top+i*dy
        sp=r["species_code"]
        q=r["fdr_bh"]
        sig=q<=.05
        els += [
          text(60,y+5,sp,16,"bold" if sig else "normal"),
          line(sx(.5),y,sx(r["wet_gain_share"]),y,3 if sig else 1),
          circle(sx(r["wet_gain_share"]),y,6 if sig else 4),
          text(1145,y+5,f"{r['wet_gains']}/{r['dry_losses']}",14,"bold" if sig else "normal","end")
        ]
    els += [
      text(sx(.35),1015,"dry-associated",17,"bold","middle"),
      text(sx(.68),1015,"wet-associated",17,"bold","middle"),
      text(1145,82,"wet/dry",14,"bold","end"),
      text(60,1015,f"Species heterogeneity: χ²={d['heterogeneity_test']['chi2']:.1f}, df={d['heterogeneity_test']['df']}, P≈1.9×10⁻²¹",17,"bold")
    ]
    (OUT/"FIGURE_2_ECO_SPECIES_V0_1.svg").write_text(svg_wrap(1200,h,els),encoding="utf-8")

def figure3():
    d=load_json("NAAMP_ECOLOGICAL_PULSE_RECEIPT_V0_1.json")
    pri=d["primary_models"]
    sen=d["exact_consecutive_year_sensitivity"]
    vals=[
      ("Nestedness · primary",pri["nestedness_component"]),
      ("Nestedness · consecutive",sen["nestedness_component"]),
      ("Turnover · primary",pri["simpson_turnover"]),
      ("Turnover · consecutive",sen["simpson_turnover"]),
    ]
    els=[
      text(55,48,"Figure 3. Richness gain is not simple nested addition",28,"bold"),
      text(55,82,"Rain-contrast slopes for temporal beta-diversity components",18),
    ]
    xmin,xmax=-.02,.04
    x0,x1=400,1080
    def sx(v): return x0+(v-xmin)/(xmax-xmin)*(x1-x0)
    els += [line(sx(0),115,sx(0),480,2,"6 6"),line(x0,500,x1,500,2)]
    for v in [-.02,-.01,0,.01,.02,.03,.04]:
        x=sx(v);els += [line(x,493,x,507,2),text(x,538,f"{v:.2f}",15,"normal","middle")]
    ys=[170,245,350,425]
    for (label,res),y in zip(vals,ys):
        b=res["beta_rain_contrast"];lo,hi=res["ci95_beta"]
        els += [
          text(60,y+6,label,20,"bold" if "consecutive" in label else "normal"),
          line(sx(lo),y,sx(hi),y,5),
          line(sx(lo),y-8,sx(lo),y+8,2),line(sx(hi),y-8,sx(hi),y+8,2),
          circle(sx(b),y,7),
          text(1140,y+6,f"P={res['p_value']:.3g}",17,"bold" if res["p_value"]<.05 else "normal","end")
        ]
    els += [
      text(740,580,"Change in beta-diversity component per unit log-rain contrast",18,"normal","middle"),
      text(60,635,"Nestedness does not increase; turnover increases in exact consecutive-year pairs.",20,"bold"),
      text(60,675,"Interpretation: wetter active assemblages gain richness with compositional replacement, not only addition.",18)
    ]
    (OUT/"FIGURE_3_ECO_BETA_V0_1.svg").write_text(svg_wrap(1200,720,els),encoding="utf-8")

if __name__=="__main__":
    figure1();figure2();figure3()
    for p in sorted(OUT.glob("*.svg")):
        print(p)
