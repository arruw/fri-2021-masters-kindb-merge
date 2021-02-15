# https://github.com/idealo/imagededup
# https://github.com/knjcode/imgdupes
# https://towardsdatascience.com/a-great-tool-for-image-datasets-cb249663ca45

import pandas as pd
import os
from PIL import Image
from pprint import pprint
from tqdm import tqdm

df = pd.read_csv("./annotations/kin-persons.csv")
df["merge_count"] = df["paths"].apply(lambda p: len(p.split("', '")))

df = df.sort_values("merge_count", ascending=False)
df = df.loc[df["merge_count"] > 1]

df.to_csv("./annotations/merges-count.csv")

print(df.head(75))
print(df.shape)