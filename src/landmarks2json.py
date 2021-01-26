from tkinter import *
from PIL import ImageTk, Image
from glob import glob
from pprint import pprint
import csv
import json
import numpy as np
from os import path

def read_landmarks(file_path):
    with open(file_path, "r") as file:
        landmarks = file.readlines()
        landmarks = list(map(lambda l: l.replace("\n", "").strip().split(" "), landmarks))
        landmarks = list(filter(lambda l: len(l) == 15, landmarks))
    return landmarks

def landmark_to_json(landmark, file_name):
    # 0 1 2 3 4          5       6       7        8        9      10     11        12        13        14
    # x y w h confidence x_r_eye y_r_eye x_l_eye  y_l_eye, x_nose y_nose x_r_mouth y_r_mouth x_l_mouth x_l_mouth
    return {
        "data": [
            {
                f"{file_name}": [
                    {
                        "lefteye": [
                            int(landmark[5]),
                            int(landmark[6])
                        ],
                        "righteye": [
                            int(landmark[7]),
                            int(landmark[8])
                        ],
                        "nose": [
                            int(landmark[9]),
                            int(landmark[10])
                        ],
                        "leftmouthcorner": [
                            int(landmark[11]),
                            int(landmark[12])
                        ],
                        "rightmouthcorner": [
                            int(landmark[13]),
                            int(landmark[14])
                        ]
                    }
                ]
            }
        ]
    }

def process(glob_pattern):
    for file_path in glob(glob_pattern):
        file_name = file_path.split('/')[-1][:-4]
        landmarks = read_landmarks(file_path)
        weighted_area = list(map(lambda l: int(l[2]) * int(l[3]) * float(l[4]), landmarks))
        max_index = np.argmax(weighted_area)
        json_dict = landmark_to_json(landmarks[max_index], file_name)
        with open(f"./datasets/ibb-landmarks-json/landmarks_{file_name}.json", "w") as f:
            json.dump(json_dict, f)

process("./datasets/ibb-landmarks/*.txt")
