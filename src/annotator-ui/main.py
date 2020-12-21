# ###!./.env/bin/python3

# pip install Pillow

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

        self.window.protocol

        self.index_frame = Frame(self.master)
        self.index_frame.grid(row=0, column=0)
        self.preview_frame = Frame(self.master)
        self.preview_frame.grid(row=1, column=0)
        self.buttons_frame = Frame(self.master)
        self.buttons_frame.grid(row=2, column=0)
        self.flags_frame = Frame(self.master)
        self.flags_frame.grid(row=3, column=0)

        self.index_var = IntVar(value=1)
        self.index_var.trace_add("write", self.onIndexChange)
        Label(self.index_frame, text="Image ").pack(side=LEFT)
        Entry(self.index_frame, textvariable=self.index_var,
              justify=CENTER).pack(side=LEFT)
        Label(self.index_frame, text=" of ").pack(side=LEFT)
        Label(self.index_frame, text=len(self.images)).pack(side=LEFT)

        self.canvas = Canvas(self.preview_frame, width=300, height=300)
        self.canvas.pack(fill="both", expand=True)

        Button(self.buttons_frame, text="Back",
               command=self.onBackButton).pack(side=LEFT)
        Button(self.buttons_frame, text="Next",
               command=self.onNextButton).pack(side=LEFT)

        self.annotation_vars = {
            'watermark': BooleanVar(),
            'multiple_faces': BooleanVar(),
            'low_resolution': BooleanVar(),
            'comment': StringVar(),
        }
        Checkbutton(self.flags_frame, text="Watermark",
                    variable=self.annotation_vars["watermark"]).pack(side=LEFT)
        Checkbutton(self.flags_frame, text="Multiple faces",
                    variable=self.annotation_vars["multiple_faces"]).pack(side=LEFT)
        Checkbutton(self.flags_frame, text="Low resolution",
                    variable=self.annotation_vars["low_resolution"]).pack(side=LEFT)

        Entry(self.master, textvariable=self.annotation_vars["comment"]).grid(
            row=4, column=0)

        self._load_image()

    def onNextButton(self):
        self._store_annotation()

        self.image_index = (self.image_index + 1) % len(self.images)
        self.index_var.set(self.image_index + 1)
        self._load_image()

    def onBackButton(self):
        self._store_annotation()

        self.image_index = (self.image_index - 1) % len(self.images)
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
                self._load_image()
            else:
                self.index_var.set(self.image_index + 1)
        except Exception:
            self.index_var.set(self.image_index + 1)

    def _load_image(self):
        image_path = self.images[self.image_index]
        print(f"Loading image @ {self.image_index}: {image_path}")
        self.window.title(image_path)
        self.canvas.delete("all")
        self.image = ImageTk.PhotoImage(Image.open(image_path))
        self.canvas.config(width=self.image.width(),
                           height=self.image.height())
        self.canvas.create_image(0, 0, anchor=NW, image=self.image)
        self._restore_annotation()

    def _read_annotations(self):
        data = dict()

        if not path.exists(self.annotations_file_path):
            return data

        column_names = ["path", "watermark",
                        "multiple_faces", "low_resolution", "comment"]
        with open(self.annotations_file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file, fieldnames=column_names)
            next(reader)  # skip headers
            for row in reader:
                data[row["path"]] = row

        return data

    def _write_annotations(self):
        column_names = ["path", "watermark",
                        "multiple_faces", "low_resolution", "comment"]
        with open(self.annotations_file_path, "w") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=column_names)
            writer.writeheader()
            for data in self.annotations.values():
                writer.writerow(data)

    def _store_annotation(self):
        self.annotations[self.images[self.image_index]] = {
            'path': self.images[self.image_index],
            'watermark': self.annotation_vars["watermark"].get(),
            'multiple_faces': self.annotation_vars["multiple_faces"].get(),
            'low_resolution': self.annotation_vars["low_resolution"].get(),
            'comment': self.annotation_vars["comment"].get()
        }
        self._write_annotations()

    def _restore_annotation(self):
        annotation = self.annotations.get(
            self.images[self.image_index], {
                'path': self.images[self.image_index],
                'watermark': False,
                'multiple_faces': False,
                'low_resolution': False,
                'comment': ""
            })
        self.annotation_vars["watermark"].set(annotation["watermark"])
        self.annotation_vars["multiple_faces"].set(
            annotation["multiple_faces"])
        self.annotation_vars["low_resolution"].set(
            annotation["low_resolution"])
        self.annotation_vars["comment"].set(annotation["comment"])


def main(args):
    base_path = args[1]
    extensions = list(map(lambda ex: ex.strip(), args[2].split(",")))

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
