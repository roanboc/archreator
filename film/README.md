# The film

_[← Repository README](../README.md)_

*ArChreator in two minutes*: how an idea becomes a confirmed picture of a
business and then tested software, and where everything is kept in a
repository. It plays on [the public site](../site/index.html), from
`site/assets/film/`.

The film is drawn from source. Nothing in it was recorded or edited by hand,
so when the method changes the film is made again.

| File | Holds |
| ---- | ----- |
| [`script.json`](./script.json) | The words: every line is spoken, shown as a caption and timed against. The voice settings, and the few words respelled for the voice only |
| [`film.html`](./film.html), [`film.css`](./film.css), [`film.js`](./film.js) | The picture, as a function of time. It uses the site's stylesheet and the site's own drawing of the loop, [`site/loop.js`](../site/loop.js), so the film and the page cannot disagree about it |
| [`timeline.js`](./timeline.js) | When each line is said. Written by the voice tool, committed, never edited by hand |
| [`tools/voice.py`](./tools/voice.py) | Voices the script, writes the timeline, the narration and the captions |
| [`tools/render.js`](./tools/render.js) | Draws every frame, lays the narration under it, writes the film and its poster |

## Making it again

```bash
uv run film/tools/voice.py     # a changed line is voiced again; the timeline and captions are rewritten
node film/tools/render.js      # 2,861 frames, then the film: about two minutes on four cores
```

The first needs [uv](https://docs.astral.sh/uv/), which fetches the voice
tool's own dependencies, and on its first run downloads the voice model
(about 350 MB) into `film/build/models/`. The second needs Node with
Playwright and Chromium, and `ffmpeg` on the `PATH`. Everything under
`film/build/` is rebuilt and ignored by git.

To look at one moment without rendering, serve the repository and open
`film/film.html?t=42`, or shoot a frame: `node film/tools/render.js --still 42`.

## Changing what it says

Edit `script.json`, then run both tools. A line's length sets how long its
picture stays, so the picture follows the words without retiming. Where a
picture arrives part-way through a line, `film.js` says how many seconds in:
check those moments after a line is reworded.

**Hear a name before recording it.** The voice reads by spelling, and reads
*ArChreator* as "ar-kreeter". The script respells it for the voice only, as
*Arcreator*, which it says as "ar-kree-ay-ter"; the captions keep the name as
it is written. `uv run film/tools/voice.py --sounds` prints the sounds the
voice will make for every respelled word.

## The voice

The narration is a synthetic voice, and the film and the page both say so:
[Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M), under the Apache
License 2.0, run through
[kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx), with the
`af_heart` voice at 0.95 speed. The model is downloaded when the film is
made and is not part of this repository.
