import os

from dotenv import load_dotenv

# dotenv config
load_dotenv()

environ = os.getenv("DJANGO_SETTINGS", "local")

if environ == "local":
    from .local import *

elif environ == "dev":
    from .dev import *

else:
    from .production import *
