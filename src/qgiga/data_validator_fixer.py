import json
import os
import re
from pathlib import Path

from bs4 import BeautifulSoup

from src.qgiga.crawler import Crawler
from src.qgiga.page_fetcher import PageFetcher


class DataValidatorFixer:
    base_path = "/Users/cuixg/Desktop/Project/GlowFlix/public/data-source/qgiga"

    def __init__(self):
        pass

    @classmethod
    def generate_search_catalog(cls):
        """
        生成索引目录
        :return:
        """
        pass

    @classmethod
    def regenerate_paginated_files(cls):
        """
        重新生成分页文件
        :return:
        """
        type_folder_path = Path("{}/types".format(cls.base_path))
        if not type_folder_path.exists():
            raise FileNotFoundError("分类文件不存在")

        for type_file_path in type_folder_path.iterdir():
            print(type_file_path)
            if type_file_path.is_dir():
                for file_path in type_file_path.iterdir():
                    print(file_path)

    @classmethod
    def detect_video_playable(cls):
        """
        检测不能观看视频
        :return:
        """
        movies_path = Path("{}/movies".format(cls.base_path))
        if not movies_path.exists():
            raise FileNotFoundError("视频不存在")

        for movie_path in Path(movies_path).iterdir():
            if movie_path.is_file():
                with open(movie_path, "r", encoding="utf-8") as file:
                    movie_json = json.load(file)
                if "allVideosOk" in movie_json and movie_json["allVideosOk"] and "isCompleted" in movie_json and movie_json["isCompleted"]:
                    continue
                try:
                    Crawler.crawl_detail("/hema/{}.html".format(movie_json["id"]), True)
                except Exception as e:
                    print(e)

    @classmethod
    def sanitize_movie_data(cls):
        """
        检测视频文件
        :return:
        """
        movies_path = Path("{}/movies".format(cls.base_path))
        if not movies_path.exists():
            raise FileNotFoundError("视频不存在")

        for movie_path in Path(movies_path).iterdir():
            if movie_path.is_file():
                with open(movie_path, "r", encoding="utf-8") as file:
                    movie_json = json.load(file)
                if "isCompleted" in movie_json and movie_json["isCompleted"]:
                    continue
                print(movie_json)

    @classmethod
    def sanitize_movie_completed(cls):
        """
        检测视频是否完结
        :return:
        """
        movies_path = Path("{}/movies".format(cls.base_path))
        if not movies_path.exists():
            raise FileNotFoundError("视频不存在")

        for movie_path in Path(movies_path).iterdir():
            if movie_path.is_file():
                with open(movie_path, "r", encoding="utf-8") as file:
                    movie_json = json.load(file)
                if "isCompleted" in movie_json and movie_json["isCompleted"]:
                    continue
                print("----------------------------------------------")
                print(movie_json["remark"])
                print(movie_json["videos"])
                print(len(movie_json["videos"]))
                completed = input("请输入Y/N：")
                if completed == "Y":
                    movie_json["isCompleted"] = True
                    json_str = json.dumps(movie_json, separators=(",", ":"), ensure_ascii=False)
                    cls._write_to_file(movie_path.as_posix(), json_str)

    @classmethod
    def _update_movie_completed(cls, path: str):
        with open(path, "r", encoding="utf-8") as file:
            movie_json = json.load(file)
        movie_json["isCompleted"] = True
        json_str = json.dumps(movie_json, separators=(",", ":"), ensure_ascii=False)
        cls._write_to_file(path, json_str)



    @classmethod
    def _write_to_file(cls, path: str, content: str):
        with open(path, "w") as file:
            file.write(content)

    @classmethod
    def _get_movie_href(cls, movie_path: Path):
        return "/hema/{}.html".format(movie_path.stem)

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
    DataValidatorFixer.detect_video_playable()
