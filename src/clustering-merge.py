import pandas as pd
import numpy as np

from pprint import pprint
from glob import glob

clustering_merge_df = pd.read_csv("./annotations/clustering-merge.csv")
ibb_persons = pd.read_csv("./annotations/ibb-persons.csv")
ibb_persons["paths"] = ibb_persons["pid"]
infr_persons = pd.concat([pd.read_csv("./annotations/in-persons.csv"), pd.read_csv("./annotations/fr-persons.csv")])

persons_df = pd.concat([infr_persons, ibb_persons])
persons_df["xid"] = None

# 403, 227
merged_df = clustering_merge_df.groupby("Index")["Path"].apply(list).reset_index(name='Paths')
for i, row in merged_df.iterrows():
    # if row["Index"] != 227: continue
    paths = list(map(lambda x: int(x.split("/")[2]), filter(lambda x: len(x.split("/")) == 4, row["Paths"])))
    paths += list(filter(lambda x: len(x.split("/")) == 3, row["Paths"]))
    persons_df.loc[persons_df["paths"].isin(paths), "xid"] = row["Index"]

persons_df = persons_df.drop(persons_df.loc[persons_df["xid"].isna()].index)

pid2xid = dict()
for i, row in persons_df.iterrows():
    pid2xid[row["pid"]] = row["xid"]

persons_df["father_pid"] = persons_df["father_pid"].map(lambda x: pid2xid.get(x, None))
persons_df["mother_pid"] = persons_df["mother_pid"].map(lambda x: pid2xid.get(x, None))
persons_df["pid"] = persons_df["xid"]
del persons_df["xid"]
persons_df = persons_df.drop(persons_df.loc[persons_df["pid"].isna()].index)

def bucket(x):
    return list(filter(lambda x: str(x) != "nan", map(str, set(x))))

grouped_df = persons_df.groupby("pid").agg(bucket).reset_index()

grouped_df["name"] = grouped_df["name"].apply(lambda x: " ".join(map(lambda y: y.capitalize(), max(x, key=len).split(" "))))
grouped_df["family_name"] = grouped_df["family_name"].apply(lambda x: sorted(x)[0] if len(x) else None)
grouped_df["sex"] = grouped_df["sex"].apply(lambda x: x[0].upper()[0] if len(x) else None)
grouped_df["father_pid"] = grouped_df["father_pid"].apply(lambda x: x[0] if len(x) else None)
grouped_df["mother_pid"] = grouped_df["mother_pid"].apply(lambda x: x[0] if len(x) else None)

grouped_df = grouped_df.sort_values("family_name")
del grouped_df["fid"]

grouped_df.to_csv("./annotations/kin-persons.csv", index=False)


def image_globs(path):
    if path.isnumeric():
        return [
            f"./datasets/ibb/{path}-*.jpg",
            f"./datasets/ibb/{path}-*.JPG",
            f"./datasets/ibb/{path}-*.jpeg",
            f"./datasets/ibb/{path}-*.JPEG",
            f"./datasets/ibb/{path}-*.png",
            f"./datasets/ibb/{path}-*.PNG",
            f"./datasets/ibb/{path}_*.jpg",
            f"./datasets/ibb/{path}_*.JPG",
            f"./datasets/ibb/{path}_*.jpeg",
            f"./datasets/ibb/{path}_*.JPEG",
            f"./datasets/ibb/{path}_*.png",
            f"./datasets/ibb/{path}_*.PNG",
        ]
    else:
        return [
            f"./datasets/{path}/*.jpg",
            f"./datasets/{path}/*.JPG",
            f"./datasets/{path}/*.jpeg",
            f"./datasets/{path}/*.JPEG",
            f"./datasets/{path}/*.png",
            f"./datasets/{path}/*.PNG",
        ]

images_data = []
for i, row in grouped_df.iterrows():
    globs = []
    for path in row["paths"]:
        globs += image_globs(path)
    files = []
    for g in globs:
        files += glob(g)
    files = sorted(list(set(files)))
    for f in files:
        images_data += [[row["pid"], f]]

images_df = pd.DataFrame.from_records(images_data, columns=["pid", "path"])
images_df["iid"] = images_df.index + 1
images_df = images_df[["iid", "pid", "path"]]

# images_df = pd.read_csv("./annotations/kin-images.csv")

annotations_df = pd.concat([
    pd.read_csv("./annotations/ibb-annotations.csv"),
    pd.read_csv("./annotations/fr-annotations.csv")
])

to_delete = annotations_df.loc[
    (annotations_df["watermark"] == True) |
    (annotations_df["multiple_faces"] == True) |
    (annotations_df["low_resolution"] == True) |
    (annotations_df["occlusion"] == True) |
    (annotations_df["garbage"] == True) |
    (~annotations_df["comment"].isna())
]["path"].tolist()

images_df = images_df.drop(images_df.loc[images_df["path"].isin(to_delete)].index)

images_df.to_csv("./annotations/kin-images.csv", index=False)

embeddings_df = pd.concat([pd.read_csv('./annotations/fr-in-embeddings.csv'), pd.read_csv('./annotations/ibb-embeddings.csv')])
embeddings_df = embeddings_df.set_index("path").join(images_df.set_index("path"), how="inner")

embeddings_df_columns = embeddings_df.columns.values.tolist()
embeddings_df_columns.remove("iid")
embeddings_df_columns.remove("pid")
embeddings_df_columns = ["iid", "pid"] + embeddings_df_columns

embeddings_df = embeddings_df[embeddings_df_columns]
embeddings_df = embeddings_df.dropna()
embeddings_df.to_csv("./annotations/kin-embeddings.csv", index=False)


