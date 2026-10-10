"""Basis-Klassen für die Ratsinformationssystem-Scraper."""

from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
from urllib.parse import urlsplit


def sicherer_link(link) -> str:
    """Gibt den Link nur zurück, wenn er absolut ist und http(s) nutzt, sonst ''.

    Links stammen aus fremden iCal-Feeds und HTML-Seiten der Kommunen
    (URL:javascript:... wäre sonst ein klickbarer Link, Audit 10.10.2026, Befund #4).
    """
    link = (link or '').strip()
    if not link or any(ord(c) < 0x20 or c == '\x7f' for c in link):
        return ''
    try:
        teile = urlsplit(link)
    except ValueError:
        return ''
    if teile.scheme.lower() not in ('http', 'https') or not teile.netloc:
        return ''
    return link


@dataclass
class Termin:
    """Ein Sitzungstermin."""
    stadt: str
    datum: datetime
    uhrzeit: str
    gremium: str
    ort: str
    link: str

    def __post_init__(self):
        self.link = sicherer_link(self.link)

    def __lt__(self, other):
        """Sortierung nach Datum."""
        return self.datum < other.datum

    def datum_formatiert(self) -> str:
        """Gibt das Datum im deutschen Format zurück."""
        wochentage = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
        wt = wochentage[self.datum.weekday()]
        return f"{wt}, {self.datum.strftime('%d.%m.%Y')}"


class BaseScraper(ABC):
    """Abstrakte Basisklasse für Scraper."""

    def __init__(self, stadt_name: str, base_url: str):
        self.stadt_name = stadt_name
        self.base_url = base_url

    @abstractmethod
    def hole_termine(self, jahr: int, monat: int) -> list[Termin]:
        """Holt alle Termine für einen bestimmten Monat."""
        pass
