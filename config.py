"""Konfiguration der Ratsinformationssysteme im Münsterland."""

from enum import Enum
from dataclasses import dataclass


class SystemTyp(Enum):
    SESSIONNET = "sessionnet"
    RATSINFO = "ratsinfo"
    ALLRIS = "allris"
    GREMIENINFO = "gremieninfo"
    NICHT_UNTERSTUETZT = "nicht_unterstuetzt"


class Kreis(Enum):
    """Kreise und kreisfreie Städte im Münsterland."""
    MUENSTER = "Münsterland"
    STEINFURT = "Kreis Steinfurt"
    BORKEN = "Kreis Borken"
    COESFELD = "Kreis Coesfeld"
    WARENDORF = "Kreis Warendorf"


@dataclass
class Stadt:
    name: str
    einwohner: int
    url: str
    typ: SystemTyp
    kreis: Kreis


def erkenne_systemtyp(url: str) -> SystemTyp:
    """Erkennt den Systemtyp anhand der URL."""
    if "si0046" in url:
        return SystemTyp.SESSIONNET
    if "ratsinfomanagement.net" in url:
        return SystemTyp.RATSINFO
    return SystemTyp.NICHT_UNTERSTUETZT


# Alle Städte aus der HTML-Datei
STAEDTE = [
    # Münsterland (überregionale Einheiten)
    Stadt("Stadt Münster", 325000, "https://www.stadt-muenster.de/sessionnet/sessionnetbi/si0046.php", SystemTyp.SESSIONNET, Kreis.MUENSTER),
    Stadt("LWL", 0, "https://allris.lwl.org/public/", SystemTyp.ALLRIS, Kreis.MUENSTER),
    Stadt("Kreis Steinfurt", 462800, "https://sessionnet.owl-it.de/kreis_steinfurt/bi/si0046.asp", SystemTyp.SESSIONNET, Kreis.MUENSTER),
    Stadt("Kreis Borken", 380112, "https://secure.kreis-borken.de/BI/si0046.asp", SystemTyp.SESSIONNET, Kreis.MUENSTER),
    Stadt("Kreis Warendorf", 182500, "https://www.kreis-warendorf.de/w1/sessionnet/bi/si0046.php", SystemTyp.SESSIONNET, Kreis.MUENSTER),
    Stadt("Kreis Coesfeld", 113000, "https://www.kreis-coesfeld.de/sessionnet/sessionnetbi/si0046.php", SystemTyp.SESSIONNET, Kreis.MUENSTER),
    # Kreis Steinfurt - Gemeinden
    Stadt("Altenberge", 10415, "https://altenberge.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Emsdetten", 35927, "https://emsdetten.ratsinfomanagement.net/termine", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Greven", 37700, "https://greven.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Hopsten", 7007, "https://hopsten.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Horstmar", 6849, "https://horstmar.ratsinfomanagement.net/termine", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Hörstel", 20093, "https://hoerstel.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Ibbenbüren", 51888, "https://ibbenbueren.ratsinfomanagement.net/termine", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Ladbergen", 6821, "https://ladbergen.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Laer", 6805, "https://laer.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Lengerich", 22527, "https://lengerich.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Lienen", 8783, "https://lienen.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Lotte", 14314, "https://lotte.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Metelen", 6417, "https://metelen.ratsinfomanagement.net/startseite", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Mettingen", 12000, "https://mettingen.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Neuenkirchen", 14072, "https://neuenkirchen.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Nordwalde", 9807, "https://nordwalde.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Ochtrup", 19893, "https://ochtrup.gremien.info/", SystemTyp.GREMIENINFO, Kreis.STEINFURT),
    Stadt("Recke", 11370, "https://recke.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Rheine", 76948, "https://www.rheine-buergerinfo.de/si0046.asp", SystemTyp.SESSIONNET, Kreis.STEINFURT),
    Stadt("Saerbeck", 7128, "https://saerbeck.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Steinfurt", 35102, "https://steinfurt.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Tecklenburg", 9288, "https://tecklenburg.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Westerkappeln", 11485, "https://westerkappeln.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.STEINFURT),
    Stadt("Wettringen", 8261, "https://sessionnet.owl-it.de/kreis_steinfurt/wettringen/bi/si0046.asp", SystemTyp.SESSIONNET, Kreis.STEINFURT),
    # Kreis Borken - Gemeinden
    Stadt("Ahaus", 40176, "https://sessionnet.owl-it.de/stadt-ahaus/bi/si0046.asp", SystemTyp.SESSIONNET, Kreis.BORKEN),
    Stadt("Bocholt", 71074, "https://ratsinfo.bocholt.de/", SystemTyp.RATSINFO, Kreis.BORKEN),
    Stadt("Borken", 43035, "https://bi.borken.de/si0046.asp", SystemTyp.SESSIONNET, Kreis.BORKEN),
    Stadt("Gescher", 17433, "https://gescher.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.BORKEN),
    Stadt("Gronau", 49031, "https://gronau.ratsinfomanagement.net/termine", SystemTyp.RATSINFO, Kreis.BORKEN),
    Stadt("Heek", 8628, "https://heek.ratsinfomanagement.net/termine", SystemTyp.RATSINFO, Kreis.BORKEN),
    Stadt("Heiden", 8704, "https://heiden.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.BORKEN),
    Stadt("Isselburg", 11251, "https://isselburg.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.BORKEN),
    Stadt("Legden", 7511, "https://legden.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.BORKEN),
    Stadt("Raesfeld", 11709, "https://raesfeld.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.BORKEN),
    Stadt("Reken", 15109, "https://reken.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.BORKEN),
    Stadt("Rhede", 19674, "https://rhede.gremien.info/", SystemTyp.GREMIENINFO, Kreis.BORKEN),
    Stadt("Schöppingen", 6623, "https://schoeppingen.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.BORKEN),
    Stadt("Stadtlohn", 20946, "https://stadtlohn.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.BORKEN),
    Stadt("Südlohn", 9861, "https://suedlohn.gremien.info/", SystemTyp.GREMIENINFO, Kreis.BORKEN),
    Stadt("Velen", 12678, "https://velen.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.BORKEN),
    Stadt("Vreden", 22758, "https://vreden.ratsinfomanagement.net/", SystemTyp.RATSINFO, Kreis.BORKEN),
    # Kreis Coesfeld - Gemeinden
    Stadt("Ascheberg", 15602, "https://sessionnet.owl-it.de/ascheberg/bi/si0046.asp", SystemTyp.SESSIONNET, Kreis.COESFELD),
    Stadt("Billerbeck", 11945, "https://ratsinfo.billerbeck.de/bi/si0046.asp", SystemTyp.SESSIONNET, Kreis.COESFELD),
    Stadt("Coesfeld", 36382, "https://buergerinfo.coesfeld.de/si0046.php", SystemTyp.SESSIONNET, Kreis.COESFELD),
    Stadt("Dülmen", 46877, "https://sessionweb.duelmen.de/bi/si0046.asp", SystemTyp.SESSIONNET, Kreis.COESFELD),
    Stadt("Havixbeck", 12357, "https://www.ris-havixbeck.de/bi/si0046.php", SystemTyp.SESSIONNET, Kreis.COESFELD),
    Stadt("Lüdinghausen", 24847, "https://www.stadt-luedinghausen.de/sessionnet/buergerinfo/si0046.php", SystemTyp.SESSIONNET, Kreis.COESFELD),
    Stadt("Nordkirchen", 10762, "https://sessionnet.owl-it.de/nordkirchen/bi/si0046.asp", SystemTyp.SESSIONNET, Kreis.COESFELD),
    Stadt("Nottuln", 19672, "https://www.nottuln.de/sessionnet/sessionnetbi/si0046.php", SystemTyp.SESSIONNET, Kreis.COESFELD),
    Stadt("Olfen", 13175, "", SystemTyp.NICHT_UNTERSTUETZT, Kreis.COESFELD),
    Stadt("Rosendahl", 11249, "https://sessionnet.owl-it.de/rosendahl/bi/si0046.asp", SystemTyp.SESSIONNET, Kreis.COESFELD),
    Stadt("Senden", 20495, "https://sessionnet.owl-it.de/gemeinde-senden/bi/si0046.asp", SystemTyp.SESSIONNET, Kreis.COESFELD),
    # Kreis Warendorf - Gemeinden
    Stadt("Ahlen", 52627, "https://www.ahlen.sitzung-online.de/public/", SystemTyp.NICHT_UNTERSTUETZT, Kreis.WARENDORF),
    Stadt("Beckum", 36737, "https://sessionnet.owl-it.de/beckum/bi/si0046.asp", SystemTyp.SESSIONNET, Kreis.WARENDORF),
    Stadt("Beelen", 6159, "https://sessionnet.owl-it.de/beelen/bi/si0046.asp", SystemTyp.SESSIONNET, Kreis.WARENDORF),
    Stadt("Drensteinfurt", 15607, "https://sessionnet.owl-it.de/drensteinfurt/bi/si0046.asp", SystemTyp.SESSIONNET, Kreis.WARENDORF),
    Stadt("Ennigerloh", 20000, "", SystemTyp.NICHT_UNTERSTUETZT, Kreis.WARENDORF),
    Stadt("Everswinkel", 9825, "https://www.everswinkel.de/sessionnet/www/buergerinfo/si0046.php", SystemTyp.SESSIONNET, Kreis.WARENDORF),
    Stadt("Oelde", 29500, "", SystemTyp.NICHT_UNTERSTUETZT, Kreis.WARENDORF),
    Stadt("Ostbevern", 11000, "https://www.ostbevern.de/sessionnet/sessionnetbi/si0046.php", SystemTyp.SESSIONNET, Kreis.WARENDORF),
    Stadt("Sassenberg", 14258, "https://session.sassenberg.de/sessionnet/bi/si0046.php", SystemTyp.SESSIONNET, Kreis.WARENDORF),
    Stadt("Sendenhorst", 14148, "", SystemTyp.NICHT_UNTERSTUETZT, Kreis.WARENDORF),
    Stadt("Telgte", 19982, "https://sessionnet.owl-it.de/telgte/BI/si0046.asp", SystemTyp.SESSIONNET, Kreis.WARENDORF),
    Stadt("Wadersloh", 13000, "https://sessionnet.owl-it.de/wadersloh/bi/si0046.asp", SystemTyp.SESSIONNET, Kreis.WARENDORF),
    Stadt("Warendorf", 37146, "https://sessionnet.owl-it.de/warendorf/bi/si0046.asp", SystemTyp.SESSIONNET, Kreis.WARENDORF),
]


def get_staedte_nach_typ(typ: SystemTyp) -> list[Stadt]:
    """Gibt alle Städte eines bestimmten Systemtyps zurück."""
    return [s for s in STAEDTE if s.typ == typ]


def get_staedte_nach_kreis(kreis: Kreis) -> list[Stadt]:
    """Gibt alle Städte eines Kreises zurück."""
    return [s for s in STAEDTE if s.kreis == kreis]


def get_unterstuetzte_staedte() -> list[Stadt]:
    """Gibt alle Städte mit unterstütztem Systemtyp zurück."""
    return [s for s in STAEDTE if s.typ != SystemTyp.NICHT_UNTERSTUETZT]
