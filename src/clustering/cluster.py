import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pprint import pprint
from colorhash import ColorHash

from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist, squareform

df1 = pd.read_csv('./annotations/fr-in-embeddings.csv')
df2 = pd.read_csv('./annotations/ibb-embeddings.csv')
ibb_persons = pd.read_csv('./annotations/ibb-persons.csv')

def ibb_pid2label(pid):
    row = ibb_persons.loc[ibb_persons['pid'] == int(pid)]
    return f"{row['family_name'].to_string(header=False, index=False)}/{pid}/{row['name'].to_string(header=False, index=False)}"

df1["person"] = df1["path"].map(lambda x: "/".join(x.split("/")[-4:-1]))
df2["person"] = df2["path"].map(lambda x: ibb_pid2label(x.split("/")[-1].replace("_", "-").split("-")[0]))

df = pd.concat([df1, df2])

mean_embeddings = df.copy()
del mean_embeddings["path"]
 
mean_embeddings = pd.merge(
    mean_embeddings.groupby("person", as_index=False).mean(),
    mean_embeddings.groupby("person", as_index=False)["0"].count(),
    on="person") \
    .rename(columns={"0_x": "0", "0_y": "count"}) \
    .set_index("person")

del mean_embeddings["count"]

labels = mean_embeddings.index.tolist()

print("Calculating pdist...")
dist = pdist(mean_embeddings.to_numpy(), metric='cosine')
print("Calculating linkage...")
Z = linkage(dist, method='single')
print("Plotting...")
with plt.rc_context({'lines.linewidth': 0.5}):
    plt.clf()
    plt.figure(figsize=(10, 100))
    plt.title("Single linkage HC of avg. embeddings")
    dendrogram(Z, labels=labels, orientation='right')
    plt.axvline(0.05, ls=':', lw=0.8, c='r', alpha=0.5)
    plt.axvline(0.10, ls=':', lw=0.8, c='r', alpha=0.5)
    plt.axvline(0.15, ls=':', lw=0.8, c='r', alpha=0.5)
    plt.axvline(0.20, ls=':', lw=0.8, c='r', alpha=0.5)
    plt.grid(False)
    plt.tight_layout()
    plt.xticks(fontsize=6, rotation=0)
    plt.savefig("./annotations/clustering.pdf")
    # plt.show()