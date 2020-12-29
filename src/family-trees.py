import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import math
from textwrap import wrap

COLOR_MALE = "#34aeeb"
COLOR_FEMALE = "#de3e7e"

persons = pd.read_csv("./datasets/ibb/persons.csv", index_col="pid")

G = nx.DiGraph()

for pid, person in persons.iterrows():
  G.add_node(pid, **person)

for pid, person in persons.iterrows():
  if not math.isnan(person["father_pid"]):
    G.add_edge(person["father_pid"], pid)
  if not math.isnan(person["mother_pid"]):
    G.add_edge(person["mother_pid"], pid)

colors = list(map(lambda n: COLOR_MALE if n[1]["sex"] == "Male" else COLOR_FEMALE, G.nodes(data=True)))
pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
labels1 = {n[0]: f"{n[0]}\n{n[1]['name']}" for n in G.nodes(data=True)}
labels2 = {n[0]: "\n".join(wrap(" ".join(n[1]['family_name'].split('.')), width=25)) for n in G.nodes(data=True)}

plt.figure(num=None, figsize=(200, 2.5), frameon=False, clear=True, tight_layout=True)

nx.draw_networkx(G, pos=pos, node_color=colors, with_labels=False, node_size=50, linewidths=0.1, width=0.1, arrowsize=1, style="dashed", alpha=0.5)
nx.draw_networkx_labels(G, pos=pos, labels=labels1, font_size=2)
nx.draw_networkx_labels(G, pos={k:(v[0], v[1]-5) for k,v in pos.items()}, labels=labels2, font_size=1.5, font_color="#5a5a5a", verticalalignment="top")

plt.savefig("./datasets/ibb/family-trees.pdf", format="pdf", orientation="landscape")