#%%
# Get transcript from YouTube
import sys
from dataclasses import asdict, dataclass, field
from glob import glob
from operator import index
from pathlib import Path
from pprint import pprint
from typing import List

import pandas as pd
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
# %%
html_file = list(html_files)[3]

# %%
with open(html_file) as fp:
    soup = BeautifulSoup(fp, "lxml", from_encoding="utf-8")
# %%
divs = soup.find_all(
    "a", {"class": "yt-simple-endpoint style-scope ytd-video-renderer"}
)
video_ids = [get_video_id_from_url(div.get("href")) for div in divs]


# %%
video_ids = video_ids[40:42]
lt = lambda x: YouTubeTranscriptApi.list_transcripts(x)
datasets = [Subtitle(lt(video_id)) for video_id in video_ids]

# %%


@dataclass
class Subtitle:
    # transcript_list: object
    video_id: str
    ko: List[dict] = None
    en: List[dict] = None
    ko_translated: List[dict] = None
    en_translated: List[dict] = None

    def __post_init__(self):
        self.transcript_list = YouTubeTranscriptApi.list_transcripts(self.video_id)
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
            en_df = self.make_dataframe(self.en)

            df = ko_df.merge(en_df, how="outer", on="start", suffixes=("_kor", "_eng"))

        elif self.ko and self.en_translated:
            ko_df = self.make_dataframe(self.ko)
            ko_df = ko_df.rename(columns={"text": "kor"})

            en_df = self.make_dataframe(self.en_translated)
            en_df = en_df.rename(columns={"text": "en_translated"})

            df = ko_df.merge(en_df, how="outer", on="start", suffixes=("_kor", "_eng"))

        elif self.ko_translated and self.en:
            ko_df = self.make_dataframe(self.ko_translated)
            ko_df = ko_df.rename(columns={"text": "ko_translated"})

            en_df = self.make_dataframe(self.en)
            en_df = en_df.rename(columns={"text": "eng"})

            df = ko_df.merge(en_df, how="outer", on="start", suffixes=("_kor", "_eng"))
        else:
            return None

        df["video_id"] = self.video_id
        return df

    @property
    def url(self):
        return f"https://www.youtube.com/watch?v={self.video_id}"


subtitle = Subtitle(video_id)

subtitle.to_pandas().head(50)
# %%
ko, en = [transcript.fetch() for transcript in transcript_list]  #%%
ko_df = pd.DataFrame(ko)
ko_df.text = ko_df.text.str.replace("\n", " ")
en_df = pd.DataFrame(en)
en_df.text = en_df.text.str.replace("\n", "")
pd.concat([ko_df, en_df], axis=1)
# %%
kr_translation = [
    transcript.translate("en").fetch()
    for transcript in transcript_list
    if transcript.language_code == "ko"
]
kr_tr_df = pd.DataFrame(kr_translation[0])
kr_tr_df.text = kr_tr_df.text.str.replace("\n", " ")
# %%
ko_df.merge(kr_tr_df, how="inner", on="start").tail(50)
# %%
