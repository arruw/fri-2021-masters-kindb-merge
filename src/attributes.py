import pandas as pd
from deepface import DeepFace
from glob import glob
from pprint import pprint
from tqdm import tqdm

DB_ROOT = "/mnt/d/matja/dev/kindb-merge"

images = glob(f"{DB_ROOT}/**/*.png", recursive=True)

data = []
for index, image in tqdm(enumerate(images)):
  try:
    iid = int(image.split("/")[-1].replace(".png", ""))
    obj = DeepFace.analyze(
      img_path = image,
      actions = ['age', 'race', 'emotion'],
      enforce_detection = False)
    data.append([
      iid,
      obj["age"],
      obj["dominant_race"],
      obj["dominant_emotion"],
    ])

    if index % 10 == 0:
      df = pd.DataFrame(data, columns=["iid", "age", "dominant_race", "dominant_emotion"])
      df.to_csv("./annotations/attributes.csv")

  except Exception as e:
    print(f"[ERROR] {e}")
    continue

df = pd.DataFrame(data, columns=["iid", "age", "dominant_race", "dominant_emotion"])
df.to_csv("./annotations/attributes.csv")
