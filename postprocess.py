#%%
import time

import numpy as np
import pandas as pd
import parmap
import requests
from bs4 import BeautifulSoup

# %%
df = pd.read_csv("dataset.csv", sep="\t")
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


#%%

video_infos = parmap.map(get_info, urls, pm_pbar=True, pm_processes=104)

# %%
video_infos = [video_info for video_info in video_infos if video_info]
info = pd.DataFrame(video_infos)

# %%
df = df.merge(info, how="left", on="url")
# %%
df.to_csv("dataset_1M.csv", encoding="utf-8-sig", index=False, sep="\t")
# %%

# %%
