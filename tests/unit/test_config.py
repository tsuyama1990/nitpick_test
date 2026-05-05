
import pytest
from pydantic import ValidationError

from src.config import Settings


def test_config_extra_forbid() -> None:
    """Test that pydantic_settings rejects unknown variables."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(UNKNOWN_VARIABLE="test")  # type: ignore[call-arg]

    assert "Extra inputs are not permitted" in str(exc_info.value)
