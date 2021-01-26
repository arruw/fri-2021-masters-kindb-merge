import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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

import cv2

device = "cpu"

mtcnn = MTCNN(device=device)

transform = transforms.Compose([
  transforms.Lambda(lambda x: cv2.cvtColor(x.cpu().detach().numpy(), cv2.COLOR_RGB2BGR))
])

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


img_pil = Image.open("./datasets/ibb/6-1.png").convert("RGB")
_, _, points = mtcnn.detect(img_pil, landmarks=True)

cx, cy, angle = get_pivot(points[0,0:2,0], points[0,0:2,1])
aligned_image = Image.fromarray(
  cv2.cvtColor(
    cv2.warpAffine(
      cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR),
      cv2.getRotationMatrix2D((cx, cy),angle,1),
      (img_pil.width, img_pil.height)
    ),
    cv2.COLOR_BGR2RGB
  )
)

plt.imshow(aligned_image)
plt.show()
