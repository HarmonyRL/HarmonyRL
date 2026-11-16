"""Writing lead sheets to MusicXML and MIDI files."""

from .score import DEFAULT_TITLE
from .sheet import write_lead_sheet

__all__ = [
	"DEFAULT_TITLE",
	"write_lead_sheet",
]
