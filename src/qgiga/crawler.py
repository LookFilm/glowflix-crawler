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
    base_path = "/Users/cuixg/Desktop/Project/GlowFlix/public/data-source/qgiga"

    def __init__(self):
        pass

    @classmethod
    def refresh_all_info(cls):
        # index_path = os.path.join(cls.base_path, "index.json")
        # if os.path.exists(index_path):
        #     os.remove(index_path)
        # types_folder_path = os.path.join(cls.base_path, "types")
        # if os.path.exists(types_folder_path):
        #     shutil.rmtree(types_folder_path)

        type_hrefs = cls.crawl_all_type_href()

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.submit(cls.crawl_index)
            for href in type_hrefs:
                executor.submit(cls.crawl_type, href)


    @classmethod
    def crawl_index(cls):
        html = PageFetcher.fetch_html("/")
        soup = BeautifulSoup(html, "html.parser")
        modules = soup.find(id="index-main").find_all("div", class_="module")
        group_list = []
        for module in modules:
            module_title = module.find("div", class_="module-heading").find("h2", class_="module-title").get_text()
            movie_items = module.find("div", class_="module-list").find("div", class_="module-items").find_all("div", class_="module-item")
            movie_list = []
            for movie in movie_items:
                tag = movie.find("div", class_="module-item-text").get_text()
                cover = movie.find("div", class_="module-item-cover").find("img")["data-src"]
                href = movie.find("div", class_="module-item-titlebox").find("a")["href"]
                print("首页加载视频: {}-{}".format(module_title, href))
                try:
                    cls.crawl_detail(href, False)
                except Exception as e:
                    print(e)
                    continue
                path = "/qgiga/movies/{}".format(cls.get_file_name(href))
                title = movie.find("div", class_="module-item-titlebox").find("a").get_text()
                movie_list.append(
                    {"id": cls.get_movie_id(href), "title": title, "cover": cover, "href": href, "tag": tag,
                     "path": path})
            group_list.append({"title": module_title, "list": movie_list})
        json_str = json.dumps(group_list, separators=(",", ":"), ensure_ascii=False)
        file_path = cls.base_path + "/index.json"
        cls.write_to_file(file_path, json_str)

    @classmethod
    def crawl_all_type_list(cls):
        type_hrefs = ["/hm/6.html", "/hm/8.html", "/hm/5.html", "/hm/7.html"]# cls.crawl_all_type_href()
        for href in type_hrefs:
            cls.crawl_type(href)
            # page_hrefs = cls.crawl_type_page_href(href)
            # for page_href in page_hrefs:
            #     cls.crawl_type_list(page_href, False)

    @classmethod
    def crawl_all_type_href(cls):
        hrefs = []
        type_info_list = []
        html = PageFetcher.fetch_html("/")
        soup = BeautifulSoup(html, "html.parser")
        type_items = soup.find(id="index-nav").find("ul", class_="drop-content-items").find_all("li", class_="grid-item")
        for type_item in type_items:
            href = type_item.find("a")["href"]
            title = type_item.find("a").get_text()
            if title != "首页":
                hrefs.append(href)
                type_res = re.search(r"/(\d+)\.html", href)
                if type_res:
                    type_id = type_res.group(1)
                else:
                    raise ValueError("Can't find current page")
                type_info_list.append({"id": type_id, "title": title})

        json_str = json.dumps(type_info_list, separators=(",", ":"), ensure_ascii=False)
        file_path = cls.base_path + "/types/index.json"
        cls.write_to_file(file_path, json_str)
        return hrefs

    @classmethod
    def crawl_type(cls, type_href: str):
        page_hrefs = cls.crawl_type_page_href(type_href)
        for page_href in page_hrefs:
            cls.crawl_type_list(page_href, False)

    @classmethod
    def crawl_type_page_href(cls, url: str):
        hrefs = []
        html = PageFetcher.fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        main = soup.find(id="main")
        page = main.find("div", class_="module-footer").find("div", id="page")
        last_page_href = page.find("a", {"title": "尾页", "class": "page-number"})["href"]
        res = re.search(r"-(\d+)\.html", last_page_href)
        if res:
            page_size = res.group(1)
            for i in range(1, int(page_size) + 1):
                hrefs.append(url.replace(".html", "-{}.html".format(i)))
        return hrefs

    @classmethod
    def crawl_type_list(cls, url: str, should_reload: bool = False):
        html = PageFetcher.fetch_html(url)

        current_res = re.search(r"-(\d+)\.html", url)
        if current_res:
            current_page = current_res.group(1)
        else:
            raise ValueError("Can't find current page")

        type_res = re.search(r"/(\d+)-", url)
        if type_res:
            type_id = type_res.group(1)
        else:
            raise ValueError("Can't find current page")
        soup = BeautifulSoup(html, "html.parser")
        main = soup.find(id="main")
        # type_title = main.find("h1", class_="page-title").get_text()
        print("开始加载分类: {}".format(url))
        file_path = "{}/types/{}/{}.json".format(cls.base_path, type_id, current_page)
        if Path(file_path).is_file() and not should_reload:
            return
        total = main.find("div", class_="page-heading").find("span", class_="important").get_text()
        module_items = main.find("div", class_="module-items").find_all("div", class_="module-item")
        movie_list = []

        for module_item in module_items:
            tag = module_item.find("div", class_="module-item-text").get_text()
            cover = module_item.find("div", class_="module-item-cover").find("img")["data-src"]
            href = module_item.find("div", class_="module-item-titlebox").find("a")["href"]
            print("分类加载视频: {}-{}: {}".format(type_id, current_page, href))
            try:
                cls.crawl_detail(href, False)
            except Exception as e:
                print(e)
                continue
            path = "/qgiga/movies/{}".format(cls.get_file_name(href))
            title = module_item.find("div", class_="module-item-titlebox").find("a").get_text()
            movie_list.append(
                {"id": cls.get_movie_id(href), "title": title, "cover": cover, "href": href, "tag": tag, "path": path})
        page = main.find("div", class_="module-footer").find("div", id="page")
        # current_page = page.find("span", class_="page-current").get_text()
        last_page_href = page.find("a",  {"title": "尾页", "class": "page-number"})["href"]
        page_size = 1
        res = re.search(r"-(\d+)\.html", last_page_href)
        if res:
            page_size = res.group(1)

        page_info = {
            "page": current_page,
            "list": movie_list,
            "total": total,
            "totalPage": page_size
        }

        json_str = json.dumps(page_info, separators=(",", ":"), ensure_ascii=False)
        cls.write_to_file(file_path, json_str)

    @classmethod
    def crawl_batch_detail(cls, urls: [str]):
        print("Crawling")
        for url in urls:
            cls.crawl_detail(url, False)
        print("Finished")

    @classmethod
    def crawl_detail(cls, url: str, should_reload: bool = False):
        print("开始加载详情: {}".format(url))
        file_path = "{}/movies/{}".format(cls.base_path, cls.get_file_name(url))
        if Path(file_path).is_file() and not should_reload:
            print("已存在详情: {}".format(url))
            with open(file_path, "r", encoding="utf-8") as file:
                movie_json = json.load(file)
            if "isCompleted" in movie_json and movie_json["isCompleted"] and "allVideosOk" in movie_json and movie_json["allVideosOk"]:
                return
        html = PageFetcher.fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        main = soup.find(id="main").find("div", class_="view-heading")
        cover = main.find("div", class_="module-item-pic").find("img")["data-src"]
        video_info = main.find("div", class_="video-info")
        name = video_info.find("h1", class_="page-title").get_text()
        detail = {"cover": cover, "name": name, "id": cls.get_movie_id(url), "isCompleted": False}
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
                if "全集" in value or "完结" in value or cls._is_match_full_episode(value):
                    detail["isCompleted"] = True
            elif "语言" in title:
                detail["language"] = value
            elif "剧情" in title:
                detail["plot"] = value

        videos = []
        detail["allVideosOk"] = True
        for video in soup.find("div", class_="module-blocklist").find_all("a"):
            name = video.get_text().strip()
            if name == "全集":
                detail["isCompleted"] = True
            href = video.get("href")
            try:
                url = cls.crawl_video_url(href)
                videos.append({"name": name, "url": url, "href": href})
            except Exception as e:
                detail["allVideosOk"] = False
                detail["isCompleted"] = False
                break

        detail["videos"] = videos
        json_str = json.dumps(detail, separators=(",", ":"), ensure_ascii=False)
        cls.write_to_file(file_path, json_str)
        if not detail["allVideosOk"]:
            raise ValueError("影片部分视频错误,{}".format(url))

    @classmethod
    def crawl_video_url(cls, url: str):
        print("开始加载视频: {}".format(url))
        html = PageFetcher.fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        info = soup.find(id="main").find("div", class_="wupanzhi").find("script").get_text()
        pattern = r'var now="(https?://.*?\.m3u8)"'
        match = re.search(pattern, info)
        if match is None:
            raise ValueError("未获得播放地址")
        url = match.group(1)
        cls.check_m3u8_available(url)
        return url

    @classmethod
    def get_file_name(cls, url: str):
        return "{}.json".format(Path(url).stem)

    @classmethod
    def get_movie_id(cls, url: str):
        return Path(url).stem

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
            raise ConnectionError("请求视频异常", e)

        if resp.status_code != 200:
            raise ConnectionError("视频请求失败")

        playlist = m3u8.loads(resp.text)
        if playlist is None:
            raise ValueError("获取视频内容失败")

    @classmethod
    def _is_match_full_episode(cls, text: str) -> bool:
        """
        判断字符串是否符合「全数字集」格式，例如：全60集 → True
        Args:
            text: 待校验文本，如"全60集"
        Returns:
            bool: 符合返回True，否则False
        """
        if not isinstance(text, str):
            return False
        pattern = r"^全(\d+)集$"
        return bool(re.match(pattern, text.strip()))


if __name__ == '__main__':
    Crawler.refresh_all_info()
    # Crawler.crawl_index()

