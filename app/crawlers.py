import random
from urllib.parse import urljoin, urlparse

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
        params = {"q": ' '.join(self.keywords), "type": self.type}

        rs = [grequests.get(url, params=params, headers={"Accept": "text/html"})]
        urls = [urljoin(self.GITHUB_BASE_URL, link["href"]) for link in self.parse_and_get_links(grequests.map(rs))]
        return urls

    def parse_and_get_links(self, response) -> list[dict]:
        links = []
        soup = BeautifulSoup(response[0].text, "html.parser")

        result_list = soup.find_all("div", attrs={"class": "Box-sc-g0xbh4-0 bBwPjs search-title"})
        for item in result_list:
            for link in item.find_all('a', href=True):
                links.append(link)

        return links

    def get_repo_extra(self, response) -> dict[str, str | dict]:
        soup = BeautifulSoup(response.text, "html.parser")
        owner = urlparse(response.url).path.split("/")[1]

        languages = soup.find_all("span", {"class": "color-fg-default text-bold mr-1"})

        return {
            "owner": owner,
            "language_stats": {lang.text: lang.findNext().text for lang in languages} or None
        }

    def run(self) -> list[dict[str, str | dict]]:
        urls = self.get_urls()

        if not self.type == self.REPOSITORY_TYPE:
            return [{"url": url} for url in urls]

        # can't find appropriate https proxy use only http
        # rs = (grequests.get(url, proxies={"http": self.proxy, "https": self.proxy}) for url in urls)

        rs = (grequests.get(url, proxies={"http": self.proxy}) for url in urls)
        responses = grequests.map(rs)

        result: list[dict[str, str | dict]] = []
        for response, url in zip(responses, urls, strict=True):
            result.append({"url": url, "extra": self.get_repo_extra(response)})
        return result
