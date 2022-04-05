#%%
import glob
import time
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

# %%
# set domain as hash tag
keywords = [
    "mukbang",
    "makeup",
    "daily makeup",
    "ps4",
    "xbox" "배틀그라운드",
    "오버워치",
    "포트나이트",
    "개봉기",
    "스마트폰",
    "아이폰",
    "갤럭시",
    "애플",
    "삼성",
    "맥북",
    "키즈 자막",
    "키즈",
    "정치",
    "정치 자막",
    "정치 subtitle",
    "스포츠",
    "스포츠 자막",
    "epl",
    "epl 자막",
]

#%%

# "종교",
# "연예",
# "연애",


class Crawler:
    def __init__(self, keywords: List[str], headless=False) -> None:
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), chrome_options=self.options
        )
        self.keywords = keywords

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
        with open(f"./html/{keyword}.html", "w+", encoding="utf-8") as fp:
            fp.write(self.html)

    def download(self) -> None:
        """main function to download html page source"""
        for keyword in tqdm(self.keywords):
            if not glob.glob(f"./html/{keyword}.html"):
                self.search(keyword)
                self.scroll_down_to_bottom()
                self.download_and_save_html(keyword)

    def get_category(self, url: str):
        """Get video's category"""


if __name__ == "__main__":
    bot = Crawler(keywords)
    bot.download()
    bot.quit()


# %%
