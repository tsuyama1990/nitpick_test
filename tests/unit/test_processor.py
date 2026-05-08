from src.domain_models.github import CommitDetail
from src.transformation.processor import process_commits_per_committer, process_commits_per_day


def test_process_commits_per_day_empty() -> None:
    df = process_commits_per_day([])
    assert df.height == 0
    assert "date" in df.columns
    assert "commit_count" in df.columns


def test_process_commits_per_committer_empty() -> None:
    df = process_commits_per_committer([])
    assert df.height == 0
    assert "author_name" in df.columns
    assert "commit_count" in df.columns


def test_process_commits_per_day() -> None:
    data1: dict[str, object] = {
        "sha": "1",
        "commit": {
            "message": "m1",
            "author": {"name": "a1", "date": "2023-01-01T10:00:00Z"},
        },
    }
    data2: dict[str, object] = {
        "sha": "2",
        "commit": {
            "message": "m2",
            "author": {"name": "a2", "date": "2023-01-01T11:00:00Z"},
        },
    }
    data3: dict[str, object] = {
        "sha": "3",
        "commit": {
            "message": "m3",
            "author": {"name": "a1", "date": "2023-01-02T10:00:00Z"},
        },
    }
    commits = [
        CommitDetail(**data1),  # type: ignore[arg-type]
        CommitDetail(**data2),  # type: ignore[arg-type]
        CommitDetail(**data3),  # type: ignore[arg-type]
    ]

    df = process_commits_per_day(commits)

    assert df.height == 2
    # It should be sorted descending
    assert df["date"][0].strftime("%Y-%m-%d") == "2023-01-02"
    assert df["commit_count"][0] == 1
    assert df["date"][1].strftime("%Y-%m-%d") == "2023-01-01"
    assert df["commit_count"][1] == 2


def test_process_commits_per_committer() -> None:
    data1: dict[str, object] = {
        "sha": "1",
        "commit": {
            "message": "m1",
            "author": {"name": "user1", "date": "2023-01-01T10:00:00Z"},
        },
    }
    data2: dict[str, object] = {
        "sha": "2",
        "commit": {
            "message": "m2",
            "author": {"name": "user1", "date": "2023-01-01T11:00:00Z"},
        },
    }
    data3: dict[str, object] = {
        "sha": "3",
        "commit": {
            "message": "m3",
            "author": {"name": "user2", "date": "2023-01-02T10:00:00Z"},
        },
    }
    data4: dict[str, object] = {
        "sha": "4",
        "commit": {
            "message": "m4",
            "author": {"name": "user3", "date": "2023-01-02T10:00:00Z"},
        },
    }
    data5: dict[str, object] = {
        "sha": "5",
        "commit": {
            "message": "m5",
            "author": {"name": "user4", "date": "2023-01-02T10:00:00Z"},
        },
    }
    data6: dict[str, object] = {
        "sha": "6",
        "commit": {
            "message": "m6",
            "author": {"name": "user5", "date": "2023-01-02T10:00:00Z"},
        },
    }
    data7: dict[str, object] = {
        "sha": "7",
        "commit": {
            "message": "m7",
            "author": {"name": "user6", "date": "2023-01-02T10:00:00Z"},
        },
    }
    commits = [
        CommitDetail(**data1),  # type: ignore[arg-type]
        CommitDetail(**data2),  # type: ignore[arg-type]
        CommitDetail(**data3),  # type: ignore[arg-type]
        CommitDetail(**data4),  # type: ignore[arg-type]
        CommitDetail(**data5),  # type: ignore[arg-type]
        CommitDetail(**data6),  # type: ignore[arg-type]
        CommitDetail(**data7),  # type: ignore[arg-type]
    ]

    df = process_commits_per_committer(commits)

    # Should only return top 5
    assert df.height == 5
    # user1 should have 2 commits and be first
    assert df["author_name"][0] == "user1"
    assert df["commit_count"][0] == 2
