from typing import Any

from pydantic import BaseModel, ConfigDict


def filter_unknown_keys(data: dict[str, Any], model_class: type[BaseModel]) -> dict[str, Any]:
    """
    Pure-function filter to strip unknown keys matching against model.__fields__ before
    constructing the model instance, to avoid validation errors when extra='forbid' is used.
    """
    allowed_keys = set(model_class.model_fields.keys())
    return {k: v for k, v in data.items() if k in allowed_keys}


class Repository(BaseModel):
    """
    GitHub Repository model.
    API docs: https://docs.github.com/en/rest/repos/repos
    Mapped keys:
    - Stars -> stargazers_count
    - Forks -> forks_count
    - Open Issue Count -> open_issues_count
    """

    id: int
    name: str
    full_name: str
    stargazers_count: int
    forks_count: int
    open_issues_count: int

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def from_api_payload(cls, payload: dict[str, Any]) -> "Repository":
        filtered_payload = filter_unknown_keys(payload, cls)
        return cls(**filtered_payload)


class CommitAuthor(BaseModel):
    name: str
    email: str
    date: str

    model_config = ConfigDict(extra="forbid")


class CommitDetail(BaseModel):
    author: CommitAuthor
    message: str

    model_config = ConfigDict(extra="forbid")


class Commit(BaseModel):
    """
    GitHub Commit model.
    API docs: https://docs.github.com/en/rest/commits/commits
    """

    sha: str
    commit: CommitDetail

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def from_api_payload(cls, payload: dict[str, Any]) -> "Commit":
        filtered_payload = filter_unknown_keys(payload, cls)

        # also filter the nested commit payload
        if "commit" in filtered_payload and isinstance(filtered_payload["commit"], dict):
            commit_data = filtered_payload["commit"]
            filtered_commit_data = filter_unknown_keys(commit_data, CommitDetail)

            if "author" in filtered_commit_data and isinstance(
                filtered_commit_data["author"], dict
            ):
                author_data = filtered_commit_data["author"]
                filtered_author_data = filter_unknown_keys(author_data, CommitAuthor)
                filtered_commit_data["author"] = filtered_author_data

            filtered_payload["commit"] = filtered_commit_data

        return cls(**filtered_payload)
