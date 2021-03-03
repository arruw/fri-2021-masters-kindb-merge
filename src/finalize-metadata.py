import pandas as pd
import math
from pprint import pprint

persons_df = pd.read_csv("annotations/kin-persons.csv")
images_df = pd.read_csv("annotations/kin-images.csv")
attributes_df = pd.read_csv("annotations/attributes.csv", index_col=0)

persons_paths_df = persons_df[["pid", "paths"]]
images_paths_df = images_df[["iid", "path"]]

del persons_df["paths"]
del images_df["path"]

images_df = images_df.merge(attributes_df, left_on="iid", right_on="iid", how="inner")

race_df = images_df.copy()
del race_df["iid"]
del race_df["age"]
del race_df["dominant_emotion"]
race_df = race_df.groupby("pid").agg(lambda x: x.value_counts().index[0]).reset_index()
race_df["race"] = race_df["dominant_race"]
del race_df["dominant_race"]

del images_df["dominant_race"]
images_df["emotion"] = images_df["dominant_emotion"]
del images_df["dominant_emotion"]

def map_pid(pid):
  if math.isnan(pid):
    return ""
  else:
    return str(int(pid))

persons_df["father_pid"] = persons_df["father_pid"].map(map_pid)
persons_df["mother_pid"] = persons_df["mother_pid"].map(map_pid)

persons_df = persons_df.merge(race_df, left_on="pid", right_on="pid", how="inner")

print(images_df.head())
print(persons_df.head())

images_df.to_csv("kindb-images.csv", index=False)
persons_df.to_csv("kindb-persons.csv", index=False)
images_paths_df.to_csv("kin-images-path-map.csv", index=False)
persons_paths_df.to_csv("kin-persons-paths-map.csv", index=False)

