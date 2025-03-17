from questrya.factory import create_app

app = create_app()

# Ensure tasks are registered
from questrya import tasks  # noqa
