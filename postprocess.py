#%%
import time

import numpy as np
import pandas as pd
import parmap
import requests
from bs4 import BeautifulSoup
from sklearn.model_selection import train_test_split

# %%
df = pd.read_csv("dataset_1M.csv", sep="\t")
# %%
urls = df.url.unique()
# %%
#%%
def get_video_info(url: str) -> dict:
    headers = requests.utils.default_headers()
    headers.update(
        {
            "User-Agent": "My User Agent 1.0",
        }
    )
    response = None
    while not response:
        try:
            response = requests.request("GET", url, headers=headers)
        except:
            time.sleep(1)
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        genre = soup.find("meta", {"itemprop": "genre"})["content"]
    except Exception as e:
        return None
    title = soup.find("meta", {"name": "title"})["content"]
    description = soup.find("meta", {"name": "description"})["content"]
    upload_ate = soup.find("meta", {"itemprop": "uploadDate"})["content"]
    view_count = soup.find("meta", {"itemprop": "interactionCount"})["content"]

    video_info = {
        "genre": genre,
        "title": title,
        "description": description,
        "upload_ate": upload_ate,
        "view_count": view_count,
    }
    return video_info


def get_info(url):
    video_info = get_video_info(url)
    if video_info:
        video_info["url"] = url
        return video_info


def main():
    video_infos = parmap.map(get_info, urls, pm_pbar=True, pm_processes=104)
    video_infos = [video_info for video_info in video_infos if video_info]
    info = pd.DataFrame(video_infos)
    df = df.merge(info, how="left", on="url")
    df.to_csv("dataset_1M.csv", encoding="utf-8-sig", index=False, sep="\t")


if __name__ == "__main__":
    main()
# %%

# %%
def split_dataset():
    dataset_index = np.arange(df.shape[0])

    train_index, test_index = train_test_split(
        dataset_index, shuffle=True, stratify=df.genre, test_size=3000, random_state=42
    )
    train_index, val_index = train_test_split(
        train_index,
        shuffle=True,
        stratify=df.iloc[train_index].genre,
        test_size=5000,
        random_state=42,
    )
    train, val, test = df.iloc[train_index], df.iloc[val_index], df.iloc[test_index]
    return train, val, test


# %%
train, val, test = split_dataset()
# %%
train.to_csv("./data/train.csv", encoding="utf-8-sig", index=False, sep="\t")
val.to_csv("./data/val.csv", encoding="utf-8-sig", index=False, sep="\t")
test.to_csv("./data/test.csv", encoding="utf-8-sig", index=False, sep="\t")
# %%
