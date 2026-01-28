import os
from dotenv import load_dotenv

# Application configuration
LOG_DIR = os.path.join(os.path.expanduser('~'), '.azor')
OUTPUT_DIR = os.path.join(os.path.expanduser('~'), '.azor', 'output')
CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.azor', 'config')
WAL_FILE = os.path.join(LOG_DIR, 'azor-wal.json')

os.makedirs(LOG_DIR, exist_ok=True)
load_dotenv()

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)