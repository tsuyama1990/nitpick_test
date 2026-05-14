import pytest
from pydantic import ValidationError

from src.domain_models.manifest import Manifest


def test_manifest_valid() -> None:
    manifest = Manifest(name="app", version="0.1.0", description="A test app")
    assert manifest.name == "app"
    assert manifest.version == "0.1.0"
    assert manifest.description == "A test app"


def test_manifest_invalid_extra() -> None:
    with pytest.raises(ValidationError):
        Manifest(name="app", version="0.1.0", description="A test app", extra_field="invalid")  # type: ignore[call-arg]


def test_manifest_missing_field() -> None:
    with pytest.raises(ValidationError):
        Manifest(name="app", version="0.1.0")  # type: ignore[call-arg]
