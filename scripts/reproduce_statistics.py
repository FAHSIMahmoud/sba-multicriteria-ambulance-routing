"""Pareto-front statistics and heuristic/search time split (Tables 2 and 4).
Usage: EMOA_BIN=/path/to/run_emoa python scripts/reproduce_statistics.py"""
import pathlib, os
ROOT = pathlib.Path(__file__).resolve().parent.parent
import nbformat, json, math, random, time, heapq, itertools, re, subprocess, numpy as np, pandas as pd
nb=nbformat.read(str(ROOT/"notebook/FEDZ_TrackB_v3_multicriteria_benchmark.ipynb"),4)
g={}
exec(nb.cells[2].source, g)                        # config
g["OUT"]=str(ROOT/"results/_work"); import os; os.makedirs(g["OUT"]+"/graphs",exist_ok=True)
exec("import os, sys, json, math, time, random, heapq, itertools, re, subprocess\nimport numpy as np, pandas as pd", g)
exec(nb.cells[11].source.split("BASE_T = Inst")[0], g)   # Inst, rev_dijkstra
exec(nb.cells[13].source, g)                       # algorithms
R=str(ROOT/"results"); os.makedirs(ROOT/"results/reproduced",exist_ok=True)
ARCS=pd.read_csv(str(ROOT/"data/arcs_criteria.csv")); meta=json.load(open(R+"/run_metadata.json"))
Inst=g["Inst"]; rev=g["rev_dijkstra"]
BASE=Inst(ARCS,["time"],"t"); HOSP=sorted({BASE.id[int(h["node"])] for h in meta["hospitals"]})
DT={h:rev(BASE,h,0) for h in HOSP}
rng=random.Random(2026); cand=[i for i in range(len(BASE.id)) if i not in HOSP]; ORIG=rng.sample(cand,200)
inv={i:n for n,i in BASE.id.items()}
Q=[(inv[s],inv[min(HOSP,key=lambda h:DT[h][s])]) for s in ORIG if min(DT[h][s] for h in HOSP)<math.inf]
raw=pd.read_csv(R+"/raw/bench_OSM.csv")
rows=[]; split=[]
for sname,crit in g["OBJECTIVE_SETS"].items():
    I=Inst(ARCS,crit,sname); H={}
    em=raw[(raw.set==sname)&(raw.alg=="EMOA*")].set_index("q").n_sol
    for qi,(a,b) in enumerate(Q):
        s,t=I.id[a],I.id[b]
        if t not in H: H[t]=[rev(I,t,j) for j in range(I.d)]
        F,_=g["martins_py"](I,s,t,time.perf_counter()+120)
        F=sorted(F); T0=min(f[0] for f in F)
        rec=dict(set=sname,d=I.d,q=qi,front=len(F),emoa_n=int(em.get(qi,-1)),T0_s=T0*0.1,
                 dT_max_pct=100*(max(f[0] for f in F)/T0-1))
        # criteria of fastest (lexicographic) and of the route with min sum of non-time criteria
        fast=min(F); best=min(F,key=lambda f:(sum(f[1:]),f[0]))
        rec.update(fast_other=sum(fast[1:]),min_other=sum(best[1:]),dT_minother_pct=100*(best[0]/T0-1))
        rows.append(rec)
D=pd.DataFrame(rows); D.to_csv(ROOT/"results/reproduced/front_stats.csv",index=False)
print("reproduction check (front size == EMOA* n_sol in Colab run):",(D.front==D.emoa_n).mean())
S=D.groupby("set",sort=False).agg(d=("d","first"),multi_pct=("front",lambda x:100*(x>1).mean()),front_mean=("front","mean"),front_max=("front","max"),
  T0_median_s=("T0_s","median"),fast_has_other_pct=("fast_other",lambda x:100*(x>0).mean()),
  dT_minother_mean=("dT_minother_pct","mean"),dT_minother_max=("dT_minother_pct","max"))
print(S.round(2).to_string()); S.to_csv(ROOT/"results/reproduced/front_summary.csv")

# ---------- split: heuristic initialisation vs search (local machine) ----------
EXE=os.environ.get("EMOA_BIN","bin_src/public_emoa/build/run_emoa"); cpu=subprocess.run("lscpu | grep 'Model name'",shell=True,capture_output=True,text=True).stdout.split(":")[1].strip()
hc={}
def heur_cached(I,t):
    k=(I.tag,t)
    if k not in hc: hc[k]=[rev(I,t,j) for j in range(I.d)]
    return hc[k]
recs=[]
for sname,crit in g["OBJECTIVE_SETS"].items():
    I=Inst(ARCS,crit,sname); fs=I.write()
    for qi,(a,b) in enumerate(Q):
        s,t=I.id[a],I.id[b]
        res=g["OUT"]+"/graphs/_r.txt"
        subprocess.run([EXE,str(s+1),str(t+1),"60",str(I.d),*fs[:I.d],res],capture_output=True)
        kv=dict(l.split(":",1) for l in open(res).read().splitlines() if ":" in l and not l.startswith("Label"))
        recs.append(dict(set=sname,alg="EMOA* (C++)",heur_ms=1000*float(kv["rt_initHeu"]),search_ms=1000*float(kv["rt_search"])))
    g["heur"]=lambda I_,t_: heur_cached(I_,t_)
    for alg in ["BOA* (py)","NAMOA*dr (py)","LTMOA* (py)","Martins (py)"]:
        fn,dreq=g["PY_ALGOS"][alg]
        if dreq and I.d!=dreq: continue
        for qi,(a,b) in enumerate(Q[:100]):
            s,t=I.id[a],I.id[b]
            x=time.perf_counter(); heur_cached(I,t); hms=1000*(time.perf_counter()-x)
            x=time.perf_counter(); fn(I,s,t,time.perf_counter()+60); sms=1000*(time.perf_counter()-x)
            recs.append(dict(set=sname,alg=alg,heur_ms=np.nan if alg.startswith("Martins") else hms,search_ms=sms))
P=pd.DataFrame(recs); P.to_csv(ROOT/"results/reproduced/split_local.csv",index=False)
T=P.groupby(["set","alg"],sort=False).agg(n=("search_ms","size"),search_median_ms=("search_ms","median"),search_p95_ms=("search_ms",lambda x:x.quantile(.95)))
print("CPU:",cpu); print(T.round(3).to_string())
E=P[P.alg.str.startswith("EMOA")].groupby("set",sort=False)[["heur_ms","search_ms"]].median(); print(E.round(3))
json.dump({"cpu":cpu},open(ROOT/"results/reproduced/split_meta.json","w"))
