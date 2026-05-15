
from pytest_mock import MockerFixture

from src.app import main


def test_main(mocker: MockerFixture) -> None:
    mock_logger = mocker.patch("src.app.logger")
    main()
    mock_logger.info.assert_called_once_with("Hello from app!")
