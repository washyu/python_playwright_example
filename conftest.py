import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def pytest_configure(config):
    """Configure pytest based on environment variables."""
    # Check if HEADED environment variable is set
    headed = os.getenv("HEADED", "").lower() in ("true", "1", "yes")

    if headed:
        # Add --headed to command line args if not already present
        if "--headed" not in sys.argv:
            sys.argv.append("--headed")

        # Set slowmo if HEADED is true
        slowmo = os.getenv("SLOWMO", "500")
        if "--slowmo" not in " ".join(sys.argv):
            sys.argv.append(f"--slowmo={slowmo}")
    else:
        # Headless mode - set slowmo to 0 unless explicitly set
        if "--slowmo" not in " ".join(sys.argv) and os.getenv("SLOWMO"):
            slowmo = os.getenv("SLOWMO", "0")
            sys.argv.append(f"--slowmo={slowmo}")
