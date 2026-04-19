#!/usr/bin/env python3
"""Curate the committed workshop sample set.

Reproducible: same seed -> same 50 files. Run this once to (re)generate
`datasets/ppe/images/{train,test}/`. The workshop notebooks
read from those committed folders -- no download is needed at workshop time.

If the full Construction-PPE source isn't on disk yet, this script downloads
it into `datasets/_source/construction-ppe/` (git-ignored), then samples from it.

Usage:
    python scripts/curate_workshop_samples.py
"""
from __future__ import annotations

import random
import shutil
import subprocess
import sys
from pathlib import Path

SEED = 51
NUM_TRAIN = 40
NUM_TEST = 10
DATASET_URL = "https://github.com/ultralytics/assets/releases/download/v0.0.0/construction-ppe.zip"
SOURCE_ROOT = Path("datasets/_source/construction-ppe")
SOURCE_DIR = SOURCE_ROOT / "images" / "train"
TARGET_ROOT = Path("datasets/ppe/images")

IMG_EXTS = {".jpg", ".jpeg", ".png"}


def ensure_dataset() -> None:
    if SOURCE_DIR.is_dir() and any(SOURCE_DIR.iterdir()):
        return
    print(f"Downloading {DATASET_URL} ...")
    SOURCE_ROOT.mkdir(parents=True, exist_ok=True)
    zip_path = Path("/tmp/construction-ppe.zip")
    subprocess.check_call(["wget", "-q", "-O", str(zip_path), DATASET_URL])
    subprocess.check_call(["unzip", "-q", "-o", str(zip_path), "-d", str(SOURCE_ROOT)])
    zip_path.unlink(missing_ok=True)


def main() -> int:
    ensure_dataset()
    images = sorted(p for p in SOURCE_DIR.iterdir() if p.suffix.lower() in IMG_EXTS)
    if len(images) < NUM_TRAIN + NUM_TEST:
        print(f"Not enough source images: {len(images)}", file=sys.stderr)
        return 1

    rng = random.Random(SEED)
    rng.shuffle(images)
    picked = images[: NUM_TRAIN + NUM_TEST]
    splits = {"train": picked[:NUM_TRAIN], "test": picked[NUM_TRAIN:]}

    for split_name, files in splits.items():
        out_dir = TARGET_ROOT / split_name
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True)
        for i, src in enumerate(files, start=1):
            dst = out_dir / f"{split_name}_{i:02d}.jpg"
            shutil.copy2(src, dst)
        print(f"Wrote {len(files)} images -> {out_dir}")

    # Keep an empty val split around so Ultralytics YAML stays valid.
    val_dir = TARGET_ROOT / "val"
    val_dir.mkdir(parents=True, exist_ok=True)
    (val_dir / ".gitkeep").touch()

    return 0


if __name__ == "__main__":
    sys.exit(main())
