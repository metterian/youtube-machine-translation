#%%
import glob
import json
import re
import time
from typing import List, Optional

import parmap
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

# %%
# set domain as hash tag
keywords = [
    "프랑스 요리",
    "영국 요리",
    "영국",
    "백종원",
    "수요미식회",
    "자취 요리",
    "레시피",
    "자격증",
    "운전",
    "셀피",
    "운동하는",
    "좀비",
    "분장",
    "데일리",
    "쇼핑",
    "쇼핑 하울",
    "하울",
    "100만원",
    "구매기",
    "구매 후기",
    "소개팅",
    "10대 소개팅",
    "취중진담",
    "술게임",
    "해장",
    "자전거",
    "카페",
    "카페 vlog",
    "카페 소개팅",
    "몰래카메라",
    "몰카",
    "카메라",
    "취미",
    "호캉스",
    "호텔",
    "부산",
    "영정도",
    "길거리",
    "운동",
    "운동복",
    "운동하는 직장인",
    "직장인",
    "대학생",
    "아프라카 BJ"
    "bj",
    "빅뱅",
    "bts",
    "big bang",
    "black pink",
    "kpop star",
    "k drama"
]

#%%


class Crawler:
    def __init__(self, headless: bool = False) -> None:
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=self.options
        )

    def quit(self):
        """quit driver"""
        self.driver.quit()

    def search_query_on_youtube(self, query: str) -> str:
        """make youtube search url"""
        url = f"https://www.youtube.com/results?search_query={query}"
        return url

    def search(self, keyword: str) -> None:
        """search youtube with keyword"""
        url = self.search_query_on_youtube(keyword)
        self.driver.get(url)

        # click the filter button
        filter_bttn = self.driver.find_element_by_xpath(
            """/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[1]/div[2]/ytd-search-sub-menu-renderer/div[1]/div/ytd-toggle-button-renderer/a/tp-yt-paper-button/yt-icon"""
        )
        filter_bttn.click()
        self.driver.implicitly_wait(3)

        # click on subtitle button from filter
        subtitle_bttn = self.driver.find_element_by_xpath(
            """/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[1]/div[2]/ytd-search-sub-menu-renderer/div[1]/iron-collapse/div/ytd-search-filter-group-renderer[4]/ytd-search-filter-renderer[4]/a/div/yt-formatted-string"""
        )
        subtitle_bttn.click()

    def scroll_down_to_bottom(self) -> None:
        """scroll down to bottom youtube page"""
        cur_height = self.driver.execute_script(
            "return document.documentElement.scrollHeight;"
        )
        next_height = cur_height
        while True:
            next_height = cur_height
            self.driver.execute_script(
                "document.documentElement.scrollTop = document.documentElement.scrollHeight;"
            )
            time.sleep(1)
            cur_height = self.driver.execute_script(
                "return document.documentElement.scrollHeight;"
            )
            if cur_height == next_height:
                break

    def download_and_save_html(self, keyword) -> None:
        """Dowload html page source and save it to html folder"""
        # rename keyword
        keyword = keyword.replace(" ", "_")

        self.html = self.driver.page_source
        with open(f"./html3/{keyword}.html", "w+", encoding="utf-8") as fp:
            fp.write(self.html)

    def download(self, keyword: str) -> None:
        """main function to download html page source using keywords list

        Args:
            keywords (str): keywords list
        """

        if not glob.glob(f"./html3/{keyword}.html"):
            self.search(keyword)
            self.scroll_down_to_bottom()
            self.download_and_save_html(keyword)

def run(keyword: str):
    bot = Crawler(headless=True)
    bot.download(keyword=keyword)

def main():
    parmap.map(run, keywords, pm_pbar=True, pm_processes=64)


if __name__ == "__main__":
    main()

# %%

# %%
