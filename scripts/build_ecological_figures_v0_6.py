#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import math
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"figures_ecology_v0_6"
OUT.mkdir(parents=True,exist_ok=True)
FONT="Arial,Helvetica,sans-serif"

def esc(x): return html.escape(str(x))
def text(x,y,s,size=18,weight="normal",anchor="start",style=""):
    extra=(";"+style) if style else ""
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="font-family:{FONT};font-size:{size}px;font-weight:{weight}{extra};">{esc(s)}</text>'
def line(x1,y1,x2,y2,w=2,dash=None):
    ds=f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#111" stroke-width="{w}"{ds}/>'
def circle(x,y,r=6,fill="#111"):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="#111" stroke-width="1"/>'
def rect(x,y,w,h,rx=0,fill="white",stroke="#111",sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def svg_wrap(width,height,els):
    hmm=int(180*height/width)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="{hmm}mm" viewBox="0 0 {width} {height}">\n<rect width="{width}" height="{height}" fill="white"/>\n'+"\n".join(els)+"\n</svg>\n"
def load(name): return json.loads((ROOT/name).read_text(encoding="utf-8"))

def figure1():
    d=load("NAAMP_ECOLOGICAL_PULSE_RECEIPT_V0_1.json")
    p=d["primary_models"]["richness_gain"]
    s=d["exact_consecutive_year_sensitivity"]["richness_gain"]
    summ=d["primary_pair_summary"]
    els=[
      text(55,48,"Figure 1. Wetter matched surveys contain richer active frog communities",27,"bold"),
      text(60,92,"A  Matched design",22,"bold"),
      rect(65,120,300,135,16,"#f7f7f7"),rect(450,120,300,135,16,"#f7f7f7"),rect(835,120,300,135,16,"#f7f7f7"),
      text(215,160,"Same route",21,"bold","middle"),text(215,195,"same RunNumber",18,"normal","middle"),text(215,226,"adjacent observed years",17,"normal","middle"),
      text(600,160,"Orient pair",21,"bold","middle"),text(600,195,"wetter ↔ drier",19,"normal","middle"),text(600,226,"by DaysSinceRain",17,"normal","middle"),
      text(985,160,"Compare assemblages",21,"bold","middle"),text(985,195,"richness · turnover",18,"normal","middle"),text(985,226,"species identity",17,"normal","middle"),
      line(365,190,450,190,3),line(750,190,835,190,3),
      text(60,315,"B  Rainfall-contrast effect on wet − dry richness",22,"bold")
    ]
    xmin,xmax=0,.5;x0,x1=360,1080
    sx=lambda v:x0+(v-xmin)/(xmax-xmin)*(x1-x0)
    els.append(line(x0,510,x1,510,2))
    for v in [0,.1,.2,.3,.4,.5]:
        x=sx(v);els += [line(x,503,x,517,2),text(x,545,f"{v:.1f}",15,"normal","middle")]
    for yy,label,res in [(390,"All adjacent observed years",p),(455,"Exact consecutive years",s)]:
        lo,hi=res["ci95_beta"];b=res["beta_rain_contrast"]
        els += [text(65,yy+6,label,19,"bold"),line(sx(lo),yy,sx(hi),yy,5),
                line(sx(lo),yy-8,sx(lo),yy+8,2),line(sx(hi),yy-8,sx(hi),yy+8,2),
                circle(sx(b),yy,7),text(1130,yy+6,f"β={b:.3f}",17,"bold","end")]
    els += [
      text(720,580,"Wet − dry richness change per unit log-rain contrast",17,"normal","middle"),
      text(60,630,f"{summ['n_pairs']:,} matched pairs · {summ['n_routes']} routes · {summ['n_states']} states",18,"bold"),
      text(60,665,f"Mean active richness: wet {summ['richness']['wet_mean']:.3f} · dry {summ['richness']['dry_mean']:.3f}",17),
      text(60,700,"Greater rainfall contrast → larger active-species richness gain",19,"bold")
    ]
    (OUT/"FIGURE_1_RICHNESS_V0_6.svg").write_text(svg_wrap(1200,735,els),encoding="utf-8")

def figure2():
    d=load("NAAMP_TEMPORAL_RAIN_SENSITIVITY_RECEIPT_V0_1.json")
    rows=d["cross_species_table"];p=d["primary_cross_species"];fam=d["family_stratified_permutation"]
    x=np.array([float(r["z_early_sensitivity"]) for r in rows])
    y=np.array([float(r["late_adjusted_wet_log_odds"]) for r in rows])
    w=np.array([1/float(r["late_se"])**2 for r in rows])
    X=np.column_stack([np.ones(len(x)),x])
    beta=np.linalg.solve(X.T@(w[:,None]*X),X.T@(w*y))
    if not math.isclose(float(beta[1]),float(p["beta_per_1sd_early_sensitivity"]),rel_tol=0,abs_tol=1e-10):
        raise SystemExit(f"Figure-2 slope mismatch: {beta[1]} vs {p['beta_per_1sd_early_sensitivity']}")
    xmin,xmax=-2.2,2.8;ymin,ymax=-1.1,1.55
    left,right,top,bottom=120,1110,120,650
    sx=lambda v:left+(v-xmin)/(xmax-xmin)*(right-left)
    sy=lambda v:bottom-(v-ymin)/(ymax-ymin)*(bottom-top)
    els=[
      text(55,48,"Figure 2. Earlier species rain sensitivity predicts later community recruitment",27,"bold"),
      text(55,82,"2001–2007 sensitivity → independent 2008–2015 wet-versus-dry response",17),
      line(sx(0),top,sx(0),bottom,2,"5 6"),line(left,sy(0),right,sy(0),2,"5 6"),
      line(left,bottom,right,bottom,2),line(left,top,left,bottom,2)
    ]
    for xv in [-2,-1,0,1,2]:
        els += [line(sx(xv),bottom,sx(xv),bottom+10,2),text(sx(xv),bottom+34,str(xv),14,"normal","middle")]
    for yv in [-1,-.5,0,.5,1,1.5]:
        els += [line(left-10,sy(yv),left,sy(yv),2),text(left-18,sy(yv)+5,f"{yv:.1f}",14,"normal","end")]
    xx=np.array([xmin,xmax]);yy=beta[0]+beta[1]*xx
    els.append(line(sx(xx[0]),sy(yy[0]),sx(xx[1]),sy(yy[1]),4))
    annotate={"Gastrophryne carolinensis","Hyla squirella","Hyla femoralis","Lithobates catesbeianus","Lithobates palustris"}
    for r in rows:
        px,py=sx(float(r["z_early_sensitivity"])),sy(float(r["late_adjusted_wet_log_odds"]))
        els.append(circle(px,py,5))
        if r["species"] in annotate:
            dx=8;dy=-8
            if r["species"].startswith("Lithobates"): dy=18
            els.append(text(px+dx,py+dy,r["species"],12,"bold"))
    els += [
      text((left+right)/2,710,"Early rain-pulse sensitivity (SD units; 2001–2007)",17,"normal","middle"),
      text(28,(top+bottom)/2,"Later wet-recruitment log odds (2008–2015)",16,"normal","middle","writing-mode:tb;glyph-orientation-vertical:0"),
      rect(680,110,430,120,12,"#f7f7f7"),
      text(700,142,f"β = {p['beta_per_1sd_early_sensitivity']:.3f} per SD",18,"bold"),
      text(700,172,f"95% CI {p['ci95_beta'][0]:.3f}–{p['ci95_beta'][1]:.3f} · P={p['p_value']:.2g}",16),
      text(700,201,f"Spearman ρ={p['spearman_rho']:.3f} · family-permutation P+={fam['positive_tail_p']:.3f}",15),
      text(60,755,"27 species estimable in both non-overlapping periods",17,"bold")
    ]
    (OUT/"FIGURE_2_TEMPORAL_PREDICTION_V0_6.svg").write_text(svg_wrap(1200,790,els),encoding="utf-8")

def figure3():
    d=load("NAAMP_ECOLOGICAL_PULSE_RECEIPT_V0_1.json")
    s=load("NAAMP_SPECIES_PULSE_ADJUSTED_ROBUSTNESS_SUMMARY_V0_1.json")
    pri=d["primary_models"];sen=d["exact_consecutive_year_sensitivity"]
    vals=[
      ("Nestedness · primary",pri["nestedness_component"]),
      ("Nestedness · consecutive",sen["nestedness_component"]),
      ("Turnover · primary",pri["simpson_turnover"]),
      ("Turnover · consecutive",sen["simpson_turnover"]),
    ]
    els=[
      text(55,48,"Figure 3. Rainfall-associated richness gain includes compositional replacement",27,"bold"),
      text(55,82,"A  Rain-contrast slopes for temporal beta-diversity components",20,"bold")
    ]
    xmin,xmax=-.02,.04;x0,x1=400,1080
    sx=lambda v:x0+(v-xmin)/(xmax-xmin)*(x1-x0)
    els += [line(sx(0),115,sx(0),465,2,"6 6"),line(x0,485,x1,485,2)]
    for v in [-.02,-.01,0,.01,.02,.03,.04]:
        x=sx(v);els += [line(x,478,x,492,2),text(x,522,f"{v:.2f}",14,"normal","middle")]
    ys=[150,220,325,395]
    for (label,res),y in zip(vals,ys):
        b=res["beta_rain_contrast"];lo,hi=res["ci95_beta"]
        els += [text(60,y+6,label,18,"bold" if "consecutive" in label else "normal"),
                line(sx(lo),y,sx(hi),y,5),line(sx(lo),y-7,sx(lo),y+7,2),line(sx(hi),y-7,sx(hi),y+7,2),
                circle(sx(b),y,7),text(1140,y+5,f"P={res['p_value']:.3g}",16,"bold" if res["p_value"]<.05 else "normal","end")]
    het=s["heterogeneity"];con=s["raw_adjusted_concordance"]
    els += [
      text(55,585,"B  Species response remains heterogeneous",20,"bold"),
      rect(60,610,1080,115,12,"#f7f7f7"),
      text(90,650,f"29 adjusted species responses: Q={het['Q']:.1f}, df={het['df']}, P=1.46×10⁻¹⁷",18,"bold"),
      text(90,684,f"Raw vs adjusted species ranking: Spearman ρ={con['spearman_rho']:.3f}",17),
      text(650,684,"Exact consecutive-year turnover increases with rain contrast",17,"bold"),
    ]
    (OUT/"FIGURE_3_TURNOVER_V0_6.svg").write_text(svg_wrap(1200,760,els),encoding="utf-8")

if __name__=="__main__":
    figure1();figure2();figure3()
    for p in sorted(OUT.glob("*.svg")): print(p)
