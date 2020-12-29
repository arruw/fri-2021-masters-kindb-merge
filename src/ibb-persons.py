import pandas as pd

relations = pd.read_csv("./datasets/ibb/relations.csv")

persons_raw = dict()
for index, row in relations.iterrows():
    if row["xlsStevilka"] not in persons_raw:
        persons_raw[row["xlsStevilka"]] = {
            "pid": row["xlsStevilka"],
            "name": row["IBBfinal.ime"],
            "family_name": row["Priimek"],
            "sex": row["IBBfinal.Spol"],
            "fid": row["OznakaDruzine"],
            "father_pid": None,
            "mother_pid": None,
        }
    if row["xlsStevilka_1"] not in persons_raw:
        persons_raw[row["xlsStevilka_1"]] = {
            "pid": row["xlsStevilka_1"],
            "name": row["IBBfinal_1.ime"],
            "family_name": row["Priimek"],
            "sex": row["IBBfinal_1.Spol"],
            "fid": row["OznakaDruzine"],
            "father_pid": None,
            "mother_pid": None,
        }

for index, row in relations.iterrows():
    # we can safely ignore other labels
    if row["label"] not in ["Parent", "Child"]: continue
    father = \
        (row["label"] == "Parent" and row["IBBfinal.Spol"] == "Male") or \
        (row["label"] == "Child" and row["IBBfinal_1.Spol"] == "Male")
    ppid = row["xlsStevilka"] if row["label"] == "Parent" else row["xlsStevilka_1"]
    pid = row["xlsStevilka_1"] if row["label"] == "Parent" else row["xlsStevilka"]
    if father:
        persons_raw[pid]["father_pid"] = ppid
    else:
        persons_raw[pid]["mother_pid"] = ppid


persons = pd.DataFrame.from_dict(persons_raw, orient="index")

persons.to_csv("./datasets/ibb/persons.csv", index=False)