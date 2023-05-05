import random
from urllib.parse import urljoin

import grequests
from bs4 import BeautifulSoup


class GitHubCrawler:
    GITHUB_BASE_URL = "https://github.com/"
    REPOSITORY_TYPE = "Repositories"

    def __init__(self, keywords: list[str], proxies: list[str], type: str):
        self.keywords = keywords
        self.proxy = random.choice(proxies)
        self.type = type

    def get_urls(self) -> list[str]:
        url = urljoin(self.GITHUB_BASE_URL, "search")
        params = {"q": ','.join(self.keywords), "type": self.type, "o": "desc", "s": ""}

        rs = [grequests.get(url, params=params, proxies={"http": self.proxy})]
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

    def run(self) -> list[dict[str, str | dict]]:
        urls = self.get_urls()

        if not self.type == self.REPOSITORY_TYPE:
            return [{"url": url} for url in urls]

        rs = (grequests.get(url, proxies={"http": self.proxy}) for url in urls)
        responses = grequests.map(rs)

        result: list[dict[str, str | dict]] = []
        for response, url in zip(responses, urls, strict=True):
            result.append({"url": url, "extra": self.get_repo_extra(response)})
        return result
