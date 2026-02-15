"""Scraper für ALLRIS net 4.x-Systeme (via Wicket-AJAX)."""

import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from .base import BaseScraper, Termin


class AllrisScraper(BaseScraper):
    """Scraper für ALLRIS net-basierte Ratsinformationssysteme."""

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,*/*',
        'Accept-Language': 'de-DE,de;q=0.9',
    }

    AJAX_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/xml, text/xml, */*',
        'Accept-Language': 'de-DE,de;q=0.9',
        'Wicket-Ajax': 'true',
        'Wicket-Ajax-BaseURL': 'si010',
    }

    def __init__(self, stadt_name: str, base_url: str):
        super().__init__(stadt_name, base_url)
        self.base_url = base_url.rstrip('/')
        self.kalender_url = f"{self.base_url}/si010"

    def hole_termine(self, jahr: int, monat: int) -> list[Termin]:
        """Holt alle Termine für einen bestimmten Monat via Wicket-AJAX."""
        session = requests.Session()

        # Schritt 1: Session starten
        session.get(self.kalender_url, headers=self.HEADERS, timeout=15)

        # Schritt 2: Kalender-Daten laden (Timer-Endpoint)
        ajax_url = f"{self.kalender_url}?0-1.0-"
        resp = session.get(ajax_url, headers=self.AJAX_HEADERS, timeout=15)
        resp.raise_for_status()

        # Aktuellen Monat/Jahr aus der initialen Antwort ermitteln
        jetzt = datetime.now()
        aktueller_monat = jetzt.month
        aktuelles_jahr = jetzt.year

        # Schritt 3: Zum gewünschten Jahr navigieren (falls nötig)
        if jahr != aktuelles_jahr:
            jahr_index = jahr - 2023
            if 0 <= jahr_index <= 6:
                url = f"{self.kalender_url}?0-1.0-form-calNav-years-{jahr_index}-yearlink"
                resp = session.get(url, headers=self.AJAX_HEADERS, timeout=15)
                resp.raise_for_status()

        # Schritt 4: Zum gewünschten Monat navigieren (falls nötig)
        if monat != aktueller_monat or jahr != aktuelles_jahr:
            monat_index = monat - 1
            url = f"{self.kalender_url}?0-1.0-form-calNav-months-{monat_index}-monthlink"
            resp = session.get(url, headers=self.AJAX_HEADERS, timeout=15)
            resp.raise_for_status()

        return self._parse_kalender(resp.text, jahr, monat)

    def _parse_kalender(self, xml_text: str, jahr: int, monat: int) -> list[Termin]:
        """Parst die AJAX-Antwort und extrahiert Termine."""
        termine = []
        soup = BeautifulSoup(xml_text, 'lxml')

        aktueller_tag = None

        for row in soup.find_all('tr'):
            classes = row.get('class', [])

            # Leere Zeilen überspringen
            if 'emptyRow' in classes:
                tag_span = row.find('span', class_='dom')
                if tag_span:
                    aktueller_tag = int(tag_span.get_text(strip=True))
                continue

            # Tag aus der Zeile extrahieren
            tag_span = row.find('span', class_='dom')
            if tag_span:
                aktueller_tag = int(tag_span.get_text(strip=True))
            elif 'sameday' not in classes:
                # Weder eigener Tag noch sameday → Header-Zeile etc.
                continue

            if aktueller_tag is None:
                continue

            # Uhrzeit
            zeit_td = row.find('td', class_='time')
            if not zeit_td:
                continue
            zeit_text = zeit_td.get_text(strip=True)
            if not zeit_text:
                continue

            # Gremium (Sitzungsname)
            text_td = row.find('td', class_='textCol')
            if not text_td:
                continue
            link_tag = text_td.find('a')
            gremium = link_tag.get_text(strip=True) if link_tag else text_td.get_text(strip=True)

            # Link zur Sitzung
            link = ''
            if link_tag and link_tag.get('href'):
                href = link_tag['href']
                if href.startswith('./'):
                    link = f"{self.base_url}/{href[2:]}"
                elif href.startswith('http'):
                    link = href
                else:
                    link = f"{self.base_url}/{href}"
            if not link:
                link = self.kalender_url

            # Raum/Ort
            raum_td = row.find('td', class_='raum')
            ort = raum_td.get_text(strip=True) if raum_td else ''

            # Datum zusammenbauen
            try:
                stunde, minute = 0, 0
                zeit_match = re.match(r'(\d{1,2}):(\d{2})', zeit_text)
                if zeit_match:
                    stunde = int(zeit_match.group(1))
                    minute = int(zeit_match.group(2))
                datum = datetime(jahr, monat, aktueller_tag, stunde, minute)
            except ValueError:
                continue

            uhrzeit = f"{stunde:02d}:{minute:02d} Uhr"

            termine.append(Termin(
                stadt=self.stadt_name,
                datum=datum,
                uhrzeit=uhrzeit,
                gremium=gremium[:100],
                ort=ort[:100],
                link=link
            ))

        return termine
