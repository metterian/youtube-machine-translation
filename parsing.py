#%%
# Get transcript from YouTube
from glob import glob
from itertools import chain
from pprint import pprint
from typing import List

import numpy as np
import pandas as pd
import parmap
from bs4 import BeautifulSoup
from tqdm import tqdm
from youtube_transcript_api import YouTubeTranscriptApi

print = pprint

#%%


def get_video_id_from_url(url: str) -> str:
    """parse the youtube id from url

    Args:
        url (str): https://www.youtube.com/watch?v={video_id}

    Returns:
        str: parsed youtube id
    """
    return url.split("watch?v=")[-1]


def get_url_from_video_id(video_id: str) -> str:
    """make youtube url for serching using video id

    Args:
        video_id (str): video id

    Returns:
        str: added youtube url
    """
    return f"https://www.youtube.com/watch?v={video_id}"


# %%
def get_video_id_from_html(html_path: str) -> List[str]:
    """get video id from html file after parsing

    Args:
        html_path (str): html file path

    Returns:
        List[str]: video ids in list
    """
    with open(html_path) as fp:
        soup = BeautifulSoup(fp, "lxml", from_encoding="utf-8")
    divs = soup.find_all(
        "a", {"class": "yt-simple-endpoint style-scope ytd-video-renderer"}
    )
    return [get_video_id_from_url(div.get("href")) for div in divs]


def get_video_ids(n_workers: int) -> List[str]:
    """open all html files and get video ids"""
    html_files = glob("./html/*.html")
    # html_keywords = [Path(file).stem for file in html_files]
    video_ids = parmap.map(
        get_video_id_from_html, html_files, pm_pbar=True, pm_processes=n_workers
    )
    video_ids = filter_video_id(video_ids)
    return video_ids


def filter_video_id(video_ids: List[str]) -> List[str]:
    """remove youtube shorts videos"""
    return [video_id for video_id in video_ids if "shorts" not in video_id]


# %%


def get_subtitle_from_api(video_id: str) -> dict:
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    except:
        return None
    ko, en = None, None
    for transcript in transcript_list:
        video_id = transcript.video_id
        if not transcript.is_generated:
            if transcript.language_code == "ko":
                ko = transcript.fetch()
            if transcript.language_code in ["en", "en-US"]:
                en = transcript.fetch()
    if ko and en:
        return {"video_id": video_id, "kor": ko, "eng": en}
    else:
        return None


def sync_subtitle(subtitle) -> List[dict]:
    """Synchronization is performed based on the start time of subtitles.

    Returns:
        _type_: _description_
    """
    if subtitle:
        video_id, kor, eng = subtitle.values()
    else:
        return None

    ko = {subtitle["start"]: subtitle["text"] for subtitle in kor}
    en = {subtitle["start"]: subtitle["text"] for subtitle in eng}

    subtitles = []
    for start, text in ko.items():
        if start in en:
            subtitle = {
                "video_id": video_id,
                "start": start,
                "kor": text,
                "eng": en[start],
                "url": get_url_from_video_id(video_id),
            }
            subtitles.append(subtitle)

    return subtitles


def get_subtitle(video_id: List[str]):
    subtitle = get_subtitle_from_api(video_id)
    if subtitle:
        return sync_subtitle(subtitle)


#%%
if __name__ == "__main__":
    n_workers = 100

    video_ids = get_video_ids(n_workers=n_workers)
    video_ids = set(chain(*video_ids))
    splitted_data = np.array_split(video_ids, 20)

    dataset = []
    for data in splitted_data[:2]:
        subtitles = parmap.map(get_subtitle, data, pm_pbar=True, pm_processes=n_workers)

        subtitles = [subtitle for subtitle in subtitles if subtitle]
        subtitles = list(chain(*subtitles))

        dataset += subtitles
    df = pd.DataFrame(dataset)

# %%
