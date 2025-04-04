class DomainException(Exception):
    """Custom exception class for domain-specific errors."""

    def __init__(self, message: str = ''):
        self.message = message
        super().__init__(self.message)
