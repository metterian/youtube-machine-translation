#%%
# Get transcript from YouTube
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from pprint import pprint
from typing import List

from bs4 import BeautifulSoup
from tqdm import tqdm
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

print = pprint
# %%
@dataclass
class Language:
    """Define language data structure"""

    code: str
    index: int = None
    transcript: List[dict] = None


@dataclass
class Subtitle:
    """Define subtitle data structure"""

    video_id: str
    en: object
    ko: object


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
path = Path("./html")
html_paths = path.glob("*.html")
# %%
html = list(html_paths)[1]

# %%
with html.open() as fp:
    soup = BeautifulSoup(fp, "lxml", from_encoding="utf-8")
# %%
divs = soup.find_all(
    "a", {"class": "yt-simple-endpoint style-scope ytd-video-renderer"}
)
video_ids = [div.get("href") for div in divs]
video_ids = video_ids
video_ids = map(get_video_id_from_url, video_ids)


#%%


def find_lang_index(lang, transcript_list):
    for i, transcript in enumerate(transcript_list):
        if transcript.language_code == lang.code:
            lang.index = i
    return lang


#%%

for video_id in video_ids:
    print(video_id)
    kor = Language("ko")
    eng = Language("en")
    # subtitle = Subtitle(video_id, en=eng, ko=kor)
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    for transcript in transcript_list:
        if transcript.language_code == "ko":
            if transcript.is_generated and not transcript.is_translatable:
                kor.transcript = transcript.fetch()
            elif transcript.is_generated and transcript.is_translatable:
                kor.transcript = transcript.fetch()
            elif not transcript.is_generated and transcript.is_translatable:
                kor.transcript = transcript.translate("en")
            elif not transcript.is_generated and not transcript.is_translatable:
                kor.transcript = None
        elif transcript.language_code == "en" or transcript.language_code == "en-US":
            if transcript.is_generated and not transcript.is_translatable:
                eng.transcript = transcript.fetch()
            elif transcript.is_generated and transcript.is_translatable:
                eng.transcript = transcript.fetch()
            elif not transcript.is_generated and transcript.is_translatable:
                eng.transcript = transcript.translate("ko")
            elif not transcript.is_generated and not transcript.is_translatable:
                eng.transcript = None
        else:
            continue
        print(asdict(subtitle))

# %%

# %%
len(test)
# %%

# %%
