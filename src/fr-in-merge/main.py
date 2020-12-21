import sys
from glob import glob
from os import path, walk
from pprint import pprint
from fuzzywuzzy import fuzz
import pathlib


def extract_member(members_paths, relation):
    relation = relation.upper()

    member = None
    if relation == "FATHER": 
        member = next(filter(lambda x: "FATHER" in x.upper(), members_paths), None)
    elif relation == "MOTHER": 
        member = next(filter(lambda x: "MOTHER" in x.upper(), members_paths), None)
    else: 
        member = next(filter(lambda x: "FATHER" not in x.upper() and "MOTHER" not in x.upper(), members_paths), None)

    if member == None:
        print(f"WARNING: Can not extract member {relation} for paths:")
        pprint(members_paths)
        return None

    member_path = member
    member = pathlib.PurePath(member).name.upper()
    member = list(filter(lambda x: x.strip() != "", member.translate(str.maketrans(",._-;:", "      ")).split(" ")))
    return (member_path, " ".join(member[:-1]), member[-1])


def main(argv):
    fr_base_path = "./datasets/fr/"
    in_base_path = "./datasets/in/"

    fr_families = []
    in_families = []

    for fr_family_dir in sorted(glob(f"{fr_base_path}Family_*/")):
        members = glob(f"{fr_family_dir}*/")
        father = extract_member(members, "FATHER")
        mother = extract_member(members, "MOTHER")
        child = extract_member(members, "CHILD")
        if father != None and mother != None:
            fr_families.append((father, mother, child))

    for in_family_dir in sorted(glob(f"{in_base_path}Family_*/")):
        members = glob(f"{in_family_dir}*/")
        father = extract_member(members, "FATHER")
        mother = extract_member(members, "MOTHER")
        child = extract_member(members, "CHILD")
        if father != None and mother != None:
            in_families.append((father, mother, child))

    # # FR & IN match
    # match_template = "|| {0:30} | {1:30} || {2:30} | {3:30} || {4:4} | {5:4} || {6:10} | {7:10} ||"
    # match_csv_template = '"{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}"'
    # print(match_csv_template.format("FR father", "IN father", "FR mother", "IN mother", "Father match %", "Mother match %", "FR family ID", "IN family ID"))
    # for (fr_father, fr_mother, _) in fr_families:
    #     for (in_father, in_mother, _) in in_families:
    #         fr_name_tokens = fr_father[1] + " " + fr_mother[1]
    #         in_name_tokens = in_father[1] + " " + in_mother[1]
    #         f_match = fuzz.token_sort_ratio(fr_father[1], in_father[1])
    #         m_match = fuzz.token_sort_ratio(fr_mother[1], in_mother[1])


    #         if (f_match >= 75 or m_match >= 75) and  f_match + m_match >= 100:
    #             fr_fid = pathlib.PurePath(fr_father[0]).parent.name
    #             in_fid = pathlib.PurePath(in_father[0]).parent.name
    #             print(match_csv_template.format(fr_father[1], in_father[1], fr_mother[1], in_mother[1], f_match, m_match, fr_fid, in_fid))


    # FR match
    match_template = "|| {0:30} | {1:30} || {2:30} | {3:30} || {4:4} | {5:4} || {6:10} | {7:10} ||"
    match_csv_template = '"{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}"'
    print(match_csv_template.format("FR father", "IN father", "FR mother", "IN mother", "Father match %", "Mother match %", "FR family ID", "IN family ID"))
    for (fr_father, fr_mother, _) in fr_families:
        for (in_father, in_mother, _) in fr_families:
            fr_fid = pathlib.PurePath(fr_father[0]).parent.name
            in_fid = pathlib.PurePath(in_father[0]).parent.name
            if fr_fid == in_fid: continue

            fr_name_tokens = fr_father[1] + " " + fr_mother[1]
            in_name_tokens = in_father[1] + " " + in_mother[1]
            f_match = fuzz.token_sort_ratio(fr_father[1], in_father[1])
            m_match = fuzz.token_sort_ratio(fr_mother[1], in_mother[1])


            if (f_match >= 75 or m_match >= 75) and  f_match + m_match >= 100:
                print(match_csv_template.format(fr_father[1], in_father[1], fr_mother[1], in_mother[1], f_match, m_match, fr_fid, in_fid))



    # # IN match
    # match_template = "|| {0:30} | {1:30} || {2:30} | {3:30} || {4:4} | {5:4} || {6:10} | {7:10} ||"
    # match_csv_template = '"{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}"'
    # print(match_csv_template.format("FR father", "IN father", "FR mother", "IN mother", "Father match %", "Mother match %", "FR family ID", "IN family ID"))
    # for (fr_father, fr_mother, _) in in_families:
    #     for (in_father, in_mother, _) in in_families:
    #         fr_fid = pathlib.PurePath(fr_father[0]).parent.name
    #         in_fid = pathlib.PurePath(in_father[0]).parent.name
    #         if fr_fid <= in_fid: continue

    #         fr_name_tokens = fr_father[1] + " " + fr_mother[1]
    #         in_name_tokens = in_father[1] + " " + in_mother[1]
    #         f_match = fuzz.token_sort_ratio(fr_father[1], in_father[1])
    #         m_match = fuzz.token_sort_ratio(fr_mother[1], in_mother[1])


    #         if (f_match >= 75 or m_match >= 75) and  f_match + m_match >= 100:
    #             print(match_csv_template.format(fr_father[1], in_father[1], fr_mother[1], in_mother[1], f_match, m_match, fr_fid, in_fid))


if __name__ == "__main__":
    main(sys.argv)
