"""Synthetic city used ONLY to test the notebook code path offline. Not research data."""
import numpy as np, networkx as nx, geopandas as gpd
from shapely.geometry import Point, LineString
def make_fixture(n=30, step=0.0012, seed=1):
    rng = np.random.default_rng(seed); G = nx.MultiDiGraph(crs="EPSG:4326"); lat0, lon0 = 35.17, -0.66
    for i in range(n):
        for j in range(n):
            a = {"y": lat0 + i * step, "x": lon0 + j * step}
            r = rng.random()
            if r < .04: a["highway"] = "traffic_signals"
            elif r < .08: a["highway"] = "stop"
            elif r < .10: a["highway"] = "crossing"
            elif r < .14: a["traffic_calming"] = "bump"
            elif r < .145: a["barrier"] = "bollard"
            G.add_node(i * n + j, **a)
    for i in range(n):
        for j in range(n):
            for di, dj in [(0, 1), (1, 0)]:
                if i + di >= n or j + dj >= n or rng.random() < .05: continue
                a, b = i * n + j, (i + di) * n + (j + dj)
                hw = "primary" if (i % 8 == 0 or j % 8 == 0) else rng.choice(["residential", "tertiary", "unclassified"])
                L = 111000 * step * (0.9 + .2 * rng.random()); ms = "50" if hw == "primary" else None
                surf = "unpaved" if rng.random() < .05 else ("asphalt" if rng.random() < .5 else None)
                if hw != "primary" and rng.random() < .2:
                    G.add_edge(a, b, length=L, highway=hw, maxspeed=ms, oneway=True, surface=surf)
                else:
                    for u, v in [(a, b), (b, a)]: G.add_edge(u, v, length=L, highway=hw, maxspeed=ms, oneway=False, surface=surf)
    hosp = gpd.GeoDataFrame({"name": ["CHU Test", "EPH Test", "Clinique X"]},
                            geometry=[Point(lon0 + .01, lat0 + .01), Point(lon0 + .025, lat0 + .028), Point(lon0 + .02, lat0 + .005)], crs="EPSG:4326")
    tc = gpd.GeoDataFrame({"traffic_calming": ["table"]}, geometry=[LineString([(lon0 + .0002, lat0 + .0060), (lon0 + .0004, lat0 + .0060)])], crs="EPSG:4326")
    return G, hosp, tc
