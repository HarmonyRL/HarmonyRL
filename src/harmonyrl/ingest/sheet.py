"""Reading a lead sheet from a MusicXML or MIDI file."""

from pathlib import Path

from harmonyrl.schema import Key

from .common import SheetImport
from .midi import lead_sheet_from_midi
from .musicxml import lead_sheet_from_musicxml


def read_lead_sheet(
	path: Path,
	*,
	part: int | None = None,
	key: Key | None = None,
) -> SheetImport:
	"""Read the lead sheet of a score, MIDI, or monophonic recording, chosen by file suffix."""
	suffix = path.suffix.lower()

	if suffix in (".musicxml", ".mxl", ".xml"):
		return lead_sheet_from_musicxml(path, part=part, key=key)
	if suffix in (".mid", ".midi"):
		return lead_sheet_from_midi(path, track=part, key=key)

	raise ValueError(f"unsupported file type {suffix!r}")
