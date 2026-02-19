# GuitarKaraoke

Remove (approximate) guitar from audio using Demucs, with a simple local web UI.

This project works by separating stems with Demucs and then remixing the non-guitar stems (drums + bass + vocals).

## Requirements

- Python 3.12 recommended
- `ffmpeg` available in PATH
- `pipx` for installing Demucs

## Quick Start (macOS/Linux)

```bash
cd /path/to/GuitarKaraoke
bash setup.sh
python3 web_app.py
```

Open `http://localhost:8000`.

## CLI Usage

```bash
python3 remove_guitar.py /path/to/input.mp3 /path/to/output.mp3
```

## How It Works

Demucs produces stems like `drums.wav`, `bass.wav`, `vocals.wav`, and `other.wav`.
We mix drums+bass+vocals to reduce guitar presence.

## Notes

- This is an approximation. If guitar is baked into vocals or other stems, it will remain.
- Large files can take a while to process, depending on CPU.

## License

Apache-2.0. See `LICENSE`.
