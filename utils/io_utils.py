import os, json
from typing import Iterable

def ensure_dirs(paths: Iterable[str]):
    for p in paths:
        os.makedirs(p, exist_ok=True)

def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)