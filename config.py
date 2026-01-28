"""Konfiguration der Ratsinformationssysteme im Münsterland."""

from enum import Enum
from dataclasses import dataclass


class SystemTyp(Enum):
    SESSIONNET = "sessionnet"
    RATSINFO = "ratsinfo"
    NICHT_UNTERSTUETZT = "nicht_unterstuetzt"


@dataclass
class Stadt:
    name: str
    einwohner: int
    url: str
    typ: SystemTyp


def erkenne_systemtyp(url: str) -> SystemTyp:
    """Erkennt den Systemtyp anhand der URL."""
    if "si0046" in url:
        return SystemTyp.SESSIONNET
    if "ratsinfomanagement.net" in url:
        return SystemTyp.RATSINFO
    return SystemTyp.NICHT_UNTERSTUETZT


# Alle Städte aus der HTML-Datei
STAEDTE = [
    Stadt("Kreis Steinfurt", 462800, "https://sessionnet.owl-it.de/kreis_steinfurt/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Kreis Borken", 380112, "https://secure.kreis-borken.de/BI/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Stadt Münster", 325000, "https://www.stadt-muenster.de/sessionnet/sessionnetbi/si0046.php", SystemTyp.SESSIONNET),
    Stadt("Kreis Warendorf", 182500, "https://www.kreis-warendorf.de/w1/sessionnet/bi/si0046.php", SystemTyp.SESSIONNET),
    Stadt("Kreis Coesfeld", 113000, "https://www.kreis-coesfeld.de/sessionnet/sessionnetbi/si0046.php", SystemTyp.SESSIONNET),
    Stadt("Rheine", 76948, "https://www.rheine-buergerinfo.de/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Bocholt", 71074, "https://ratsinfo.bocholt.de/", SystemTyp.NICHT_UNTERSTUETZT),
    Stadt("Ahlen", 52627, "https://www.ahlen.sitzung-online.de/public/", SystemTyp.NICHT_UNTERSTUETZT),
    Stadt("Ibbenbüren", 51888, "https://ibbenbueren.ratsinfomanagement.net/termine", SystemTyp.RATSINFO),
    Stadt("Gronau", 49031, "https://gronau.ratsinfomanagement.net/termine", SystemTyp.RATSINFO),
    Stadt("Dülmen", 46877, "https://sessionweb.duelmen.de/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Greven", 37700, "https://greven.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Warendorf", 37146, "https://sessionnet.owl-it.de/warendorf/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Beckum", 36737, "https://sessionnet.owl-it.de/beckum/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Coesfeld", 36382, "https://buergerinfo.coesfeld.de/si0046.php", SystemTyp.SESSIONNET),
    Stadt("Emsdetten", 35927, "https://emsdetten.ratsinfomanagement.net/termine", SystemTyp.RATSINFO),
    Stadt("Lüdinghausen", 24847, "https://www.stadt-luedinghausen.de/sessionnet/buergerinfo/si0046.php", SystemTyp.SESSIONNET),
    Stadt("Vreden", 22758, "https://vreden.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Lengerich", 22527, "https://lengerich.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Senden", 20495, "https://sessionnet.owl-it.de/gemeinde-senden/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Telgte", 19982, "https://sessionnet.owl-it.de/telgte/BI/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Ochtrup", 19893, "", SystemTyp.NICHT_UNTERSTUETZT),  # System defekt
    Stadt("Nottuln", 19672, "https://www.nottuln.de/sessionnet/sessionnetbi/si0046.php", SystemTyp.SESSIONNET),
    Stadt("Drensteinfurt", 15607, "https://sessionnet.owl-it.de/drensteinfurt/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Ascheberg", 15602, "https://sessionnet.owl-it.de/ascheberg/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Sassenberg", 14258, "https://session.sassenberg.de/sessionnet/bi/si0046.php", SystemTyp.SESSIONNET),
    Stadt("Heek", 8628, "https://heek.ratsinfomanagement.net/termine", SystemTyp.RATSINFO),
    Stadt("Wettringen", 8261, "https://sessionnet.owl-it.de/kreis_steinfurt/wettringen/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Horstmar", 6849, "https://horstmar.ratsinfomanagement.net/termine", SystemTyp.RATSINFO),
    Stadt("Ladbergen", 6821, "https://www.ladbergen.de/rathaus/ratsinfosystem/termine/", SystemTyp.NICHT_UNTERSTUETZT),
    Stadt("Schöppingen", 6623, "https://schoeppingen.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Metelen", 6417, "https://metelen.ratsinfomanagement.net/startseite", SystemTyp.RATSINFO),
    Stadt("Beelen", 6159, "https://sessionnet.owl-it.de/beelen/bi/si0046.asp", SystemTyp.SESSIONNET),
]


def get_staedte_nach_typ(typ: SystemTyp) -> list[Stadt]:
    """Gibt alle Städte eines bestimmten Systemtyps zurück."""
    return [s for s in STAEDTE if s.typ == typ]


def get_unterstuetzte_staedte() -> list[Stadt]:
    """Gibt alle Städte mit unterstütztem Systemtyp zurück."""
    return [s for s in STAEDTE if s.typ != SystemTyp.NICHT_UNTERSTUETZT]
