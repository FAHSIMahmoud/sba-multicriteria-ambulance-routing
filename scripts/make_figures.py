"""Figures 1 and 2 of the paper (Figure 3 of earlier drafts is also written as fig2_runtime.pdf)."""
import pathlib, os
ROOT = pathlib.Path(__file__).resolve().parent.parent
import osmnx as ox, pandas as pd, numpy as np, matplotlib, json
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"serif","font.serif":["Liberation Serif"],"font.size":9,"pdf.fonttype":42,"axes.spines.top":False,"axes.spines.right":False,"axes.linewidth":0.6,"lines.linewidth":1.0})
R=str(ROOT/"results"); O=str(ROOT/"results/paper_figures")+"/"
G=ox.load_graphml(str(ROOT/"data/sba_drive_network_v3.graphml")); meta=json.load(open(R+"/run_metadata.json"))
VT=set(meta["config"]["VERTICAL_TYPES"])
def pts(cond): return [(d["x"],d["y"]) for n,d in G.nodes(data=True) if cond(d)]
sig=pts(lambda d:str(d.get("highway"))=="traffic_signals"); stp=pts(lambda d:str(d.get("highway")) in("stop","give_way"))
bmp=pts(lambda d:str(d.get("traffic_calming")) in VT); hosp=[(G.nodes[int(h["node"])]["x"],G.nodes[int(h["node"])]["y"]) for h in meta["hospitals"]]
print(len(sig),len(stp),len(bmp))
fig,ax=ox.plot_graph(G,node_size=0,edge_color="#c8c8c8",edge_linewidth=0.5,bgcolor="w",show=False,close=False,figsize=(6.0,6.0))
ax.scatter(*zip(*sig),s=16,c="#1f5aa6",marker="o",label=f"Traffic signals ({len(sig)})",zorder=5,linewidths=0)
ax.scatter(*zip(*stp),s=16,c="#c0392b",marker="s",label=f"Stop / give-way signs ({len(stp)})",zorder=5,linewidths=0)
ax.scatter(*zip(*bmp),s=22,c="k",marker="^",label=f"Speed bumps ({len(bmp)})",zorder=6,linewidths=0)
ax.scatter(*zip(*hosp),s=110,c="#7d3c98",marker="P",label="Emergency hospitals (CHU, EPH)",zorder=7,linewidths=0)
ax.legend(loc="lower left",fontsize=8,frameon=True,framealpha=0.9)
fig.savefig(O+"Figure1.pdf",bbox_inches="tight"); plt.close(fig)

# Figure 2: runtime vs number of objectives, end-to-end (Colab) and search-only (local)
T=pd.read_csv(R+"/tables/T2_performance_OSM.csv"); S=pd.read_csv(ROOT/"results/raw/split_local.csv")
dmap={"T-B":2,"T-I":2,"T-B-I":3,"T-B-S-St":4,"T-B-S-St-U":5}
fig,axs=plt.subplots(1,2,figsize=(6.3,2.6))
mk={"BOA*":"o","NAMOA*dr":"s","EMOA*":"^","BOA* (py)":"o","NAMOA*dr (py)":"s","LTMOA* (py)":"D","Martins (py)":"v"}
x=T[(T.scenario=="OSM")&(~T.alg.str.contains("non-exact"))&(T.set!="T-I")]
for alg,y in x.groupby("alg",sort=False):
    ls="-" if y.lang.iloc[0]=="C/C++" else "--"
    axs[0].plot(y.d,y.ms_median,marker=mk[alg],ls=ls,ms=4,label=alg.replace(" (py)"," (Py)"))
axs[0].set_yscale("log"); axs[0].set_xlabel("Number of objectives"); axs[0].set_ylabel("Median time per query (ms)")
axs[0].set_title("(a) Including heuristic computation",fontsize=9); axs[0].set_xticks([2,3,4,5])
S["d"]=S.set.map(dmap); S=S[S.set!="T-I"]
for alg,y in S.groupby("alg",sort=False):
    y=y.groupby("d").search_ms.median(); a=alg.replace(" (C++)","").replace(" (py)"," (Py)")
    axs[1].plot(y.index,y.values,marker=mk.get(alg.replace(" (C++)",""),"o"),ls="-" if "C++" in alg else "--",ms=4,label=a)
axs[1].set_yscale("log"); axs[1].set_xlabel("Number of objectives"); axs[1].set_title("(b) Search only, heuristics cached",fontsize=9); axs[1].set_xticks([2,3,4,5])
h0,l0=axs[0].get_legend_handles_labels(); axs[0].legend(h0,l0,fontsize=6.5,frameon=False,ncol=1)
axs[1].legend(fontsize=6.5,frameon=False)
from matplotlib.ticker import NullFormatter, LogLocator
for a in axs: a.yaxis.set_minor_formatter(NullFormatter()); a.yaxis.set_major_locator(LogLocator(base=10))
fig.tight_layout(); fig.savefig(O+"fig2_runtime.pdf",bbox_inches="tight"); plt.close(fig)

# Figure 3: extra time of the least-interruption route among trips with a trade-off
F=pd.read_csv(ROOT/"results/raw/front_stats.csv")
fig,ax=plt.subplots(figsize=(4.6,2.6))
for st,lab in [("T-B","Time–bumps"),("T-I","Time–interruptions"),("T-B-S-St","Time–bumps–signals–stops")]:
    y=np.sort(F[(F.set==st)&(F.front>1)].dT_minother_pct.values)
    ax.step(y,np.arange(1,len(y)+1)/len(y),where="post",label=f"{lab} (n = {len(y)})")
ax.set_xscale("symlog",linthresh=1); ax.set_xlabel("Extra travel time of the least-disturbed route (%)"); ax.set_ylabel("Cumulative share of trips")
ax.legend(fontsize=7,frameon=False); fig.tight_layout(); fig.savefig(O+"Figure2.pdf",bbox_inches="tight"); plt.close(fig)
