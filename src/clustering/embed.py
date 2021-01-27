import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2

from pprint import pprint
from glob import glob
from tqdm import tqdm
from PIL import Image
from colorhash import ColorHash
from zipfile import ZipFile
from csv import DictReader

from facenet_pytorch import InceptionResnetV1, MTCNN

from torchvision import transforms, datasets
from torch.utils.data import DataLoader, Dataset

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN


def get_ibb_images():
    data = dict()
    column_names = ["path", "watermark", "multiple_faces", "low_resolution", "comment", "hat", "sunglasses", "glasses", "occlusion", "garbage"]
    with open("./datasets/ibb/annotations.csv", 'r') as csv_file:
        reader = DictReader(csv_file, fieldnames=column_names)
        next(reader)  # skip headers
        for row in reader:
            data[row["path"]] = row

    def is_ok(row):
        return \
            row["watermark"] == "False" \
            and row["multiple_faces"]  == "False" \
            and row["low_resolution"]  == "False" \
            and not row["comment"].strip() \
            and row["occlusion"] == "False" \
            and row["garbage"] == "False"

    return list(map(lambda x: x['path'], filter(is_ok, data.values())))

def get_pivot(x, y):
    x1, x2 = sorted(x)
    y1, y2 = sorted(y)
    cx = x1 + (x2 - x1)/2
    cy = y1 + (y2 - y1)/2

    vector_1 = [1, 0]
    vector_2 = [x2 - cx, y2 - cy]

    unit_vector_1 = vector_1 / np.linalg.norm(vector_1)
    unit_vector_2 = vector_2 / np.linalg.norm(vector_2)
    dot_product = np.dot(unit_vector_1, unit_vector_2)
    angle = np.arccos(dot_product)
    return (cx, cy, angle * 180 / np.pi)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'Running on device: {device}')

# load pretrained models
mtcnn = MTCNN(device=device)
resnet = InceptionResnetV1(pretrained='vggface2', device=device).eval()

# calculate embeddings
embeddings = []
image_paths = []

images = []
images += glob("./datasets/fr/**/*.jpg", recursive=True)
images += glob("./datasets/in/**/*.jpg", recursive=True)
images += glob("./datasets/fr/**/*.jpeg", recursive=True)
images += glob("./datasets/in/**/*.jpeg", recursive=True)
images += glob("./datasets/fr/**/*.png", recursive=True)
images += glob("./datasets/in/**/*.png", recursive=True)
images += glob("./datasets/fr/**/*.JPG", recursive=True)
images += glob("./datasets/in/**/*.JPG", recursive=True)
images += glob("./datasets/fr/**/*.JPEG", recursive=True)
images += glob("./datasets/in/**/*.JPEG", recursive=True)
images += glob("./datasets/fr/**/*.PNG", recursive=True)
images += glob("./datasets/in/**/*.PNG", recursive=True)
# images += get_ibb_images()

for img_path in tqdm(images):
    with torch.no_grad():
        try:
            img_pil = Image.open(img_path).convert("RGB")
            # _, _, points = mtcnn.detect(img_pil, landmarks=True)

            # # align
            # cx, cy, angle = get_pivot(points[0,0:2,0], points[0,0:2,1])
            # aligned_image = Image.fromarray(
            #     cv2.cvtColor(
            #         cv2.warpAffine(
            #             cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR),
            #             cv2.getRotationMatrix2D((cx, cy),angle,1),
            #             (img_pil.width, img_pil.height)
            #         ),
            #         cv2.COLOR_BGR2RGB
            #     )
            # )

            # crop
            img_cropped = mtcnn(img_pil)
            # img_cropped = mtcnn(aligned_image)

            # embed
            img_embedding = resnet(img_cropped.unsqueeze(0))
            embeddings.append(img_embedding.squeeze().cpu().tolist())
            image_paths.append(img_path)
        except:
            print(f"\t[ERROR] {img_path}")

# store computed embeddings
df = pd.concat([pd.DataFrame({'path': image_paths}), pd.DataFrame(embeddings)], axis=1)
df.to_csv('./annotations/fr-in-embeddings.csv', index=False)