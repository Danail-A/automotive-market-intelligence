import csv
import re
import os
import shutil

from pathlib import Path

import psycopg2
from psycopg2 import sql

## Configs

PROJECT_DIR = Path('.')

PROCESSED_DIR = "empty for now"
FAILED_DIR = "empty for now"

print({PROJECT_DIR})