# HarmonyRL

English | [한국어](https://github.com/HarmonyRL/HarmonyRL/blob/main/README.ko.md)

Chord progressions for a melody. HarmonyRL reads a lead sheet from MusicXML or MIDI, writes
chords under the melody, and can redraw only the bars you choose while keeping the rest.

The models are transformer chord policies pretrained on human accompaniments, then fine-tuned
with reinforcement learning. Pick the one whose sound you want:

| Model | Style |
|---|---|
| [`CloudHolic/harmonyrl-chromatic`](https://huggingface.co/CloudHolic/harmonyrl-chromatic) | rich reharmonization, many chords from outside the key |
| [`CloudHolic/harmonyrl-smooth`](https://huggingface.co/CloudHolic/harmonyrl-smooth) | consonant, resolving progressions |
| [`CloudHolic/harmonyrl-base`](https://huggingface.co/CloudHolic/harmonyrl-base) | close to the training data |

Each model card describes its training and evaluation. All 3 are in the
[HarmonyRL collection](https://huggingface.co/collections/CloudHolic/harmonyrl).

## Installation

Python 3.12 or later.

```sh
pip install harmonyrl
```

A GPU is used when PyTorch finds one; the models also run on the CPU.

## Usage

```python
from pathlib import Path

from harmonyrl import HarmonyRL
from harmonyrl.ingest import read_lead_sheet
from harmonyrl.render import write_lead_sheet

model = HarmonyRL.from_pretrained("CloudHolic/harmonyrl-chromatic")
sheet = read_lead_sheet(Path("melody.musicxml")).sheet

# Up to 3 different harmonizations of the whole lead sheet
candidates = model.harmonize_sheet(sheet, candidates=3, seed=0)
write_lead_sheet(candidates[0], Path("harmonized.musicxml"))

# Redraw bars 4 and 5 (counted from 0) and keep every other chord
redrawn = model.harmonize_sheet(candidates[0], bars=range(4, 6), candidates=2)
write_lead_sheet(redrawn[0], Path("redrawn.mid"))
```

A lead sheet that already has chord symbols works the same way: read it, then pass `bars=` to
fill only those bars. Without `bars=`, every chord is written anew.

### Generation settings

Each model ships its defaults in `generation_config.json`. Keyword arguments override them for
one call, and `model.generation_config` holds them for later calls.

| Setting | Meaning |
|---|---|
| `temperature` | Sampling temperature. Lower is safer, higher is more varied |
| `pool` | When refilling bars between kept chords, drafts drawn per candidate; the chords after the bars weigh which drafts are returned |
| `max_duplicates` | Repeated draws allowed before the search for distinct candidates stops |

```python
model.harmonize_sheet(sheet, candidates=4, temperature=0.8)
```

The candidates always differ, so a call can return fewer than `candidates` (at most 16): each
draw that repeats a candidate already found counts toward `max_duplicates` (1 by default), and
the search stops there with what it has. A few bars between kept chords often leave few distinct
progressions, so raise `max_duplicates` to look longer. `seed` makes a call reproducible on the
same device.

### Melodies and chords as data

`HarmonyRL.harmonize` takes 1 `Melody` of up to 32 bars and returns a list of up to `candidates`
tuples of `ChordEvent`, the types in `harmonyrl.schema`. `harmonize_sheet` splits longer parts
into overlapping 32-bar windows (`overlap=`, 4 bars by default) and calls it per window.

## Files

| Format | Read | Write |
|---|---|---|
| MusicXML (`.musicxml`, `.xml`; `.mxl` read only) | melody and chord symbols | melody and chord symbols |
| MIDI (`.mid`, `.midi`) | melody | melody and chords |

- A score splits into parts at time signature changes and, in MusicXML, at rehearsal marks.
  Bar numbers in `bars=` count across all parts.
- `read_lead_sheet(path, part=...)` picks the part (MusicXML) or track (MIDI) that holds the
  melody; without it, the most melody-like one is chosen.
- The whole piece gets 1 key, from its key signature and notes. Pass `key=` when the key
  signature does not match the music.
- Chord symbols the model cannot spell exactly are approximated; their bars are listed in
  `SheetImport.approximated`. Repeats are read as written, not expanded, and reported in
  `SheetImport.warnings`.
- To refine chords over several sessions, write MusicXML and read it back. MIDI output keeps
  the chords only as notes.

## Limitations

- One call to `harmonize` covers up to 32 bars, and the windows of `harmonize_sheet` do not see
  each other beyond their overlap, so song-level structure such as repeated verses is not
  modeled.
- A new chord can sound abrupt against the kept chords around it. Redraw, or ask for more
  candidates.
- Each harmonization is a sample: outputs differ from draw to draw unless `seed` is set.

## License

The code is MIT licensed. The model weights are CC BY-NC-SA 3.0, following their training data:
[Hooktheory](https://www.hooktheory.com) melodies and chords as released with
[Sheet Sage](https://github.com/chrisdonahue/sheetsage) (Donahue, Thickstun, Liang,
"[Melody Transcription via Generative Pre-Training](https://arxiv.org/abs/2212.01884)",
ISMIR 2022).
