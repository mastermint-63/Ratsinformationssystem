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
    Stadt("Ahaus", 40176, "https://sessionnet.owl-it.de/stadt-ahaus/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Ahlen", 52627, "https://www.ahlen.sitzung-online.de/public/", SystemTyp.NICHT_UNTERSTUETZT),
    Stadt("Altenberge", 10415, "https://altenberge.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Ascheberg", 15602, "https://sessionnet.owl-it.de/ascheberg/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Beckum", 36737, "https://sessionnet.owl-it.de/beckum/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Beelen", 6159, "https://sessionnet.owl-it.de/beelen/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Billerbeck", 11945, "https://ratsinfo.billerbeck.de/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Bocholt", 71074, "https://ratsinfo.bocholt.de/", SystemTyp.NICHT_UNTERSTUETZT),
    Stadt("Borken", 43035, "https://bi.borken.de/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Coesfeld", 36382, "https://buergerinfo.coesfeld.de/si0046.php", SystemTyp.SESSIONNET),
    Stadt("Drensteinfurt", 15607, "https://sessionnet.owl-it.de/drensteinfurt/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Dülmen", 46877, "https://sessionweb.duelmen.de/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Emsdetten", 35927, "https://emsdetten.ratsinfomanagement.net/termine", SystemTyp.RATSINFO),
    Stadt("Ennigerloh", 20000, "", SystemTyp.NICHT_UNTERSTUETZT),
    Stadt("Everswinkel", 9825, "https://www.everswinkel.de/sessionnet/www/buergerinfo/si0046.php", SystemTyp.SESSIONNET),
    Stadt("Gescher", 17433, "https://gescher.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Greven", 37700, "https://greven.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Gronau", 49031, "https://gronau.ratsinfomanagement.net/termine", SystemTyp.RATSINFO),
    Stadt("Havixbeck", 12357, "https://www.ris-havixbeck.de/bi/si0046.php", SystemTyp.SESSIONNET),
    Stadt("Heek", 8628, "https://heek.ratsinfomanagement.net/termine", SystemTyp.RATSINFO),
    Stadt("Heiden", 8704, "https://heiden.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Hörstel", 20093, "https://hoerstel.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Hopsten", 7007, "https://hopsten.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Horstmar", 6849, "https://horstmar.ratsinfomanagement.net/termine", SystemTyp.RATSINFO),
    Stadt("Ibbenbüren", 51888, "https://ibbenbueren.ratsinfomanagement.net/termine", SystemTyp.RATSINFO),
    Stadt("Isselburg", 11251, "https://isselburg.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Ladbergen", 6821, "https://ladbergen.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Laer", 6805, "https://laer.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Legden", 7511, "https://legden.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Lengerich", 22527, "https://lengerich.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Lienen", 8783, "https://lienen.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Lotte", 14314, "https://lotte.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Lüdinghausen", 24847, "https://www.stadt-luedinghausen.de/sessionnet/buergerinfo/si0046.php", SystemTyp.SESSIONNET),
    Stadt("Metelen", 6417, "https://metelen.ratsinfomanagement.net/startseite", SystemTyp.RATSINFO),
    Stadt("Mettingen", 12000, "https://mettingen.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Neuenkirchen", 14072, "https://neuenkirchen.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Nordkirchen", 10762, "https://sessionnet.owl-it.de/nordkirchen/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Nordwalde", 9807, "https://nordwalde.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Nottuln", 19672, "https://www.nottuln.de/sessionnet/sessionnetbi/si0046.php", SystemTyp.SESSIONNET),
    Stadt("Ochtrup", 19893, "", SystemTyp.NICHT_UNTERSTUETZT),
    Stadt("Oelde", 29500, "", SystemTyp.NICHT_UNTERSTUETZT),
    Stadt("Olfen", 13175, "https://ratsinfo.olpe.de", SystemTyp.RATSINFO),
    Stadt("Ostbevern", 11000, "https://www.ostbevern.de/sessionnet/sessionnetbi/si0046.php", SystemTyp.SESSIONNET),
    Stadt("Raesfeld", 11709, "https://raesfeld.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Recke", 11370, "https://recke.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Reken", 15109, "https://reken.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Rheine", 76948, "https://www.rheine-buergerinfo.de/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Rhede", 19674, "", SystemTyp.NICHT_UNTERSTUETZT),
    Stadt("Rosendahl", 11249, "https://sessionnet.owl-it.de/rosendahl/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Saerbeck", 7128, "https://saerbeck.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Sassenberg", 14258, "https://session.sassenberg.de/sessionnet/bi/si0046.php", SystemTyp.SESSIONNET),
    Stadt("Schöppingen", 6623, "https://schoeppingen.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Senden", 20495, "https://sessionnet.owl-it.de/gemeinde-senden/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Sendenhorst", 14148, "", SystemTyp.NICHT_UNTERSTUETZT),
    Stadt("Stadtlohn", 20946, "https://stadtlohn.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Steinfurt", 35102, "https://steinfurt.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Südlohn", 9861, "", SystemTyp.NICHT_UNTERSTUETZT),
    Stadt("Tecklenburg", 9288, "https://tecklenburg.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Telgte", 19982, "https://sessionnet.owl-it.de/telgte/BI/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Velen", 12678, "https://velen.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Vreden", 22758, "https://vreden.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Wadersloh", 13000, "https://sessionnet.owl-it.de/wadersloh/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Warendorf", 37146, "https://sessionnet.owl-it.de/warendorf/bi/si0046.asp", SystemTyp.SESSIONNET),
    Stadt("Westerkappeln", 11485, "https://westerkappeln.ratsinfomanagement.net/", SystemTyp.RATSINFO),
    Stadt("Wettringen", 8261, "https://sessionnet.owl-it.de/kreis_steinfurt/wettringen/bi/si0046.asp", SystemTyp.SESSIONNET),
]


def get_staedte_nach_typ(typ: SystemTyp) -> list[Stadt]:
    """Gibt alle Städte eines bestimmten Systemtyps zurück."""
    return [s for s in STAEDTE if s.typ == typ]


def get_unterstuetzte_staedte() -> list[Stadt]:
    """Gibt alle Städte mit unterstütztem Systemtyp zurück."""
    return [s for s in STAEDTE if s.typ != SystemTyp.NICHT_UNTERSTUETZT]
