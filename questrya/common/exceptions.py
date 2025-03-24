class DomainException(Exception):
    """Custom exception class for domain-specific errors."""

    def __init__(self, message: str = ''):
        super().__init__(self.message)
