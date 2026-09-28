#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"figures_ecology_v0_6"
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
    matched=load_json("NAAMP_ECOLOGICAL_PULSE_RECEIPT_V0_1.json")
    ts=load_json("NAAMP_RAINFALL_PULSE_TIMESCALE_SUMMARY_V0_1.json")
    p=matched["primary_models"]["richness_gain"]
    s=matched["exact_consecutive_year_sensitivity"]["richness_gain"]
    summ=matched["primary_pair_summary"]
    curve=ts["run_level_richness_curve"]["effects_vs_days8plus"]

    els=[
      text(55,48,"Figure 1. Active-community richness remains elevated for several days after rain",28,"bold"),
      text(60,92,"A  Matched wet–dry community contrast",22,"bold"),
      text(60,125,f"{summ['n_pairs']:,} pairs · {summ['n_routes']} routes · {summ['n_states']} states",17),
    ]

    xmin,xmax=0.0,0.5
    x0,x1=365,1080
    def sx(v): return x0+(v-xmin)/(xmax-xmin)*(x1-x0)
    els += [line(x0,285,x1,285,2)]
    for v in [0,.1,.2,.3,.4,.5]:
        x=sx(v); els += [line(x,278,x,292,2),text(x,320,f"{v:.1f}",15,"normal","middle")]
    for yy,label,res in [(180,"All adjacent observed years",p),(240,"Exact consecutive years",s)]:
        lo,hi=res["ci95_beta"]; b=res["beta_rain_contrast"]
        els += [
          text(65,yy+6,label,18,"bold" if "Exact" in label else "normal"),
          line(sx(lo),yy,sx(hi),yy,5),
          line(sx(lo),yy-8,sx(lo),yy+8,2),line(sx(hi),yy-8,sx(hi),yy+8,2),
          circle(sx(b),yy,7),
          text(1140,yy+6,f"β={b:.3f}",17,"bold","end")
        ]
    els += [text(720,352,"Wet − dry richness gain per unit log-rain contrast",17,"normal","middle")]

    els += [text(60,410,"B  Prespecified rain-recency curve",22,"bold"),
            text(60,440,"Adjusted richness difference relative to ≥8 days since rain",17)]
    labels=["day0","day1","days2_3","days4_7"]
    display={"day0":"Day 0","day1":"Day 1","days2_3":"Days 2–3","days4_7":"Days 4–7"}
    ymin,ymax=0.0,.95
    py0,py1=700,475
    px=[250,480,710,940]
    def sy(v): return py0-(v-ymin)/(ymax-ymin)*(py0-py1)
    els += [line(150,py0,1080,py0,2)]
    for v in [0,.2,.4,.6,.8]:
        y=sy(v); els += [line(143,y,157,y,2),text(130,y+5,f"{v:.1f}",14,"normal","end"),line(150,y,1080,y,1,"3 7")]
    prev=None
    for x,b in zip(px,labels):
        e=curve[b]; est=e["difference_species"]; lo,hi=e["ci95"]
        y=sy(est)
        if prev is not None: els.append(line(prev[0],prev[1],x,y,3))
        els += [line(x,sy(lo),x,sy(hi),4),line(x-8,sy(lo),x+8,sy(lo),2),line(x-8,sy(hi),x+8,sy(hi),2),circle(x,y,8),
                text(x,735,display[b],16,"bold","middle")]
        prev=(x,y)
    els += [
      text(60,785,"Difference in active species richness",17,"normal"),
      text(60,825,"Prespecified pulse endpoint: 4–7 days",20,"bold"),
      text(60,858,"All recent-rain bins remain above the ≥8-day reference; the stricter matched sensitivity is clear through days 2–3.",16)
    ]
    (OUT/"FIGURE_1_ECO_TIMESCALE_V0_1.svg").write_text(svg_wrap(1200,900,els),encoding="utf-8")

def figure2():
    d=load_json("NAAMP_SPECIES_PULSE_ADJUSTED_ROBUSTNESS_SUMMARY_V0_1.json")
    rows=[]
    for x in d["fdr_5_percent"]["negative_species"]:
        rows.append({**x,"direction":"dry-associated"})
    for x in d["fdr_5_percent"]["positive_species"]:
        rows.append({**x,"direction":"wet-associated"})
    rows=sorted(rows,key=lambda z:z["adjusted_wet_probability"])

    h=560
    x0,x1=430,1050
    xmin,xmax=.30,.82
    def sx(v): return x0+(v-xmin)/(xmax-xmin)*(x1-x0)

    els=[
      text(55,48,"Figure 2. Species-selective wet-versus-dry responses persist after adjustment",28,"bold"),
      text(55,80,"FDR-supported species; adjusted wet probability among discordant matched pairs",17),
      line(sx(.5),110,sx(.5),400,2,"6 6"),
    ]
    for v in [.3,.4,.5,.6,.7,.8]:
        x=sx(v); els += [line(x,400,x,412,2),text(x,442,f"{v:.1f}",15,"normal","middle")]

    ys=[135+i*38 for i in range(len(rows))]
    for r,y in zip(rows,ys):
        p=r["adjusted_wet_probability"]
        els += [
          text(60,y+5,r["species"],17,"bold"),
          line(sx(.5),y,sx(p),y,4),
          circle(sx(p),y,7),
          text(1140,y+5,f"q={r['fdr_bh']:.3g}",15,"bold","end")
        ]

    het=d["heterogeneity"]
    con=d["raw_adjusted_concordance"]
    els += [
      text(60,480,f"All 29 species: Q={het['Q']:.1f}, df={het['df']}, P≈1.46×10⁻¹⁷",18,"bold"),
      text(60,512,f"Raw vs adjusted species ranking: Spearman ρ={con['spearman_rho']:.3f}",17),
      text(60,542,"52.1% of family-matched heterogeneity remains within families (P=8.28×10⁻⁸)",16,"bold"),
      text(780,520,"0.5 = no wet/dry bias",16,"normal","middle")
    ]
    (OUT/"FIGURE_2_ECO_SPECIES_V0_2.svg").write_text(svg_wrap(1200,590,els),encoding="utf-8")

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
    (OUT/"FIGURE_3_ECO_BETA_V0_2.svg").write_text(svg_wrap(1200,720,els),encoding="utf-8")

if __name__=="__main__":
    figure1();figure2();figure3()
    for p in sorted(OUT.glob("*.svg")):
        print(p)
