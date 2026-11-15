"""Create web-ready hero media from the user-supplied 展示视频.mp4.

The original stays in the source folder. This script only changes encoding and size.
Usage: python scripts/prepare_hero.py "C:/path/to/展示视频.mp4"
Requires ffmpeg in PATH or the imageio-ffmpeg package.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def ffmpeg_executable() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, AttributeError) as exc:
        raise RuntimeError("ffmpeg or imageio-ffmpeg is required") from exc


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    destination = Path(__file__).resolve().parents[1] / "public" / "media" / "hero"
    destination.mkdir(parents=True, exist_ok=True)
    ffmpeg = ffmpeg_executable()

    run(
        [
            ffmpeg,
            "-y",
            "-ss",
            "7",
            "-i",
            str(source),
            "-frames:v",
            "1",
            "-vf",
            "scale=1280:-2",
            "-c:v",
            "libwebp",
            "-quality",
            "78",
            str(destination / "poster.webp"),
        ]
    )
    run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(source),
            "-vf",
            "scale=1280:-2,fps=24",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "27",
            "-pix_fmt",
            "yuv420p",
            "-an",
            "-movflags",
            "+faststart",
            str(destination / "hero.mp4"),
        ]
    )
    for filename in ("hero.mp4", "poster.webp"):
        file = destination / filename
        print(f"{file}: {file.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
