import pandas as pd

relation2sexMap = {
    "FATHER": "Male",
    "MOTHER": "Female",
    "DAUGHTER": "Female",
    "SON": "Male",
}

def getFather(row):
    import pprint
    pprint.pprint(row)
    return None

persons = pd.read_csv("./src/fr-in-merge/fr-families.csv")
persons["pid"] = persons.index + 1000
persons["name"] = persons["Name"]
persons["family_name"] = None
persons["sex"] = persons["Relation"].apply(lambda x: relation2sexMap[x])
persons["fid"] = persons['Family ID'].apply(lambda fid: f"FR1{int(fid):03d}")
persons["father_pid"] = persons.apply(lambda row: str(row["pid"] - 2) if row["Path"].endswith("_daughter/") else None, axis=1)
persons["mother_pid"] = persons.apply(lambda row: str(row["pid"] - 1) if row["Path"].endswith("_daughter/") else None, axis=1)
persons["paths"] = persons["Path"]

del persons["Name"]
del persons["Relation"]
del persons["Family ID"]
del persons["Path"]
del persons["Comment"]
del persons["Full Name"]

persons["pid"] = persons["pid"].map(lambda x: f"FR{x}")
persons["father_pid"] = persons["father_pid"].map(lambda x: f"FR{x}" if x else None)
persons["mother_pid"] = persons["mother_pid"].map(lambda x: f"FR{x}" if x else None)
persons["paths"] = persons["paths"].map(lambda x: x.replace("./datasets/", "")[:-1])

persons.to_csv("./annotations/fr-persons.csv", index=False)

print(persons.head(50))