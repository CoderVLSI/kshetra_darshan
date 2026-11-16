"""Generate reviewed guide lines with the project's existing configured voice.

Credentials come only from ELEVENLABS_API_KEY; never ship API access in Godot.
Existing audio is retained. Only explicit manifest entries are generated.
"""
import argparse
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
VOICE_ID = "AfGQOwNTk8JotVVaad3o"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        print("NARRATION_BLOCKED: ELEVENLABS_API_KEY is not configured.")
        return 2
    manifest = json.loads((ROOT / "godot/data/narration_manifest.json").read_text(encoding="utf-8"))
    items = manifest["items"][:args.limit or None]
    for item in items:
        output = ROOT / "godot" / item["path"].removeprefix("res://")
        if output.exists() and output.stat().st_size > 1000:
            print("EXISTS", item["id"], flush=True)
            continue
        request = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128",
            data=json.dumps({"text": item["text"], "model_id": "eleven_multilingual_v2",
                             "voice_settings": {"stability": .55, "similarity_boost": .85}}).encode(),
            headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
            method="POST")
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                payload = response.read()
            if len(payload) < 1000:
                raise ValueError("Audio response was unexpectedly short")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(payload)
            print("GENERATED", item["id"], len(payload), flush=True)
        except urllib.error.HTTPError as error:
            print("NARRATION_BLOCKED: provider returned HTTP", error.code, flush=True)
            return 1
        except Exception as error:
            print("NARRATION_FAILED:", type(error).__name__, flush=True)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
