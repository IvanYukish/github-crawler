from unittest.mock import patch

import grequests
import pytest
import requests

from app.crawlers import GitHubCrawler


@pytest.mark.parametrize(
    "test_input,expected", [
        (
                {
                    "keywords": [
                        "openstack",
                        "nova",
                        "css"
                    ],
                    "proxies": [
                        "https://198.27.74.6:9300"
                    ],
                    "type": "Repositories"
                }, ['https://github.com/atuldjadhav/DropBox-Cloud-Storage',
                    'https://github.com/michealbalogun/Horizon-dashboard']
        )
    ]

)
@patch.object(grequests, "get")
@patch.object(grequests, "map")
def test_get_urls(mock_map, mock_get, test_input, expected):
    with open('tests/test_data/github_test.html', 'r') as file:
        content = file.read()

    response = [requests.Response()]
    response[0].status_code = 200
    response[0]._content = content
    mock_map.return_value = response
    instance = GitHubCrawler(**test_input)
    urls = instance.get_urls()
    assert urls == expected


@pytest.mark.parametrize(
    "test_input,expected", [
        (
                ['https://github.com/atuldjadhav/DropBox-Cloud-Storage'],
                [
                    {
                        "url": "https://github.com/atuldjadhav/DropBox-Cloud-Storage",
                        "extra": {
                            "owner": "atuldjadhav",
                            "language_stats": {
                                "CSS": "52.0%",
                                "JavaScript": "47.2%",
                                "HTML": "0.8%"
                            }
                        }
                    },
                ]
        )
    ]
)
@patch.object(grequests, "get")
@patch.object(grequests, "map")
@patch.object(GitHubCrawler, "get_urls")
def test_run(mock_crawler, mock_map, mock_get, test_input, expected):
    with open('tests/test_data/cloud_storage.html', 'r') as file:
        content = file.read()

    mock_crawler.return_value = test_input
    response = [requests.Response()]
    response[0].status_code = 200
    response[0]._content = bytes(content, "utf-8")
    mock_map.return_value = response
    instance = GitHubCrawler(**{
        "keywords": [
            "openstack",
            "nova",
            "css"
        ],
        "proxies": [
            "https://198.27.74.6:9300"
        ],
        "type": "Repositories"
    })
    collected_data = instance.run()

    assert collected_data == expected
