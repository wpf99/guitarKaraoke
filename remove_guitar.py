#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            + " ".join(cmd)
            + "\n\nSTDOUT:\n"
            + result.stdout
            + "\n\nSTDERR:\n"
            + result.stderr
        )


def output_codec_args(output_path: Path) -> list[str]:
    ext = output_path.suffix.lower()
    if ext == ".mp3":
        return ["-c:a", "libmp3lame", "-q:a", "2"]
    if ext in {".m4a", ".mp4"}:
        return ["-c:a", "aac", "-b:a", "192k"]
    return ["-c:a", "pcm_s16le"]


def remove_guitar(input_path: Path, output_path: Path, model: str) -> None:
    if not input_path.exists():
        raise FileNotFoundError(str(input_path))

    work_dir = output_path.parent
    work_dir.mkdir(parents=True, exist_ok=True)

    # Verify demucs/ffmpeg are available.
    run(["demucs", "-h"])
    run(["ffmpeg", "-version"])

    # Run demucs to split stems.
    run(
        [
            "demucs",
            "-n",
            model,
            "--out",
            str(work_dir),
            str(input_path),
        ]
    )

    # Demucs output path: <out>/<model>/<trackname>/
    track_dir = work_dir / model / input_path.stem
    drums = track_dir / "drums.wav"
    bass = track_dir / "bass.wav"
    vocals = track_dir / "vocals.wav"

    if not (drums.exists() and bass.exists() and vocals.exists()):
        raise RuntimeError(f"Missing expected stems in {track_dir}")

    # Mix drums + bass + vocals to approximate "no guitar".
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(drums),
        "-i",
        str(bass),
        "-i",
        str(vocals),
        "-filter_complex",
        "amix=inputs=3:duration=longest:dropout_transition=2",
    ]
    ffmpeg_cmd += output_codec_args(output_path)
    ffmpeg_cmd.append(str(output_path))
    run(ffmpeg_cmd)

    # Cleanup demucs stems to keep the workspace tidy.
    shutil.rmtree(work_dir / model, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove (approx) guitar by mixing non-guitar stems."
    )
    parser.add_argument("input", help="Path to input audio file")
    parser.add_argument("output", help="Path to output audio file")
    parser.add_argument(
        "--model",
        default="htdemucs",
        help="Demucs model name (default: htdemucs)",
    )
    args = parser.parse_args()

    remove_guitar(Path(args.input), Path(args.output), args.model)


if __name__ == "__main__":
    main()
