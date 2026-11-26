# /// script
# requires-python = ">=3.10"
# dependencies = ["kokoro-onnx", "soundfile", "numpy"]
# ///
"""Voice the film's script, and write down when each line is said.

    uv run film/tools/voice.py            # voices what changed, rewrites the timeline
    uv run film/tools/voice.py --sounds   # prints how the voice will say each respelled word

Reads `film/script.json`. Writes one WAV per line under `film/build/vo/`, the
whole narration as `film/build/narration.wav`, the timeline the picture is
drawn against as `film/timeline.js`, and the captions as
`site/assets/film/archreator.en.vtt`.

**One timeline, three readers.** The picture, the sound and the captions all
come from the lengths measured here, so they cannot drift apart. The timeline
is committed: the film page plays against it without the voice model.

**The voice is synthetic, and the film says so.** Kokoro-82M (Apache-2.0),
run through kokoro-onnx, with the `af_heart` voice at 0.95 speed. The model
is fetched once into `film/build/models/` and is never committed.

A line is voiced again only when its words, its respelling or the voice
settings change.
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

FILM = Path(__file__).resolve().parents[1]
REPO = FILM.parent
BUILD = FILM / "build"
MODELS = BUILD / "models"
RELEASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
MODEL_FILES = ("kokoro-v1.0.onnx", "voices-v1.0.bin")
CAPTIONS = REPO / "site" / "assets" / "film" / "archreator.en.vtt"


def models() -> None:
    MODELS.mkdir(parents=True, exist_ok=True)
    for name in MODEL_FILES:
        target = MODELS / name
        if target.is_file() and target.stat().st_size:
            continue
        print(f"fetching {name} ...", flush=True)
        urllib.request.urlretrieve(f"{RELEASE}/{name}", target)


def spoken(text: str, say: list[list[str]]) -> str:
    """The line as the voice reads it: a respelled word, never a changed one."""
    for pattern, replacement in say:
        text = re.sub(pattern, replacement, text)
    return text


def clock(seconds: float) -> str:
    whole = int(seconds)
    return f"{whole // 3600:02d}:{whole % 3600 // 60:02d}:{whole % 60:02d}.{int(round((seconds - whole) * 1000)):03d}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Voice the film's script and write its timeline.")
    parser.add_argument("--sounds", action="store_true", help="print how the voice says each respelled word, and stop")
    args = parser.parse_args()

    script = json.loads((FILM / "script.json").read_text(encoding="utf-8"))
    voice, pace = script["voice"], script["pace"]
    models()

    if args.sounds:
        from kokoro_onnx.tokenizer import Tokenizer
        tokenizer = Tokenizer()
        for pattern, replacement in voice["say"]:
            print(f"{pattern!r:24} read as {replacement!r:14} -> {tokenizer.phonemize(replacement, voice['lang'])}")
        return 0

    import numpy as np
    import soundfile as sf
    from kokoro_onnx import Kokoro

    engine = None
    out = BUILD / "vo"
    out.mkdir(parents=True, exist_ok=True)
    rate = 24000
    lines, track, now = [], [], pace["lead_in"]
    track.append(np.zeros(int(pace["lead_in"] * rate), dtype=np.float32))
    scenes = {}
    for scene in script["scenes"]:
        scene_start = now if lines else 0.0
        for index, line in enumerate(scene["lines"]):
            key = f'{scene["id"]}/{line["id"]}'
            text = spoken(line.get("say") or line["text"], voice["say"])
            stamp = hashlib.sha256(json.dumps([text, voice["voice"], voice["lang"], voice["speed"]]).encode()).hexdigest()
            wav = out / f'{scene["id"]}-{line["id"]}.wav'
            mark = wav.with_suffix(".sha256")
            if not (wav.is_file() and mark.is_file() and mark.read_text() == stamp):
                if engine is None:
                    engine = Kokoro(str(MODELS / MODEL_FILES[0]), str(MODELS / MODEL_FILES[1]))
                samples, rate = engine.create(text, voice=voice["voice"], speed=voice["speed"], lang=voice["lang"])
                loud = np.where(np.abs(samples) > 0.01)[0]
                if len(loud):
                    samples = samples[max(0, loud[0] - 240):loud[-1] + 720]
                sf.write(str(wav), samples, rate)
                mark.write_text(stamp)
                print(f"voiced {key}: {len(samples) / rate:.2f}s", flush=True)
            samples, rate = sf.read(str(wav), dtype="float32")
            length = len(samples) / rate
            last = index == len(scene["lines"]) - 1
            gap = line.get("gap", pace["after_scene"] if last else pace["after_line"])
            lines.append({"key": key, "text": line["text"], "start": round(now, 3), "end": round(now + length, 3)})
            track += [samples, np.zeros(int(gap * rate), dtype=np.float32)]
            now += length + gap
        scenes[scene["id"]] = [round(scene_start, 3), round(now, 3)]
    track.append(np.zeros(int(pace["lead_out"] * rate), dtype=np.float32))
    duration = round(now + pace["lead_out"], 3)
    scenes[script["scenes"][-1]["id"]][1] = duration
    sf.write(str(BUILD / "narration.wav"), np.concatenate(track), rate)

    timeline = {"duration": duration, "scenes": scenes, "lines": lines}
    (FILM / "timeline.js").write_text(
        "// Written by film/tools/voice.py from the voiced lines. Do not edit by hand.\n"
        "window.FILM_TIMELINE = " + json.dumps(timeline, indent=1, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    CAPTIONS.parent.mkdir(parents=True, exist_ok=True)
    cues = ["WEBVTT", ""]
    for number, line in enumerate(lines, start=1):
        cues += [str(number), f'{clock(line["start"])} --> {clock(line["end"] + 0.15)}', line["text"], ""]
    CAPTIONS.write_text("\n".join(cues), encoding="utf-8")
    words = sum(len(line["text"].split()) for line in lines)
    print(f"{len(lines)} lines, {words} words, {duration:.1f}s. Timeline, narration and captions written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
