import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import math
from textwrap import wrap
from pprint import pprint
from glob import glob
import numpy as np

OUT_ROOT = "/mnt/d/matja/dev/kindb-merge"

COLOR_MALE = "#34aeeb"
COLOR_FEMALE = "#de3e7e"

persons_df = pd.read_csv("./annotations/kindb-persons.csv")
images_df = pd.read_csv("./annotations/kindb-images.csv")

image_count_df = images_df.groupby("pid")["iid"].agg("count").reset_index()
image_count_df = image_count_df.rename(columns={"iid": "count"})
image_count_df = image_count_df.set_index("pid")

counts = image_count_df.to_dict()["count"]


G = nx.DiGraph()

for index, person in persons_df.iterrows():
  G.add_node(int(person["pid"]), **person)

for index, person in persons_df.iterrows():
  if not math.isnan(person["father_pid"]):
    G.add_edge(int(person["father_pid"]), int(person["pid"]))
  if not math.isnan(person["mother_pid"]):
    G.add_edge(int(person["mother_pid"]), int(person["pid"]))

# PRUNE
# prune nodes without image
prune = []
for n in G.nodes():
  if counts.get(n, 0) == 0:
    prune += [n]
for p in prune:
  G.remove_node(p)
# prune edges
prune = []
for e in G.edges():
  if len(G.in_edges(e[1])) == 1:
    prune += [e]
for p in prune:
  G.remove_edge(p[0], p[1])
# prune lonely nodes
prune = []
for n in G.nodes():
  if len(G.in_edges(n)) + len(G.out_edges(n)) == 0:
    prune += [n]
for p in prune:
  G.remove_node(p)

# COUNT TRIPLETS
n_triplets_s = 0
n_triplets_d = 0
n_triplets_i = 0
for n, nd in G.nodes(data=True):
  ie = list(G.in_edges(n))
  if len(ie) != 2: continue
  if nd["sex"] == "M":
    n_triplets_s += 1
  else:
    n_triplets_d += 1

  # print(f"{n}: {counts[n]} * {counts[ie[0][0]]} * {counts[ie[1][0]]} = {counts[n] * counts[ie[0][0]] * counts[ie[1][0]]}")
  # exit()
  n_triplets_i += (counts[n] * counts[ie[0][0]] * counts[ie[1][0]])

print(f"# father/mother/son triplets: {n_triplets_s}")
print(f"# father/mother/daughter triplets: {n_triplets_d}")
print(f"# number of positive sample combinations: {n_triplets_i}")
print(f"# number of images per person: {np.average(list(counts.values())):.2f}+/-{np.std(list(counts.values())):.2f}")
print(f"# total number of images: {sum(list(counts.values()))}")
print(f"# total number of persons: {len(list(G.nodes()))}")

node_colors = [COLOR_MALE if n[1]["sex"] == "M" else COLOR_FEMALE for n in G.nodes(data=True)]
node_border_colors = ["g" if counts.get(int(n), None) else "r" for n in G.nodes()]
pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
labels1 = {n[0]: f"{n[0]}\n{n[1]['name']}" for n in G.nodes(data=True)}
# labels2 = {n[0]: "\n".join(wrap(" ".join(n[1]['family_name'].split('.')), width=25)) for n in G.nodes(data=True)}

plt.figure(num=None, figsize=(200, 2.5), frameon=False, clear=True, tight_layout=True)

nx.draw_networkx_nodes(G, pos=pos, node_color=node_colors, node_size=50, edgecolors=node_border_colors, linewidths=0.5, alpha=0.5)
nx.draw_networkx_edges(G, pos=pos, node_size=50, width=0.1, arrowsize=1, style="dashed", alpha=0.5)
nx.draw_networkx_labels(G, pos=pos, labels=labels1, font_size=2)
# nx.draw_networkx_labels(G, pos={k:(v[0], v[1]-5) for k,v in pos.items()}, labels=labels2, font_size=1.5, font_color="#5a5a5a", verticalalignment="top")

plt.savefig("./annotations/kin-trees.pdf", format="pdf", orientation="landscape")

nx.write_gpickle(G, "./annotations/kin-trees.gpickle")



# persons_df = pd.read_csv("annotations/kindb-persons.csv")

# ok = []
# to_remove = []
# for index, person in persons_df.iterrows():
#   pid = int(person["pid"])
#   if pid not in G:
#     to_remove.append(index)
#   else:
#     ok.append(index)


# persons_df = persons_df.drop(persons_df.index[to_remove])
# persons_df.to_csv("annotations/kindb-persons.csv", index=False)

# images_df = pd.read_csv("annotations/kindb-images.csv")
# pprint(images_df.shape)
# images_df = images_df.merge(persons_df, left_on="pid", right_on="pid", how="inner")
# images_df = images_df.drop(columns=["name","family_name","sex","father_pid","mother_pid","race"])
# pprint(images_df.shape)
# images_df.to_csv("annotations/kindb-images.csv", index=False)
