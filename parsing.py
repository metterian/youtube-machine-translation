#%%
# Get transcript from YouTube
import multiprocessing
import sys
from dataclasses import asdict, dataclass, field
from glob import glob
from operator import index
from pathlib import Path
from pprint import pprint
from typing import List

import numpy as np
import pandas as pd
import parmap
from bs4 import BeautifulSoup
from tqdm import tqdm
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

print = pprint
# %%


@dataclass(unsafe_hash=True)
class Subtitle:
    """Define subtitle data structure"""

    transcript_list = object

    @property
    def url(self) -> str:
        self.video_id = [transcript.video_id for transcript in transcript_list][0]
        return f"https://www.youtube.com/watch?v={self.video_id}"


#%%
def get_url_from_hashtag(hashtag: str) -> str:
    """make youtube url for serching using hashtag

    Args:
        hashtag (str): #hashtag

    Returns:
        str: added youtube url
    """
    param: hashtag
    return f"https://www.youtube.com/hashtag/{hashtag}"


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
# get html paths from folder
html_files = glob("./html/*.html")
html_keywords = [Path(file).stem for file in html_files]
html_file = list(html_files)[3]

# %%
with open(html_file) as fp:
    soup = BeautifulSoup(fp, "lxml", from_encoding="utf-8")
# %%
# TODO add filter shorts video
divs = soup.find_all(
    "a", {"class": "yt-simple-endpoint style-scope ytd-video-renderer"}
)
video_ids = [get_video_id_from_url(div.get("href")) for div in divs]


# %%

# %%


@dataclass
class Subtitle:
    video_id: str
    keyword: str
    ko: List[dict] = None
    en: List[dict] = None
    ko_translated: List[dict] = None
    en_translated: List[dict] = None

    def __post_init__(self):
        try:
            self.transcript_list = YouTubeTranscriptApi.list_transcripts(self.video_id)
        except:
            return None
        for transcript in self.transcript_list:
            self.video_id = transcript.video_id
            if not transcript.is_generated:
                if transcript.language_code == "ko":
                    self.ko = transcript.fetch()
                    self.en_translated = transcript.translate("en").fetch()
                if (
                    transcript.language_code == "en"
                    or transcript.language_code == "en-US"
                ):
                    self.en = transcript.fetch()
                    self.ko_translated = transcript.translate("ko").fetch()

    def __repr__(self) -> str:
        return f"""video_id: {self.video_id}
    ko: {bool(self.ko)}
    en: {bool(self.en)}
    ko_translated: {bool(self.ko_translated)}
    en_translated: {bool(self.en_translated)}
    """

    def make_dataframe(self, transcript: List[dict]) -> pd.DataFrame:
        """make Dataframe and preprocessing"""
        df = pd.DataFrame(transcript)
        df.text = df.text.str.replace("\n", " ")
        return df

    def to_pandas(self) -> pd.DataFrame:
        """export subtitle variable to Dataframe

        Returns:
            pd.DataFrame: kor and eng subtitle are merged as Dataframe
        """
        df = pd.DataFrame(
            columns={"video_id", "ko", "en", "ko_translated", "en_translated"}
        )
        if self.ko and self.en:
            ko_df = self.make_dataframe(self.ko)
            ko_df = ko_df.rename(columns={"text": "kor"})

            en_df = self.make_dataframe(self.en)
            en_df = en_df.rename(columns={"text": "eng"})

        elif self.ko and self.en_translated:
            ko_df = self.make_dataframe(self.ko)
            ko_df = ko_df.rename(columns={"text": "kor"})

            en_df = self.make_dataframe(self.en_translated)
            en_df = en_df.rename(columns={"text": "en_translated"})

        elif self.ko_translated and self.en:
            ko_df = self.make_dataframe(self.ko_translated)
            ko_df = ko_df.rename(columns={"text": "ko_translated"})

            en_df = self.make_dataframe(self.en)
            en_df = en_df.rename(columns={"text": "eng"})

        else:
            return None

        df = ko_df.merge(en_df, how="outer", on="start", suffixes=("_kor", "_eng"))
        df["video_id"] = self.video_id
        df["href"] = self.url
        df["keyword"] = self.keyword
        return df

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"


#%%
# datasets = [Subtitle(video_id) for video_id in tqdm(video_ids)]

# %%
num_cores = multiprocessing.cpu_count()

splitted_dataset = np.array_split(video_ids, num_cores)
splitted_dataset = [x.tolist() for x in splitted_dataset]
dataset = parmap.map(Subtitle, splitted_dataset, pm_pbar=True, pm_processes=6)
# %%
