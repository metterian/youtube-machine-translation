#%%
# Get transcript from YouTube
import csv
import itertools
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from glob import glob
from operator import index
from pathlib import Path
from pprint import pprint
from typing import List

import pandas as pd
import parmap
from bs4 import BeautifulSoup
from tqdm import tqdm
from youtube_transcript_api import YouTubeTranscriptApi

print = pprint

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


def get_video_id_from_html(html_path: str) -> List[str]:
    """get video id from html file after parsing

    Args:
        html_path (str): html file path

    Returns:
        List[str]: video ids in list
    """
    with open(html_path) as fp:
        soup = BeautifulSoup(fp, "lxml", from_encoding="utf-8")
    # TODO add filter shorts video
    divs = soup.find_all(
        "a", {"class": "yt-simple-endpoint style-scope ytd-video-renderer"}
    )
    return [get_video_id_from_url(div.get("href")) for div in divs]


def get_video_ids() -> List[str]:
    """ open all html files and get video ids """
    html_files = glob("./html/*.html")
    # html_keywords = [Path(file).stem for file in html_files]
    video_ids = parmap.map(
        get_video_id_from_html, html_files, pm_pbar=True, pm_processes=80
    )
    video_ids = filter_video_id(video_ids)
    return video_ids


def filter_video_id(video_ids: List[str]) -> List[str]:
    return [video_id for video_id in video_ids if "shorts" not in video_id]


# %%


@dataclass
class Subtitle:
    video_id: str
    ko: List[dict] = None
    en: List[dict] = None
    ko_translated: List[dict] = None
    en_translated: List[dict] = None

    def __post_init__(self):
        self.get_subtitle_from_api()

    def get_subtitle_from_api(self, translation: bool = False) -> None:
        try:
            self.transcript_list = YouTubeTranscriptApi.list_transcripts(self.video_id)
        except:
            return None
        for transcript in self.transcript_list:
            self.video_id = transcript.video_id
            if not transcript.is_generated:
                if transcript.language_code == "ko":
                    self.ko = transcript.fetch()
                    if translation:
                        self.en_translated = transcript.translate("en").fetch()
                if transcript.language_code in ["en", "en-US"]:
                    self.en = transcript.fetch()
                    if translation:
                        self.ko_translated = transcript.translate("ko").fetch()

    def __repr__(self) -> str:
        info = f"video_id: {self.video_id}"
        info += f"\nko: {bool(self.ko)}"
        info += f"\nen: {bool(self.en)}"
        info += f"\nko_translated: {bool(self.ko_translated)}"
        info += f"\nen_translated: {bool(self.en_translated)}"
        return info

    def make_dataframe(self, transcript: List[dict]) -> pd.DataFrame:
        """make Dataframe and preprocessing"""
        df = pd.DataFrame(transcript)
        df.text = df.text.str.replace("\n", " ")
        return df

    def to_list(self) -> List[dict]:
        """export subtitle variable to Dataframe

        Returns:
            pd.DataFrame: kor and eng subtitle are merged as Dataframe
        """

        return self.sync_subtitle()

    def sync_subtitle(self) -> dict:
        """Synchronization is performed based on the start time of subtitles.

        Returns:
            _type_: _description_
        """
        ko = {subtitle["start"]: subtitle["text"] for subtitle in self.ko}
        en = {subtitle["start"]: subtitle["text"] for subtitle in self.en}
        subtitle = [
            {"video_id": self.video_id, "start": start, "kor": text, "eng": en[start]}
            for start, text in ko.items()
        ]

        return subtitle
        # for dataframe
        # if self.ko and self.en:
        #     ko_df = self.make_dataframe(self.ko)
        #     ko_df = ko_df.rename(columns={"text": "kor"})

        #     en_df = self.make_dataframe(self.en)
        #     en_df = en_df.rename(columns={"text": "eng"})

        # elif self.ko and self.en_translated:
        #     ko_df = self.make_dataframe(self.ko)
        #     ko_df = ko_df.rename(columns={"text": "kor"})

        #     en_df = self.make_dataframe(self.en_translated)
        #     en_df = en_df.rename(columns={"text": "en_translated"})

        # elif self.ko_translated and self.en:
        #     ko_df = self.make_dataframe(self.ko_translated)
        #     ko_df = ko_df.rename(columns={"text": "ko_translated"})

        #     en_df = self.make_dataframe(self.en)
        #     en_df = en_df.rename(columns={"text": "eng"})

        # else:
        #     return None

        # df = ko_df.merge(en_df, how="outer", on="start", suffixes=("_kor", "_eng"))
        # df["video_id"] = self.video_id
        # df["href"] = self.url

        # return df

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"


subtitle = Subtitle("ob8NZqCLUL8")
#%%

# %%

if __name__ == "__main__":
    video_ids = get_video_ids()
    video_ids = list(itertools.chain(*video_ids))
    subtitles = parmap.map(Subtitle, video_ids[:2000], pm_pbar=True, pm_processes=50)
    subtitles = [Subtitle(video_id) for video_id in tqdm(video_ids[:2000])]

    dataset = [subtitle.to_list() for subtitle in subtitles]

    # datasets = [subtitle.to_pandas() for subtitle in dataset]
    # pd.concat(datasets, axis=0).to_csv("dataset.csv", encoding="utf-8-sig", index=False)

# %%
