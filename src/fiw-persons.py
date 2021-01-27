# MID,1,2,3,4,Gender,Name
# 1,0,5,4,4,Male,Madmoud
# 2,5,0,4,4,Female,Amina
# 3,1,1,0,2,Male,Tareq
# 4,1,1,2,0,Male,Yasser

import pandas as pd
from glob import glob
from pprint import pprint

# "Surname a/o Name","Family ID","Gender","Firstname","Student Email","Comment"
meta_df = pd.read_csv("./datasets/ibb/meta.csv")
meta_df["xid"] = meta_df["Family ID"] + "-" + meta_df["Firstname"]
meta_df["pid"] = meta_df.index + 2
meta_df = meta_df.rename(columns={"Surname a/o Name": "family_name", "Family ID": "fid", "Gender": "sex", "Firstname": "name"})
meta_df = meta_df.set_index("pid", drop=False)
del meta_df["Student Email"]
del meta_df["Comment"]

fn_df = meta_df[["family_name", "xid", "pid"]]


mid_files = sorted(glob("./datasets/fiw/F*/mid.csv"))
persons = []
for mid_file in mid_files:
    fid = mid_file.split("/")[-2]
    mid_df = pd.read_csv(mid_file, index_col="MID")
    mid_df["xid"] = mid_df["Name"].map(lambda x: f"{fid}-{x}")

    mids = mid_df.columns.tolist()[0:-2]


    for i, row in mid_df.iterrows():
        xid = row["xid"]
        name = row["Name"]
        sex = row["Gender"]
        fid = xid.split("-")[0]
        father_xid = None
        mother_xid = None
        for j, mid in enumerate(mids):
            if row[mid] != 1: continue
            parent = mid_df.loc[int(mid), :]
            if parent["Gender"] == "Male":
                father_xid = parent["xid"]
            else:
                mother_xid = parent["xid"]
        persons += [[xid, name, sex, fid, father_xid, mother_xid]]

persons_df = pd.DataFrame.from_records(persons, columns=["xid", "name", "sex", "fid", "father_xid", "mother_xid"])
persons_df = persons_df.set_index('xid', drop=False).join(fn_df.set_index('xid'), rsuffix="other_", how="inner")

xid2pid = dict()
for i, row in persons_df.iterrows():
    xid2pid[row["xid"]] = int(row["pid"])

persons_df["father_pid"] = persons_df["father_xid"].map(lambda x: xid2pid.get(x, None))
persons_df["mother_pid"] = persons_df["mother_xid"].map(lambda x: xid2pid.get(x, None))
del persons_df["xid"]
del persons_df["father_xid"]
del persons_df["mother_xid"]
persons_df = persons_df.set_index("pid", drop=False)
persons_df = persons_df.reindex(["pid", "name", "family_name", "sex", "fid", "father_pid", "mother_pid"], axis=1)
# print(persons_df.head(50))

# append <=F2000 
additions_df = meta_df.copy()
additions_df["isAddition"] = meta_df["xid"].map(lambda x: int(x.split("-")[0][1:]) >= 2000)
additions_df = additions_df.loc[additions_df["isAddition"] == True]
additions_df["father_pid"] = None
additions_df["mother_pid"] = None
del additions_df["isAddition"]
del additions_df["xid"]
additions_df = additions_df.reindex(["pid", "name", "family_name", "sex", "fid", "father_pid", "mother_pid"], axis=1)

# print(additions_df)

# pid,name,family_name,sex,fid,father_pid,mother_pid
pd.concat([persons_df, additions_df]).to_csv("./annotations/ibb-persons.csv", index=False)