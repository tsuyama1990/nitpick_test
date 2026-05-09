from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class RepoInfo(BaseModel):
    """
    Model for GitHub Repository Information.
    Documentation: https://docs.github.com/en/rest/repos/repos
    Maps:
      - stargazers_count -> Stars
      - forks_count -> Forks
      - open_issues_count -> Open Issues
    """

    stargazers_count: int
    forks_count: int
    open_issues_count: int

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        # Strip unknown keys to forbid extra fields securely
        allowed_keys = set(cls.model_fields.keys())
        return {k: v for k, v in data.items() if k in allowed_keys}

    @model_validator(mode="before")
    @classmethod
    def validate_and_strip(cls, data: Any) -> Any:
        return cls._strip_extra(data)


class CommitInfo(BaseModel):
    """
    Model for GitHub Commit Information.
    Documentation: https://docs.github.com/en/rest/commits/commits
    Maps:
      - sha -> commit sha
      - commit.author.name -> committer name
      - commit.author.date -> commit date
    """

    sha: str
    author_name: str
    date: str

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def _extract_and_strip(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # Extract nested fields
        res: dict[str, Any] = {}
        if "sha" in data:
            res["sha"] = data["sha"]

        commit_data = data.get("commit")
        if isinstance(commit_data, dict):
            author_data = commit_data.get("author")
            if isinstance(author_data, dict):
                if "name" in author_data:
                    res["author_name"] = author_data["name"]
                if "date" in author_data:
                    res["date"] = author_data["date"]

        allowed_keys = set(cls.model_fields.keys())
        return {k: v for k, v in res.items() if k in allowed_keys}

    @model_validator(mode="before")
    @classmethod
    def validate_and_extract(cls, data: Any) -> Any:
        return cls._extract_and_strip(data)
