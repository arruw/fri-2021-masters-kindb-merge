from tkinter import *
from PIL import ImageTk, Image
from glob import glob
from pprint import pprint
import csv
from os import path


class Main():

    def __init__(self, window, master, images, annotations_file_path):
        self.window = window
        self.master = master

        self.images = images
        self.image_index = 0

        self.annotations_file_path = annotations_file_path
        self.annotations = self._read_annotations()

        self.left_frame = Frame(self.master)
        self.left_frame.grid(row=0, column=0, sticky=N)
        self.right_frame = Frame(self.master)
        self.right_frame.grid(row=0, column=1, sticky=N)

        self.index_frame = Frame(self.left_frame)
        self.index_frame.pack(side=TOP)
        self.preview_frame = Frame(self.left_frame)
        self.preview_frame.pack(side=TOP)
        self.buttons_frame = Frame(self.left_frame)
        self.buttons_frame.pack(side=TOP)

        self.props_frame = Frame(self.right_frame)
        self.props_frame.grid(row=0, column=0, sticky=NW)
        self.flags_frame = Frame(self.right_frame)
        self.flags_frame.grid(row=1, column=0, sticky=NW)

        self.index_var = IntVar(value=1)
        self.index_var.trace_add("write", self.onIndexChange)
        self.only_flagged_var = BooleanVar(value=False)
        Label(self.index_frame, text="Image ").pack(side=LEFT)
        Spinbox(self.index_frame, from_=1, to=len(self.images), textvariable=self.index_var, justify=CENTER).pack(side=LEFT)
        Label(self.index_frame, text=" of ").pack(side=LEFT)
        Label(self.index_frame, text=len(self.images)).pack(side=LEFT)
        Checkbutton(self.index_frame, text="Only flagged", variable=self.only_flagged_var).pack(side=LEFT)

        self.canvas = Canvas(self.preview_frame, width=512, height=512)
        self.canvas.pack(fill="both", expand=True)

        Button(self.buttons_frame, text="Back", command=self.onBackButton).pack(side=LEFT)
        Button(self.buttons_frame, text="Next", command=self.onNextButton).pack(side=LEFT)
        self.window.bind('<Control-Left>', lambda _: self.onBackButton())
        self.window.bind('<Control-Right>', lambda _: self.onNextButton())

        self.prop_vars = {
            'size': StringVar()
        }
        Label(self.props_frame, text="Props:", anchor=W, font="Helvetica 16 bold").pack(side=TOP, fill=X)
        Label(self.props_frame, textvariable=self.prop_vars['size'], anchor=W).pack(side=TOP, fill=X)

        self.annotation_vars = {
            'watermark': BooleanVar(),
            'hat': BooleanVar(),
            'sunglasses': BooleanVar(),
            'glasses': BooleanVar(),
            'occlusion': BooleanVar(),
            'multiple_faces': BooleanVar(),
            'low_resolution': BooleanVar(),
            'garbage': BooleanVar(),
            'comment': StringVar(),
        }
        Label(self.flags_frame, text="Flags:", anchor=W, font="Helvetica 16 bold").pack(side=TOP, fill=X)
        Checkbutton(self.flags_frame, anchor=W, text="Watermark", variable=self.annotation_vars["watermark"]).pack(side=TOP, fill=X)
        Checkbutton(self.flags_frame, anchor=W, text="Hat", variable=self.annotation_vars["hat"]).pack(side=TOP, fill=X)
        Checkbutton(self.flags_frame, anchor=W, text="Sunglasses", variable=self.annotation_vars["sunglasses"]).pack(side=TOP, fill=X)
        Checkbutton(self.flags_frame, anchor=W, text="Glasses", variable=self.annotation_vars["glasses"]).pack(side=TOP, fill=X)
        Checkbutton(self.flags_frame, anchor=W, text="Occlusion", variable=self.annotation_vars["occlusion"]).pack(side=TOP, fill=X)
        Checkbutton(self.flags_frame, anchor=W, text="Multiple faces", variable=self.annotation_vars["multiple_faces"]).pack(side=TOP, fill=X)
        Checkbutton(self.flags_frame, anchor=W, text="Low resolution", variable=self.annotation_vars["low_resolution"]).pack(side=TOP, fill=X)
        Checkbutton(self.flags_frame, anchor=W, text="Garbage", variable=self.annotation_vars["garbage"]).pack(side=TOP, fill=X)
        Entry(self.flags_frame, textvariable=self.annotation_vars["comment"]).pack(side=TOP, fill=X)

        self._restore_annotation()
        self._load_image()

    def onNextButton(self):
        self._store_annotation()

        x = 1
        while True: 
            self.image_index = (self.image_index + 1) % len(self.images)
            self._restore_annotation()
            if not self.only_flagged_var.get() or self._is_annotation_flagged(): break
            if x >= len(self.images): self.only_flagged_var.set(False)
            x += 1

        self.index_var.set(self.image_index + 1)
        self._load_image()

    def onBackButton(self):
        self._store_annotation()

        x = 1
        while True:
            self.image_index = (self.image_index - 1) % len(self.images)
            self._restore_annotation()
            if not self.only_flagged_var.get() or self._is_annotation_flagged(): break
            if x >= len(self.images): self.only_flagged_var.set(False)
            x += 1

        self.index_var.set(self.image_index + 1)
        self._load_image()

    def onIndexChange(self, *args):
        try:
            new_index = int(self.index_var.get()) - 1
            if new_index == self.image_index:
                return

            if 0 <= new_index and new_index < len(self.images):
                self._store_annotation()

                self.image_index = new_index
                self._restore_annotation()
                self._load_image()
                
            else:
                self.index_var.set(self.image_index + 1)
        except Exception:
            self.index_var.set(self.image_index + 1)

    def _load_image(self):
        image_path = self.images[self.image_index]
        print(f"Loading image @ {self.image_index}: {image_path}")
        self.window.title(image_path)
        # self.canvas.delete("all")
        image = Image.open(image_path)
        self.prop_vars['size'].set(f"Size: {image.width}x{image.height}")
        image.thumbnail((512, 512), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(image)
        # self.canvas.config(width=self.image.width(), height=self.image.height())
        self.canvas.create_image(512/2-image.width/2, 512/2-image.height/2, anchor=NW, image=self.image)

    def _read_annotations(self):
        data = dict()

        if not path.exists(self.annotations_file_path):
            return data

        column_names = ["path", "watermark", "multiple_faces", "low_resolution", "comment", "hat", "sunglasses", "glasses", "occlusion", "garbage"]
        with open(self.annotations_file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file, fieldnames=column_names)
            next(reader)  # skip headers
            for row in reader:
                data[row["path"]] = row

        return data

    def _write_annotations(self):
        column_names = ["path", "watermark", "multiple_faces", "low_resolution", "comment", "hat", "sunglasses", "glasses", "occlusion", "garbage"]
        with open(self.annotations_file_path, "w") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=column_names)
            writer.writeheader()
            for data in self.annotations.values():
                writer.writerow(data)

    def _store_annotation(self):
        self.annotations[self.images[self.image_index]] = {
            'path': self.images[self.image_index],
            'watermark': self.annotation_vars["watermark"].get(),
            'hat': self.annotation_vars["hat"].get(),
            'sunglasses': self.annotation_vars["sunglasses"].get(),
            'glasses': self.annotation_vars["glasses"].get(),
            'occlusion': self.annotation_vars["occlusion"].get(),
            'multiple_faces': self.annotation_vars["multiple_faces"].get(),
            'low_resolution': self.annotation_vars["low_resolution"].get(),
            'garbage': self.annotation_vars["garbage"].get(),
            'comment': self.annotation_vars["comment"].get()
        }
        self._write_annotations()

    def _restore_annotation(self):
        annotation = self.annotations.get(self.images[self.image_index], dict())
        self.annotation_vars["watermark"].set(          self._get_or_default(annotation, "watermark", False))
        self.annotation_vars["hat"].set(                self._get_or_default(annotation, "hat", False))
        self.annotation_vars["sunglasses"].set(         self._get_or_default(annotation, "sunglasses", False))
        self.annotation_vars["glasses"].set(            self._get_or_default(annotation, "glasses", False))
        self.annotation_vars["occlusion"].set(          self._get_or_default(annotation, "occlusion", False))
        self.annotation_vars["multiple_faces"].set(     self._get_or_default(annotation, "multiple_faces", False))
        self.annotation_vars["low_resolution"].set(     self._get_or_default(annotation, "low_resolution", False))
        self.annotation_vars["garbage"].set(            self._get_or_default(annotation, "garbage", False))
        self.annotation_vars["comment"].set(            self._get_or_default(annotation, "comment", ""))

    def _get_or_default(self, coll, key, default):
        value = coll.get(key, "")
        if value == "":
            return default
        return value

    def _is_annotation_flagged(self):
        return any(map(lambda var: var.get(), self.annotation_vars.values()))

def main(args):
    base_path = args[1]
    # extensions = list(map(lambda ex: ex.strip(), args[2].split(",")))
    extensions = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]

    print(f"Searching the following globs: ")
    images = []
    for ex in extensions:
        print(f"\t{base_path}/**/{ex}")
        images.extend(glob(f"{base_path}/**/{ex}", recursive=True))
    images = list(sorted(images))

    print(f"Found {len(images)} images.")

    window = Tk()
    Main(window, window, images, f"{base_path}/annotations.csv")
    window.mainloop()


if __name__ == "__main__":
    import sys
    main(sys.argv)
