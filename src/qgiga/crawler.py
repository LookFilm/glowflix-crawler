import json
import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import m3u8

import requests
from bs4 import BeautifulSoup

from src.qgiga.page_fetcher import PageFetcher


class Crawler(object):
    base_path = "/Users/cuixg/Desktop/Project/GlowFlix/public/data-source/qgiga/"

    def __init__(self):
        pass

    @classmethod
    def refresh_all_info(cls):
        # folder = Path(cls.base_path)
        # if folder.exists():
        #     shutil.rmtree(folder)
        cls.crawl_index()
        # cls.crawl_all_type_list()

    @classmethod
    def crawl_index(cls):
        html = PageFetcher.fetch_html("/")
        if html is None:
            return
        soup = BeautifulSoup(html, "html.parser")
        modules = soup.find(id="index-main").find_all("div", class_="module")
        group_list = []
        for module in modules:
            module_title = module.find("div", class_="module-heading").find("h2", class_="module-title").get_text()
            movie_items = module.find("div", class_="module-list").find("div", class_="module-items").find_all("div",
                                                                                                               class_="module-item")
            movie_list = []
            for movie in movie_items:
                tag = movie.find("div", class_="module-item-text").get_text()
                cover = movie.find("div", class_="module-item-cover").find("img")["data-src"]
                href = movie.find("div", class_="module-item-titlebox").find("a")["href"]
                cls.crawl_detail(href)
                path = "/qgiga/movies/{}".format(cls.get_file_name(href))
                title = movie.find("div", class_="module-item-titlebox").find("a").get_text()
                movie_list.append({"title": title, "cover": cover, "href": href, "tag": tag, "path": path})
            group_list.append({"title": module_title, "list": movie_list})
        json_str = json.dumps(group_list, separators=(",", ":"), ensure_ascii=False)
        file_path = cls.base_path + "index.json"
        cls.write_to_file(file_path, json_str)

    @classmethod
    def crawl_all_type_list(cls):
        pass

    @classmethod
    def crawl_type_list(cls, url: str):
        html = PageFetcher.fetch_html(url)
        if html is None:
            return
        soup = BeautifulSoup(html, "html.parser")
        pass

    @classmethod
    def crawl_batch_detail(cls, urls: [str]):
        print("Crawling")
        with ThreadPoolExecutor(max_workers=8) as executor:
            for url in urls:
                executor.submit(cls.crawl_detail, url, False)
            # executor.map(cls.crawl_detail, urls)
        print("Finished")

    @classmethod
    def crawl_detail(cls, url: str, should_reload: bool = False):
        print("开始加载详情: {}".format(url))
        file_path = "{}/movies/{}".format(cls.base_path, cls.get_file_name(url))
        if Path(file_path).is_file() and not should_reload:
            return
        html = PageFetcher.fetch_html(url)
        if html is None:
            return
        soup = BeautifulSoup(html, "html.parser")
        main = soup.find(id="main").find("div", class_="view-heading")
        cover = main.find("div", class_="module-item-pic").find("img")["data-src"]
        video_info = main.find("div", class_="video-info")
        name = video_info.find("h1", class_="page-title").get_text()
        detail = {"cover": cover, "name": name}
        tags = []
        for tag in video_info.find_all(class_="tag-link"):
            tags.append(tag.get_text().replace("\n", "").replace(" ", ""))
        detail["tags"] = tags
        video_info_items = video_info.find_all("div", class_="video-info-items")
        for video_info_item in video_info_items:
            title = video_info_item.find("span", class_="video-info-itemtitle").get_text()
            content = video_info_item.find("div", class_="video-info-item")
            for slash in content.find_all("span", class_="slash"):
                slash.decompose()
            value = content.get_text().strip()
            if "导演" in title:
                detail["director"] = value
            elif "主演" in title:
                detail["actor"] = value
            elif "更新" in title:
                detail["updateTime"] = value
            elif "备注" in title:
                detail["remark"] = value
            elif "语言" in title:
                detail["language"] = value
            elif "剧情" in title:
                detail["plot"] = value
        videos = []
        for video in soup.find("div", class_="module-blocklist").find_all("a"):
            name = video.get_text().strip()
            href = video.get("href")
            url = cls.crawl_video_url(href)
            videos.append({"name": name, "url": url, "href": href})
        detail["videos"] = videos
        json_str = json.dumps(detail, separators=(",", ":"), ensure_ascii=False)
        cls.write_to_file(file_path, json_str)

    @classmethod
    def crawl_video_url(cls, url: str):
        print("开始加载视频: {}".format(url))
        html = PageFetcher.fetch_html(url)
        if html is None:
            return None
        soup = BeautifulSoup(html, "html.parser")
        info = soup.find(id="main").find("div", class_="wupanzhi").find("script").get_text()
        pattern = r'var now="(https?://.*?\.m3u8)"'
        match = re.search(pattern, info)
        if match is not None:
            url = match.group(1)
            return url
            # if cls.check_m3u8_available(url):
            #     return url
        return None

    @classmethod
    def get_file_name(cls, url: str):
        return "{}.json".format(Path(url).stem)

    @classmethod
    def write_to_file(cls, file_path: str, data: str):
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as file:
            file.write(data)

    @classmethod
    def check_m3u8_available(cls, url: str):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://vodcnd11.rsfcxq.com/"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=40, allow_redirects=True)
        except Exception as e:
            return False

        if resp.status_code != 200:
            return False

        # try:
        playlist = m3u8.loads(resp.text)
        if playlist is not None:
            return True
        return False


if __name__ == '__main__':
    # Crawler.crawl_video_url("/play/62396-0-0.html", True)
    # 62396  3029

    # Crawler.crawl_detail("/hema/61574.html")

    # Crawler.crawl_index()

    # print(Crawler.check_m3u8_available("https://v8.ppqrrs.com/wjv8/202607/28/9ASPwi2sxg95/video/index.m3u8"))

    Crawler.refresh_all_info()
