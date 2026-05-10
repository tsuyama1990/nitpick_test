class DashboardError(Exception):
    """Unified error raised by the Dashboard Controller for UI consumption."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
