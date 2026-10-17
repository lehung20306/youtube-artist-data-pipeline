import json
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

DATA_DIR = os.path.join(PROJECT_ROOT, "data")


def save_to_json(data, filename, subfolder="raw"):
    os.makedirs(os.path.join(DATA_DIR, subfolder), exist_ok=True)

    filepath = os.path.join(DATA_DIR, subfolder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_from_json(filename, subfolder="raw"):
    filepath = os.path.join(DATA_DIR, subfolder, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)