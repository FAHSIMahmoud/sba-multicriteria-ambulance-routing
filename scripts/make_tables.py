"""LaTeX rows of Tables 2-5 of the paper."""
import pathlib, os
ROOT = pathlib.Path(__file__).resolve().parent.parent
import pandas as pd, numpy as np, json
R=str(ROOT/"results/tables")+"/"; O=str(ROOT/"results/latex_rows")+"/"; import os; os.makedirs(O,exist_ok=True)
f2=lambda x: "--" if pd.isna(x) else (f"{x:.2f}" if x<100 else f"{x:.1f}")
names={"T-B":"T--B","T-I":"T--I","T-B-I":"T--B--I","T-B-S-St":"T--B--S--St","T-B-S-St-U":"T--B--S--St--U"}
# Table 3: C/C++ end-to-end
T=pd.read_csv(R+"T2_performance_OSM.csv"); C=T[T.lang=="C/C++"]
rows=[f"{names[r.set]} & {r.d} & {r.alg.replace('*','$^{*}$')} & {r['solved_%']:.0f} & {f2(r.ms_median)} & {f2(r.ms_p95)} & {f2(r.ms_max)} & {r.expanded_median:.1f} & {r.front_mean:.2f} \\\\ \\hline" for _,r in C.iterrows()]
open(O+"tab_c.tex","w").write("\n".join(rows))
# Table 4: Python end-to-end (Colab) + search-only (local)
S=pd.read_csv(ROOT/"results/raw/split_local.csv"); S["alg2"]=S.alg.str.replace(" (C++)","",regex=False)
P=T[(T.lang=="Python")&(~T.alg.str.contains("non-exact"))&(T.set.isin(["T-B","T-B-I","T-B-S-St"]))]
rows=[]
for _,r in P.iterrows():
    s=S[(S.set==r.set)&(S.alg==r.alg)].search_ms
    rows.append(f"{names[r.set]} & {r.d} & {r.alg.replace(' (py)','').replace('*','$^{*}$')} & {f2(r.ms_median)} & {f2(r.ms_p95)} & {f2(s.median())} & {f2(s.quantile(.95))} \\\\ \\hline")
    if r.alg=="Martins (py)":
        e=S[(S.set==r.set)&(S.alg=="EMOA* (C++)")]
        rows.append(f"{names[r.set]} & {r.d} & EMOA$^{{*}}$ (C++, local) & -- & -- & {f2(e.search_ms.median())} & {f2(e.search_ms.quantile(.95))} \\\\ \\hline")
open(O+"tab_py.tex","w").write("\n".join(rows))
# Table 5: Pareto set statistics + weighted-sum coverage
F=pd.read_csv(ROOT/"results/raw/front_summary.csv").set_index("set"); W=pd.read_csv(R+"T4_weighted_sum_coverage.csv").set_index("set")
rows=[]
for st in ["T-B","T-I","T-B-I","T-B-S-St","T-B-S-St-U"]:
    f=F.loc[st]; w=W.loc[st]
    rows.append(f"{names[st]} & {int(f.d)} & {f.multi_pct:.1f} & {f.front_mean:.2f} & {int(f.front_max)} & {f.dT_minother_mean:.2f} & {f.dT_minother_max:.1f} & {w.coverage_mean_pct:.1f} & {w.share_full_coverage_pct:.0f} \\\\ \\hline")
open(O+"tab_front.tex","w").write("\n".join(rows))
# Table 6: closures + contraflow (C/C++ medians, front) 
T5=pd.read_csv(R+"T5_performance_closures.csv"); T6=pd.read_csv(R+"T6_performance_contraflow.csv")
rows=[]
for D in [T[(T.lang=="C/C++")&(T.set.isin(["T-B","T-B-I","T-B-S-St"]))], T5[T5.lang=="C/C++"], T6[T6.lang=="C/C++"]]:
    for _,r in D.iterrows():
        sc={"OSM":"Base network"}.get(r.scenario,r.scenario.replace("closed","Closed").replace("%","\\%").replace("contraflow","Contraflow"))
        rows.append(f"{sc} & {names.get(r.set,r.set.replace('-','--'))} & {r.alg.replace('*','$^{*}$')} & {r.queries:.0f} & {r['solved_%']:.0f} & {f2(r.ms_median)} & {f2(r.ms_p95)} & {r.front_mean:.2f} & {int(r.front_max)} \\\\ \\hline")
open(O+"tab_scen.tex","w").write("\n".join(rows))
b=pd.read_csv(R+"T5b_closure_delay.csv"); c=pd.read_csv(R+"T6b_contraflow_saving.csv")
print(b.round(2).to_string()); print(c.round(2).to_string())
print(open(O+"tab_scen.tex").read()[:600])
