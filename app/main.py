import json
import logging
import os
import random
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import grequests

logger = logging.getLogger(__name__)


class GitHubCrawler:
    GITHUB_BASE_URL = "https://github.com/"
    REPOSITORY_TYPE = "Repositories"

    def __init__(self, keywords: list[str], proxies: list[str], type: str):
        self.keywords = keywords
        self.proxy = random.choice(proxies)
        self.type = type

    def get_urls(self) -> list[str]:
        url = f"{self.GITHUB_BASE_URL}search?q={','.join(self.keywords)}&type={self.type}&o=desc&s="
        rs = [grequests.get(url, proxies={"http": self.proxy})]
        response = grequests.map(rs)
        soup = BeautifulSoup(response[0].content, "html.parser")
        link_list = soup.find_all("a", {"class": "v-align-middle"})
        urls = [urljoin(self.GITHUB_BASE_URL, link["href"]) for link in link_list]
        return urls

    def get_repo_extra(self, response) -> dict[str, str | dict]:
        soup = BeautifulSoup(response.text, "html.parser")

        owner_data = soup.find("span", {"class": "author"}).find("a")
        owner = owner_data.get_text().strip()

        languages = soup.find_all("span", {"class": "color-fg-default text-bold mr-1"})

        return {
            "owner": owner,
            "language_stats": {lang.text: lang.findNext().text for lang in
                               languages} or None
        }

    def collect_url_info(self, urls) -> list[dict[str, str | dict]]:
        rs = (grequests.get(url, proxies={"http": self.proxy}) for url in urls)
        responses = grequests.map(rs)

        result: list[dict[str, str | dict]] = []
        for response, url in zip(responses, urls, strict=True):
            result_data = {"url": url}
            if self.type == self.REPOSITORY_TYPE:
                result_data.update({"extra": self.get_repo_extra(response)})
            result.append(result_data)
        return result


if __name__ == "__main__":
    files = [file for file in os.listdir("app/data") if file.startswith("input")]
    for index, file in enumerate(sorted(files)):
        with open(f"app/data/{file}", "r") as f:
            data = json.load(f)

        instance = GitHubCrawler(**data)
        collected_urls = instance.get_urls()
        collected_data = instance.collect_url_info(collected_urls)

        with open(f"app/data/output_example{index + 1}.json", "w") as f:
            json.dump(collected_data, f, indent=4)

        logger.warning(f"app/data/output_example{index + 1}.json was populated by data")
