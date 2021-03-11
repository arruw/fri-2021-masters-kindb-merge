import pandas as pd
import seaborn as sns
import numpy as np
from pprint import pprint
from matplotlib import pyplot as plt

sns.set()

persons_df = pd.read_csv("annotations/kindb-persons.csv")
persons_df["race"] = persons_df["race"].astype("category")
persons_df["race_code"] = persons_df["race"].cat.codes

images_df = pd.read_csv("annotations/kindb-images.csv")
images_df = images_df.merge(persons_df, left_on="pid", right_on="pid", how="inner")
images_df["emotion"] = images_df["emotion"].astype("category")
images_df["emotion_code"] = images_df["emotion"].cat.codes

persons_df = persons_df.merge(
  images_df.groupby("pid").size().reset_index(name='#images'),
  left_on="pid", right_on="pid")



def group_minority(total, data):
  cutoff = total * 0.03
  minority = data[data <= cutoff]
  minority = minority[minority > 0]

  if minority.shape[0] <= 1:
    return data, None

  minority_sum = minority.sum()
  minority_label = "Other: " + ", ".join(minority.index.map(lambda x: str(x)).tolist()) 
  majority = data[data > cutoff]
  return majority.append(pd.Series([minority_sum], ["Other"])), minority_label


def plot_pie(total, data, title, file=None):
  plt.close('all')

  data, other_label = group_minority(total, data)

  data.plot.pie(autopct="%.1f%%", pctdistance=0.8)
  plt.title(title)
  plt.ylabel(None)
  if other_label:
    plt.xlabel(other_label)
  
  plt.tight_layout()
  if file:
    plt.savefig(file)
    return
  
  plt.show()

def plot_age_pie(file=None):
  total = images_df.shape[0]
  data = images_df.groupby(pd.cut(images_df['age'], np.arange(0, 100, 5))).size()
  plot_pie(total, data, "Age", file)


def plot_emotion_pie(file=None):
  total = images_df.shape[0]
  data = images_df.groupby("emotion").size()
  plot_pie(total, data, "Emotion", file)


def plot_race_pie(file=None):
  total = persons_df.shape[0]
  data = persons_df.groupby("race").size()
  plot_pie(total, data, "Race", file)


def plot_gender_pie(file=None):
  total = persons_df.shape[0]
  data = persons_df.groupby("sex").size()
  plot_pie(total, data, "Gender", file)


def plot_image_count(file=None):
  plt.close('all')

  data = images_df.groupby("pid").size().reset_index(name='counts')
  data = persons_df.merge(data, left_on="pid", right_on="pid")

  ax = plt.gca()
  sns.histplot(data, x="counts", binwidth=1, ax=ax)
  mean = data["counts"].mean()
  std = data["counts"].std()
  ax.axvline(mean, color="red", ls=":", label=f"$\mu = {mean:.2f}$")
  ax.axvline(mean+std, color="gray", ls=":", label=f"$\sigma = {std:.2f}$")
  ax.axvline(mean-std, color="gray", ls=":")
  plt.title(f"Number of images per person") 
  plt.ylabel("Frequency")
  plt.xlabel(None)
  plt.legend()
  
  plt.tight_layout()
  if file:
    plt.savefig(file)
    return
  
  plt.show()

# plot_age_pie("viz/age-pie.pdf")
# plot_emotion_pie("viz/emotion-pie.pdf")
# plot_race_pie("viz/race-pie.pdf")
# plot_gender_pie("viz/gender-pie.pdf")
# plot_image_count("viz/number-of-images.pdf")

sns.pairplot(images_df[["race_code","age","emotion_code"]], kind="hist", corner=True)
plt.show()