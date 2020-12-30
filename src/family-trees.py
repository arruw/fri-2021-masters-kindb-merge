import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import math
from textwrap import wrap

COLOR_MALE = "#34aeeb"
COLOR_FEMALE = "#de3e7e"

persons = pd.read_csv("./datasets/ibb/persons.csv", index_col="pid")
annotations = pd.read_csv("./datasets/ibb/annotations.csv")

ok_annotations = annotations.loc[\
  (~annotations["watermark"]) \
  & (~annotations["multiple_faces"]) \
  & (~annotations["low_resolution"]) \
  & (annotations["comment"].isnull()) \
  & (~annotations["occlusion"]) \
  & (~annotations["garbage"]) \
  , ["path", "hat", "sunglasses", "glasses"] \
]

def extract_iid(row):
  return row["path"].split("/")[-1].split(".")[0]

def extract_pid(row):
  return extract_iid(row).replace("_", "-").split("-")[0]

ok_annotations["iid"] = ok_annotations.apply(extract_iid, axis=1)
ok_annotations["pid"] = ok_annotations.apply(extract_pid, axis=1)

ok_images_count = ok_annotations[["iid", "pid"]].groupby(["pid"]).size().reset_index(name="count").set_index("pid").to_dict("index")

G = nx.DiGraph()

for pid, person in persons.iterrows():
  G.add_node(pid, **person)

for pid, person in persons.iterrows():
  if not math.isnan(person["father_pid"]):
    G.add_edge(person["father_pid"], pid)
  if not math.isnan(person["mother_pid"]):
    G.add_edge(person["mother_pid"], pid)

node_colors = [COLOR_MALE if n[1]["sex"] == "Male" else COLOR_FEMALE for n in G.nodes(data=True)]
node_border_colors = ["g" if ok_images_count.get(str(n), None) else "r" for n in G.nodes()]
pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
labels1 = {n[0]: f"{n[0]}\n{n[1]['name']}" for n in G.nodes(data=True)}
labels2 = {n[0]: "\n".join(wrap(" ".join(n[1]['family_name'].split('.')), width=25)) for n in G.nodes(data=True)}

plt.figure(num=None, figsize=(200, 2.5), frameon=False, clear=True, tight_layout=True)

nx.draw_networkx_nodes(G, pos=pos, node_color=node_colors, node_size=50, edgecolors=node_border_colors, linewidths=0.5, alpha=0.5)
nx.draw_networkx_edges(G, pos=pos, node_size=50, width=0.1, arrowsize=1, style="dashed", alpha=0.5)
nx.draw_networkx_labels(G, pos=pos, labels=labels1, font_size=2)
nx.draw_networkx_labels(G, pos={k:(v[0], v[1]-5) for k,v in pos.items()}, labels=labels2, font_size=1.5, font_color="#5a5a5a", verticalalignment="top")

plt.savefig("./datasets/ibb/family-trees.pdf", format="pdf", orientation="landscape")