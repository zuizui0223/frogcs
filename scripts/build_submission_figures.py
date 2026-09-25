#!/usr/bin/env python3
from __future__ import annotations
import json, math
from pathlib import Path
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT
OUT=BASE/"figures"
OUT.mkdir(parents=True,exist_ok=True)

def read(name):
    return json.loads((BASE/name).read_text(encoding="utf-8"))

def text(x,y,s,size=26,weight="normal",anchor="start",italic=False):
    style=f"font-family:Arial,Helvetica,sans-serif;font-size:{size}px;font-weight:{weight};"
    if italic: style+="font-style:italic;"
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="{style}">{escape(str(s))}</text>'

def line(x1,y1,x2,y2,w=2,dash=None):
    extra=f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#111" stroke-width="{w}"{extra}/>'

def rect(x,y,w,h,rx=18,fill="#fff",stroke="#111",sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def circle(cx,cy,r,fill="#111"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'

def fig1():
    el=[]
    el.append('<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="108mm" viewBox="0 0 1200 720">')
    el.append('<rect width="1200" height="720" fill="white"/>')
    el.append(text(60,55,"Figure 1. Independent acoustic systems replicate the raw multispecies-calling association",30,"bold"))

    # NAAMP
    el.append(rect(55,100,500,235,24,"#f7f7f7"))
    el.append(text(80,140,"NAAMP — North America",28,"bold"))
    el.append(text(80,178,"Standardized 5-min route stops",22))
    el.append(text(80,210,"9,399 runs · 900 routes · 93,383 stops",20))
    el.append(rect(90,235,185,62,14,"#fff"))
    el.append(text(182,273,"recent rainfall",21,"bold","middle"))
    el.append(text(305,273,"→",34,"bold","middle"))
    el.append(rect(335,235,185,62,14,"#fff"))
    el.append(text(427,263,"≥2 calling species",19,"bold","middle"))
    el.append(text(427,286,"at a stop",18,"normal","middle"))

    # FrogID
    el.append(rect(645,100,500,235,24,"#f7f7f7"))
    el.append(text(670,140,"FrogID — Australia",28,"bold"))
    el.append(text(670,178,"Expert-validated short recordings",22))
    el.append(text(670,210,"40,754 recordings · 13,148 recorders",20))
    el.append(rect(680,235,185,62,14,"#fff"))
    el.append(text(772,273,"recent rainfall",21,"bold","middle"))
    el.append(text(895,273,"→",34,"bold","middle"))
    el.append(rect(925,225,185,82,14,"#fff"))
    el.append(text(1018,252,"1 vs ≥2 calling",18,"bold","middle"))
    el.append(text(1018,276,"species, conditional",17,"normal","middle"))
    el.append(text(1018,298,"on ≥1 already calling",17,"normal","middle"))

    # convergence
    el.append(line(305,335,305,405,3))
    el.append(line(895,335,895,405,3))
    el.append(line(305,405,600,455,3))
    el.append(line(895,405,600,455,3))
    el.append(rect(305,445,590,108,20,"#efefef",sw=3))
    el.append(text(600,482,"Cross-system directional claim",25,"bold","middle"))
    el.append(text(600,516,"More recent rainfall ↔ more short-window multispecies calling",21,"normal","middle"))
    el.append(text(600,542,"No pooling of effect sizes",18,"normal","middle"))

    # robustness
    el.append(rect(120,585,390,70,16,"#fff"))
    el.append(text(315,614,"NAAMP robustness",20,"bold","middle"))
    el.append(text(315,642,"within the same route",19,"normal","middle"))
    el.append(rect(690,585,390,70,16,"#fff"))
    el.append(text(885,614,"FrogID robustness",20,"bold","middle"))
    el.append(text(885,642,"within the same ERA5 cell",19,"normal","middle"))
    el.append(line(510,620,690,620,2,"8 8"))
    el.append(text(600,697,"Raw event-level association; mechanism is decomposed separately in NAAMP",17,"normal","middle"))
    el.append('</svg>')
    return "\n".join(el)+"\n"

def mapx(v,lo,hi,x0,x1):
    return x0+(v-lo)/(hi-lo)*(x1-x0)

def fig2():
    naamp=read("NAAMP_PRIMARY_RECEIPT_V0_1.json")["primary"]
    frog=read("FROGID_VALIDATION_RECEIPT_V0_2.json")["primary"]
    rob=read("SPATIAL_CONFOUNDING_ROBUSTNESS_RECEIPT_V0_1.json")["artifacts"]
    el=[]
    el.append('<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="115mm" viewBox="0 0 1200 770">')
    el.append('<rect width="1200" height="770" fill="white"/>')
    el.append(text(60,52,"Figure 2. Rain-recency associations replicate and persist within spatial units",30,"bold"))

    # Panel A
    el.append(text(65,105,"A  Primary logistic associations",25,"bold"))
    x0,x1=360,1080; lo,hi=0.75,1.05
    yaxis=280
    el.append(line(x0,yaxis,x1,yaxis,2))
    for tick in [0.75,0.8,0.85,0.9,0.95,1.0,1.05]:
        x=mapx(tick,lo,hi,x0,x1)
        el.append(line(x,yaxis-7,x,yaxis+7,2))
        el.append(text(x,yaxis+34,f"{tick:.2f}",17,"normal","middle"))
    xn=mapx(1.0,lo,hi,x0,x1); el.append(line(xn,135,xn,270,2,"7 7"))
    rows=[
      ("NAAMP",naamp["odds_ratio_per_sd_log1p_days_since_rain"],naamp["ci95_or"][0],naamp["ci95_or"][1],165,"programme days since rain"),
      ("FrogID",frog["odds_ratio_per_sd_log1p_dry_days"],frog["ci95_or"][0],frog["ci95_or"][1],225,"ERA5 antecedent dry days"),
    ]
    for label,v,l,h,y,sub in rows:
        el.append(text(70,y+6,label,22,"bold"))
        el.append(text(165,y+6,sub,17))
        xl,xv,xh=mapx(l,lo,hi,x0,x1),mapx(v,lo,hi,x0,x1),mapx(h,lo,hi,x0,x1)
        el.append(line(xl,y,xh,y,5)); el.append(line(xl,y-9,xl,y+9,3)); el.append(line(xh,y-9,xh,y+9,3)); el.append(circle(xv,y,8))
        el.append(text(1090,y+6,f"{v:.3f}",18,"bold","end"))
    el.append(text(720,340,"Odds ratio per 1 SD increase in dryness",18,"normal","middle"))
    el.append(text(720,365,"Different exposure metrics; no pooled effect",16,"normal","middle"))

    # Panel B
    el.append(text(65,425,"B  Within-spatial-unit diagnostics",25,"bold"))
    x0,x1=360,1080; lo,hi=-0.06,0.02; yaxis=640
    el.append(line(x0,yaxis,x1,yaxis,2))
    for tick in [-0.06,-0.04,-0.02,0.0,0.02]:
        x=mapx(tick,lo,hi,x0,x1)
        el.append(line(x,yaxis-7,x,yaxis+7,2))
        el.append(text(x,yaxis+34,f"{tick:.2f}",17,"normal","middle"))
    xz=mapx(0.0,lo,hi,x0,x1); el.append(line(xz,455,xz,630,2,"7 7"))
    rows2=[
      ("NAAMP within route",rob["NAAMP"]["beta_rain_within_probability_scale"],rob["NAAMP"]["ci95_beta"][0],rob["NAAMP"]["ci95_beta"][1],505),
      ("FrogID within ERA5 cell",rob["FrogID"]["beta_dry_within_probability_scale"],rob["FrogID"]["ci95_beta"][0],rob["FrogID"]["ci95_beta"][1],570),
    ]
    for label,v,l,h,y in rows2:
        el.append(text(70,y+6,label,20,"bold"))
        xl,xv,xh=mapx(l,lo,hi,x0,x1),mapx(v,lo,hi,x0,x1),mapx(h,lo,hi,x0,x1)
        el.append(line(xl,y,xh,y,5)); el.append(line(xl,y-9,xl,y+9,3)); el.append(line(xh,y-9,xh,y+9,3)); el.append(circle(xv,y,8))
        el.append(text(1090,y+6,f"{v:.4f}",18,"bold","end"))
    el.append(text(720,700,"Within-unit probability-scale coefficient",18,"normal","middle"))
    el.append(text(600,748,"Both diagnostics negative with 95% CI excluding 0 · association, not causation",17,"normal","middle"))
    el.append('</svg>')
    return "\n".join(el)+"\n"


def fig3():
    mech=read("NAAMP_MECHANISM_DECOMPOSITION_RECEIPT_V0_1.json")
    rep=read("NAAMP_REVIEW_REPAIR_RECEIPT_V0_1.json")
    net=read("NAAMP_NETWORK_RECEIPT_V0_1.json")

    act=mech["activation"]["rain_z"]
    cond=mech["conditional_multispecies_given_active"]["rain_z"]
    pool=rep["active_pool_richness"]
    ind=rep["independence_residual"]
    cov=rep["pair_covariance_sensitivity"]
    nw=net["primary"]

    el=[]
    el.append('<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="118mm" viewBox="0 0 1200 790">')
    el.append('<rect width="1200" height="790" fill="white"/>')
    el.append(text(60,55,"Figure 3. Rain expands acoustic participation without stronger residual co-calling",30,"bold"))

    # cue
    el.append(rect(430,95,340,82,20,"#f7f7f7",sw=3))
    el.append(text(600,130,"More recent rainfall",28,"bold","middle"))
    el.append(text(600,158,"lower dryness exposure",18,"normal","middle"))

    # left activation branch
    el.append(line(520,177,335,245,3))
    el.append(rect(70,235,500,405,24,"#f7f7f7",sw=3))
    el.append(text(320,278,"Community participation",27,"bold","middle"))
    el.append(text(320,315,"Any calling at a stop",21,"bold","middle"))
    el.append(text(320,346,f"OR dryness = {act['odds_ratio']:.3f}",20,"normal","middle"))
    el.append(text(320,374,f"P = {act['p_value']:.2e}",19,"normal","middle"))
    el.append(line(150,405,490,405,2,"7 7"))
    el.append(text(320,447,"Run-level active species pool",21,"bold","middle"))
    el.append(text(320,478,f"β dryness = {pool['beta_rain_z']:.4f}",20,"normal","middle"))
    el.append(text(320,506,f"95% CI {pool['ci95_beta'][0]:.4f} to {pool['ci95_beta'][1]:.4f}",18,"normal","middle"))
    el.append(text(320,534,f"P = {pool['p_value']:.2e}",19,"normal","middle"))
    el.append(text(320,595,"Supported: recent rain broadens",20,"bold","middle"))
    el.append(text(320,622,"the acoustically active community",20,"bold","middle"))

    # right residual-association branch
    el.append(line(680,177,865,245,3))
    el.append(rect(630,235,500,405,24,"#fff",sw=3))
    el.append(text(880,278,"Residual association",27,"bold","middle"))
    el.append(text(880,315,"P(≥2 species | ≥1 active)",20,"bold","middle"))
    el.append(text(880,345,f"OR dryness = {cond['odds_ratio']:.3f} · P = {cond['p_value']:.3f}",18,"normal","middle"))
    el.append(text(880,390,"Observed − independence expectation",20,"bold","middle"))
    el.append(text(880,420,f"β = {ind['beta_rain_z']:.5f} · P = {ind['p_value']:.3f}",18,"normal","middle"))
    el.append(text(880,465,"Mean pairwise excess covariance",20,"bold","middle"))
    el.append(text(880,495,f"β = {cov['beta_rain_z']:.5f} · P = {cov['p_value']:.3f}",18,"normal","middle"))
    el.append(text(880,540,"Pairwise network density",20,"bold","middle"))
    el.append(text(880,570,f"OR dryness = {nw['odds_ratio']:.3f} · P = {nw['p_value']:.3f}",18,"normal","middle"))
    el.append(text(880,612,"No detectable rain-related strengthening",19,"bold","middle"))

    el.append(rect(220,685,760,66,18,"#efefef",sw=2))
    el.append(text(600,715,"Interpretation: activation-dominated multispecies signal",23,"bold","middle"))
    el.append(text(600,740,"not evidence by itself for temporal-niche compression or facilitation",18,"normal","middle"))
    el.append('</svg>')
    return "\n".join(el)+"\n"

(OUT/"FIGURE_1_DESIGN_V0_1.svg").write_text(fig1(),encoding="utf-8")
(OUT/"FIGURE_2_EFFECTS_V0_1.svg").write_text(fig2(),encoding="utf-8")
(OUT/"FIGURE_3_DECOMPOSITION_V0_1.svg").write_text(fig3(),encoding="utf-8")
print(OUT/"FIGURE_1_DESIGN_V0_1.svg")
print(OUT/"FIGURE_2_EFFECTS_V0_1.svg")
print(OUT/"FIGURE_3_DECOMPOSITION_V0_1.svg")
