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
        type_folder_path = Path("{}/types".format(cls.base_path))
        if not type_folder_path.exists():
            raise FileNotFoundError("分类文件不存在")

        for type_file_path in type_folder_path.iterdir():
            print(type_file_path)
            if type_file_path.is_dir():
                for file_path in type_file_path.iterdir():
                    print(file_path)


        # for movie_path in Path(movies_path).iterdir():
        #     if movie_path.is_file():
        #         with open(movie_path, "r", encoding="utf-8") as file:
        #             movie_json = json.load(file)
        #         if "isCompleted" in movie_json and movie_json["isCompleted"]:
        #             continue
        #         print(movie_json["remark"])
        #         if "全集" in movie_json["remark"] or "完结" in movie_json["remark"] or cls._is_match_full_episode(
        #                 movie_json["remark"]):
        #             movie_json["isCompleted"] = True
        #             json_str = json.dumps(movie_json, separators=(",", ":"), ensure_ascii=False)
        #             with open(movie_path, "w") as file:
        #                 print(json_str)
        #                 file.write("更新数据")
        #             continue
        #         print("重新加载")



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
                print(movie_json["remark"])
                if "全集" in movie_json["remark"] or "完结" in movie_json["remark"] or cls._is_match_full_episode(movie_json["remark"]):
                    movie_json["isCompleted"] = True
                    json_str = json.dumps(movie_json, separators=(",", ":"), ensure_ascii=False)
                    with open(movie_path, "w") as file:
                        print(json_str)
                        file.write("更新数据")
                    continue
                print("重新加载")
                # movie_href = cls._get_movie_href(movie_path)
                # Crawler.crawl_detail(movie_href, True)
                # 全集 完结

    # @classmethod
    # def refresh_movie_state(cls):
    #     """
    #     设置视频状态
    #     :return:
    #     """
    #     movies_path = Path("{}/movies".format(cls.base_path))
    #     if not movies_path.exists():
    #         raise FileNotFoundError("视频不存在")
    #
    #     for movie_path in Path(movies_path).iterdir():
    #         if movie_path.is_file():
    #             with open(movie_path, "r", encoding="utf-8") as file:
    #                 movie_json = json.load(file)
    #
    #             if movie_json is None:
    #                 continue
    #             for video in movie_json["videos"]:
    #                 if "errMessage" not in video:
    #                     video["isOk"] = True
    #                     continue
    #                 if video["errMessage"] == "success":
    #                     video["isOk"] = True
    #                 else:
    #                     video["isOk"] = False
    #                     movie_json["allVideosOk"] = False
    #                 del video["errMessage"]
    #             json_str = json.dumps(movie_json, separators=(",", ":"), ensure_ascii=False)
    #             print(json_str)
    #             with open(movie_path, "w") as file:
    #                 print(json_str)
    #                 file.write(json_str)


    @classmethod
    def _get_movie_href(cls, movie_path: Path):
        return "/hema/{}.html".format(movie_path.stem)
        pass

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
    # DataValidatorFixer.refresh_movie_state()
    try:
        Crawler.crawl_video_url("/play/63906-0-0.html")
    except Exception as e:
        print(e)