from __future__ import annotations

from pathlib import Path


MODEL_ID = "Helsinki-NLP/opus-mt-en-ro"
TARGET_DIR = Path("assets/models/opus-mt-en-ro")


def main() -> int:
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("huggingface-hub is not installed. Run: pip install -r requirements.txt")
        return 1

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {MODEL_ID} to {TARGET_DIR.resolve()}")
    snapshot_download(
        repo_id=MODEL_ID,
        local_dir=TARGET_DIR,
        local_dir_use_symlinks=False,
        ignore_patterns=["*.h5", "*.ot", "*.msgpack"],
    )
    print("Model download complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
