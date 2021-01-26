from tkinter import *
from PIL import ImageTk, Image
from glob import glob
from pprint import pprint
import csv
import numpy as np
from os import path

# landmark_files = glob("./datasets/ibb-landmarks/*.txt")

# need_manual_intervention = 0

# # x y w h confidence x_r_eye y_r_eye x_l_eye  y_l_eye, x_nose y_nose x_r_mouth y_r_mouth x_l_mouth x_l_mouth

# for landmark_file in sorted(landmark_files):
#     with open(landmark_file, "r") as file:
#         landmarks = file.readlines()
#         landmarks = list(map(lambda l: l.replace("\n", "").strip(), landmarks))
#         landmarks = list(filter(lambda l: l, landmarks))

#         if len(landmarks) != 1:
#             print(f"{landmark_file}\t{len(landmarks)}")
#             need_manual_intervention += 1

# print(len(landmark_files))
# print(need_manual_intervention)


class Main():

    def __init__(self, window, master, landmark_files, final_landmarks_root):
        self.window = window
        self.master = master
        self.scale = 1024
        self.tags = ["r_eye", "l_eye", "nose", "r_mouth", "l_mouth"]

        self.index = 0
        self.landmark_index = 0
        self.landmark_files = landmark_files
        self.final_landmarks_root = final_landmarks_root

        self.window.bind('<Control-Left>', lambda _: self.onBackButton())
        self.window.bind('<Control-Right>', lambda _: self.onNextButton())

        self.canvas = Canvas(self.master, width=self.scale, height=self.scale)
        self.canvas.pack(fill="both", expand=True)

        self.landmarkObjectId = None
        self.canvas.bind("<ButtonPress-1>",  self.landmarkMoveStartCb)
        self.canvas.bind("<ButtonRelease-1>", self.landmarkMoveStopCb)

        self.image_scale = None
        self.image = None
        self._load_image()

    def onNextButton(self):
        self._save_landmarks()

        landmarks = None
        steps_left = len(self.landmark_files)
        while((landmarks is None or landmarks == 1) and steps_left > 0):
            self.index = (self.index + 1) % len(self.landmark_files)
            landmarks = len(self._get_landmarks(self.landmark_files[self.index]))
            steps_left -= 1

        print(f"{self.index}/{len(self.landmark_files)}")
        self._load_image()

    def onBackButton(self):
        self._save_landmarks()

        landmarks = None
        steps_left = len(self.landmark_files)
        while((landmarks is None or landmarks == 1) and steps_left > 0):
            self.index = (self.index - 1) % len(self.landmark_files)
            landmarks = len(self._get_landmarks(self.landmark_files[self.index]))
            steps_left -= 1
        
        print(f"{self.index}/{len(self.landmark_files)}")
        self._load_image()

    def landmarkMoveStartCb(self, event):
        x = event.x
        y = event.y
        objects = self.canvas.find_enclosed(x-20, y-20, x+20, y+20)
        objects = list(filter(lambda o: self.canvas.type(o) == "oval", objects))
        if len(objects) == 0: return
        pprint((x, y))
        self.landmarkObjectId = objects[0]

    # def landmarkMovCb(self, event):
    #     x = event.x - self.canvas.winfo_rootx()
    #     y = event.y - self.canvas.winfo_rooty()
    #     pprint((self.canvas.winfo_rootx(), self.canvas.winfo_rooty()))
    #     if not self.landmarkObjectId: return
    #     try:
    #         pprint(landmarkObjectId)
    #         self.canvas.coords(self.landmarkObjectId, event.x, event.y)
    #     except:
    #         pass

    def landmarkMoveStopCb(self, event):
        x = event.x
        y = event.y
        if not self.landmarkObjectId: return
        pprint((x, y))
        self.canvas.coords(self.landmarkObjectId, x, y, x, y)
        self.landmarkObjectId = None

    def _get_landmarks(self, landmark_file_path):
        with open(landmark_file_path, "r") as file:
            landmarks = file.readlines()
            landmarks = list(map(lambda l: l.replace("\n", "").strip().split(" "), landmarks))
            landmarks = list(filter(lambda l: len(l) == 15, landmarks))
        return landmarks

    def _load_image(self):
        landmark_file_path = self.landmark_files[self.index]
        image_file_path = "./datasets/ibb/" + landmark_file_path.split("/")[-1][:-4] + ".png"

        landmarks = self._get_landmarks(landmark_file_path)

        self.window.title(image_file_path)
        image = Image.open(image_file_path)
        width, height = image.size
        image.thumbnail((self.scale, self.scale), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(image)
        self.image_scale = (image.width/width, image.height/height, self.scale/2-image.width/2, self.scale/2-image.height/2)

        self.canvas.delete("all")
        self.canvas.create_image(self.scale/2-image.width/2, self.scale/2-image.height/2, anchor=NW, image=self.image)

        # Draw must probable landmarks
        weighted_area = list(map(lambda l: int(l[2]) * int(l[3]) * float(l[4]), landmarks))
        self.landmark_index = np.argmax(weighted_area)
        self._draw_landmark(landmarks[self.landmark_index])

        # for landmark in landmarks:
        #     self._draw_landmark(landmark, image.width/width, image.height/height, 512/2-image.width/2, 512/2-image.height/2)

    def _positionCanvas2Image(self, x, y):
        sx, sy, dx, dy = self.image_scale
        x = x * (1/sx) - dx
        y = y * (1/sy) - dy
        return (x, y)

    def _positionImage2Canvas(self, x, y):
        sx, sy, dx, dy = self.image_scale
        x = x * sx + dx
        y = y * sy + dy
        return (x, y)

    def _draw_landmark(self, landmark):
        # x y w h confidence x_r_eye y_r_eye x_l_eye  y_l_eye, x_nose y_nose x_r_mouth y_r_mouth x_l_mouth x_l_mouth
        coords = iter(map(int, landmark[5:]))
        colors = iter(["#A201E6", "#E62301", "#00AFE6", "#E6B401", "#01E607"])
        tags = iter(self.tags)
        for x, y, c, t in zip(coords, coords, colors, tags):
            x, y = self._positionImage2Canvas(x, y)
            self.canvas.create_oval(x, y, x, y, width=5, outline=c, tags=t)

    def _save_landmarks(self):
        xs = []
        ys = []
        for tag in self.tags:
            x, y, x1, y1 = self.canvas.coords(tag)
            x, y = self._positionCanvas2Image(x, y)
            xs += [int(x)]
            ys += [int(y)]

        landmark_file_path = self.landmark_files[self.index]
        final_path = self.final_landmarks_root + landmark_file_path.split("/")[-1]
        with open(final_path, "w") as file:
            file.write(f"{min(xs)} {min(ys)} {max(xs)-min(xs)} {max(ys)-min(ys)} 1.0 {xs[0]} {ys[0]} {xs[1]} {ys[1]} {xs[2]} {ys[2]} {xs[3]} {ys[3]} {xs[4]} {ys[4]} \n")
            

def main(args):
    landmark_files = sorted(glob("./datasets/ibb-landmarks/*.txt"))

    window = Tk()
    Main(window, window, landmark_files, "./datasets/ibb-landmarks-final/")
    window.mainloop()


if __name__ == "__main__":
    import sys
    main(sys.argv)