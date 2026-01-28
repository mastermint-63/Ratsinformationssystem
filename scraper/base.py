"""Basis-Klassen für die Ratsinformationssystem-Scraper."""

from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod


@dataclass
class Termin:
    """Ein Sitzungstermin."""
    stadt: str
    datum: datetime
    uhrzeit: str
    gremium: str
    ort: str
    link: str

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
