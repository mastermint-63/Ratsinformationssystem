"""Scraper für Ratsinfomanagement.net-Systeme (via iCal-Export)."""

import re
import requests
from datetime import datetime
from urllib.parse import urlparse
from .base import BaseScraper, Termin


class RatsinfoScraper(BaseScraper):
    """Scraper für Ratsinfomanagement.net-basierte Ratsinformationssysteme."""

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    def __init__(self, stadt_name: str, base_url: str):
        super().__init__(stadt_name, base_url)
        # Basis-URL ermitteln
        parsed = urlparse(base_url)
        self.base_domain = f"{parsed.scheme}://{parsed.netloc}"
        self.ical_url = f"{self.base_domain}/termine/ics/SD.NET_RIM.ics"

    def hole_termine(self, jahr: int, monat: int) -> list[Termin]:
        """Holt alle Termine für einen bestimmten Monat aus dem iCal-Feed."""
        response = requests.get(self.ical_url, headers=self.HEADERS, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'

        return self._parse_ical(response.text, jahr, monat)

    def _parse_ical(self, ical_text: str, jahr: int, monat: int) -> list[Termin]:
        """Parst den iCal-Text und extrahiert Termine für den angegebenen Monat."""
        termine = []

        # iCal in Events aufteilen
        events = re.split(r'BEGIN:VEVENT', ical_text)

        for event in events[1:]:  # Erstes Element ist Header
            if 'END:VEVENT' not in event:
                continue

            termin = self._parse_event(event, jahr, monat)
            if termin:
                termine.append(termin)

        return termine

    def _parse_event(self, event_text: str, jahr: int, monat: int) -> Termin | None:
        """Parst ein einzelnes iCal-Event."""
        # DTSTART extrahieren
        dtstart_match = re.search(r'DTSTART[^:]*:(\d{8}T\d{6})', event_text)
        if not dtstart_match:
            return None

        try:
            # Format: 20260205T160000 oder 20260205T160000Z
            dt_str = dtstart_match.group(1)
            datum = datetime.strptime(dt_str[:15], '%Y%m%dT%H%M%S')
        except ValueError:
            return None

        # Nur Termine im gewünschten Monat
        if datum.year != jahr or datum.month != monat:
            return None

        uhrzeit = datum.strftime('%H:%M Uhr')

        # SUMMARY (Gremium) extrahieren
        summary_match = re.search(r'SUMMARY:(.+?)(?:\r?\n(?! )|\r?\nEND)', event_text, re.DOTALL)
        gremium = 'Unbekannt'
        if summary_match:
            gremium = self._unfold_ical_line(summary_match.group(1))

        # LOCATION extrahieren
        location_match = re.search(r'LOCATION:(.+?)(?:\r?\n(?! )|\r?\nEND)', event_text, re.DOTALL)
        ort = ''
        if location_match:
            ort = self._unfold_ical_line(location_match.group(1))

        # URL oder DESCRIPTION mit Link extrahieren
        url_match = re.search(r'URL:(.+?)(?:\r?\n(?! )|\r?\nEND)', event_text, re.DOTALL)
        link = ''
        if url_match:
            link = self._unfold_ical_line(url_match.group(1))
        else:
            # Versuche Link aus DESCRIPTION zu extrahieren
            desc_match = re.search(r'DESCRIPTION:(.+?)(?:\r?\nEND|\r?\n[A-Z]+:)', event_text, re.DOTALL)
            if desc_match:
                desc = self._unfold_ical_line(desc_match.group(1))
                link_in_desc = re.search(r'https?://[^\s<>"\\]+', desc)
                if link_in_desc:
                    link = link_in_desc.group(0)

        # Falls kein Link gefunden, verwende Terminseite
        if not link:
            link = f"{self.base_domain}/termine"

        return Termin(
            stadt=self.stadt_name,
            datum=datum,
            uhrzeit=uhrzeit,
            gremium=gremium[:100],
            ort=ort[:100],
            link=link
        )

    def _unfold_ical_line(self, text: str) -> str:
        """Entfaltet iCal-Zeilen (Fortsetzungszeilen beginnen mit Leerzeichen/Tab)."""
        # Entferne Zeilenumbrüche mit Fortsetzung
        text = re.sub(r'\r?\n[ \t]', '', text)
        # Entferne übrige Zeilenumbrüche
        text = re.sub(r'\r?\n.*', '', text)
        # Dekodiere escaped characters
        text = text.replace('\\n', ' ').replace('\\,', ',').replace('\\;', ';')
        return text.strip()
