from enum import Enum

from pydantic import BaseModel, AnyUrl


class GithubType(str, Enum):
    repositories = "Repositories"
    issues = "Issues"
    wiki = "Wiki"


class GithubModel(BaseModel):
    type: GithubType
    proxies: list[AnyUrl]
    keywords: list[str]
