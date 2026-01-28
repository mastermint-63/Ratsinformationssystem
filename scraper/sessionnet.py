"""Scraper für SessionNet-Systeme (si0046.asp/php)."""

import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from .base import BaseScraper, Termin


class SessionNetScraper(BaseScraper):
    """Scraper für SessionNet-basierte Ratsinformationssysteme."""

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    def __init__(self, stadt_name: str, base_url: str):
        super().__init__(stadt_name, base_url)
        # Basis-URL für Termine ermitteln
        if '?' in base_url:
            self.termine_url = base_url.split('?')[0]
        else:
            self.termine_url = base_url

    def hole_termine(self, jahr: int, monat: int) -> list[Termin]:
        """Holt alle Termine für einen bestimmten Monat."""
        url = f"{self.termine_url}?__cjahr={jahr}&__cmonat={monat}"

        try:
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
        except requests.RequestException as e:
            print(f"Fehler beim Abrufen von {self.stadt_name}: {e}")
            return []

        return self._parse_html(response.text, jahr, monat)

    def _parse_html(self, html: str, jahr: int, monat: int) -> list[Termin]:
        """Parst die HTML-Seite und extrahiert Termine."""
        soup = BeautifulSoup(html, 'lxml')
        termine = []

        # Verschiedene Parsing-Strategien versuchen
        termine = self._parse_tabelle(soup, jahr, monat)
        if not termine:
            termine = self._parse_zk_struktur(soup, jahr, monat)
        if not termine:
            termine = self._parse_text_basiert(soup, jahr, monat)

        return termine

    def _parse_tabelle(self, soup: BeautifulSoup, jahr: int, monat: int) -> list[Termin]:
        """Versucht, Termine aus Tabellen zu extrahieren."""
        termine = []

        # Suche nach Tabellen mit Sitzungsdaten
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    text = ' '.join(c.get_text(strip=True) for c in cells)
                    termin = self._extrahiere_termin_aus_text(text, row, jahr, monat)
                    if termin:
                        termine.append(termin)

        return termine

    def _parse_zk_struktur(self, soup: BeautifulSoup, jahr: int, monat: int) -> list[Termin]:
        """Parst die zk-Struktur (SessionNet-spezifisch)."""
        termine = []

        # Suche nach zk-Elementen (SessionNet-spezifisch)
        for elem in soup.find_all(['div', 'span', 'p'], class_=re.compile(r'zk|smc|si')):
            text = elem.get_text(strip=True)
            link_elem = elem.find('a')
            link = link_elem.get('href', '') if link_elem else ''

            termin = self._extrahiere_termin_aus_text(text, elem, jahr, monat)
            if termin:
                termine.append(termin)

        return termine

    def _parse_text_basiert(self, soup: BeautifulSoup, jahr: int, monat: int) -> list[Termin]:
        """Parst Termine basierend auf Textmustern."""
        termine = []
        aktuelles_datum = None

        # Hole den gesamten Text-Inhalt
        content = soup.find('body')
        if not content:
            return termine

        # Suche nach Datumsmustern und sammle Termine
        datum_pattern = re.compile(r'(Mo|Di|Mi|Do|Fr|Sa|So)\s+(\d{2})\.(\d{2})\.(\d{4})')
        zeit_pattern = re.compile(r'(\d{1,2}):(\d{2})\s*(?:Uhr)?')

        # Iteriere durch alle Textblöcke
        for elem in content.find_all(['div', 'p', 'span', 'tr', 'li']):
            text = elem.get_text(' ', strip=True)

            # Prüfe auf Datum
            datum_match = datum_pattern.search(text)
            if datum_match:
                tag = int(datum_match.group(2))
                monat_parsed = int(datum_match.group(3))
                jahr_parsed = int(datum_match.group(4))
                try:
                    aktuelles_datum = datetime(jahr_parsed, monat_parsed, tag)
                except ValueError:
                    continue

            # Prüfe auf Uhrzeit (= Termin)
            zeit_match = zeit_pattern.search(text)
            if zeit_match and aktuelles_datum:
                uhrzeit = f"{zeit_match.group(1)}:{zeit_match.group(2)} Uhr"

                # Extrahiere Gremium (Text nach der Uhrzeit, vor "Ort" oder Ende)
                text_nach_zeit = text[zeit_match.end():].strip()

                # Suche nach Sitzungslink (bevorzugt smc_datatype_si)
                link_elem = elem.find('a', class_='smc_datatype_si')
                if not link_elem:
                    # Fallback: Erster Link mit si00-URL
                    for a in elem.find_all('a'):
                        href = a.get('href', '')
                        if href and 'si00' in href:
                            link_elem = a
                            break
                if not link_elem:
                    link_elem = elem.find('a', href=True)

                link = ''
                gremium = text_nach_zeit[:100] if text_nach_zeit else 'Unbekannt'

                if link_elem:
                    link = link_elem.get('href', '')
                    if link and not link.startswith('http'):
                        # Relativen Link in absoluten umwandeln
                        base = '/'.join(self.termine_url.split('/')[:-1])
                        link = f"{base}/{link}"
                    gremium = link_elem.get_text(strip=True) or gremium

                # Fallback: Link zur Terminübersicht des Monats
                if not link:
                    link = f"{self.termine_url}?__cjahr={aktuelles_datum.year}&__cmonat={aktuelles_datum.month}"

                # Prüfe auf Absage
                if 'abgesagt' in text.lower():
                    gremium = f"[ABGESAGT] {gremium}"

                termin = Termin(
                    stadt=self.stadt_name,
                    datum=aktuelles_datum,
                    uhrzeit=uhrzeit,
                    gremium=gremium.split('|')[0].strip()[:100],  # Begrenzen
                    ort='',  # Ort separat zu parsen ist schwierig
                    link=link
                )
                termine.append(termin)

        return termine

    def _extrahiere_termin_aus_text(self, text: str, elem, jahr: int, monat: int) -> Termin | None:
        """Versucht, einen Termin aus einem Textblock zu extrahieren."""
        # Datum-Pattern: "Mo 02.02.2026" oder "02.02.2026"
        datum_pattern = re.compile(r'(\d{2})\.(\d{2})\.(\d{4})')
        zeit_pattern = re.compile(r'(\d{1,2}):(\d{2})')

        datum_match = datum_pattern.search(text)
        zeit_match = zeit_pattern.search(text)

        if not datum_match or not zeit_match:
            return None

        try:
            tag = int(datum_match.group(1))
            monat_parsed = int(datum_match.group(2))
            jahr_parsed = int(datum_match.group(3))
            datum = datetime(jahr_parsed, monat_parsed, tag)
        except ValueError:
            return None

        uhrzeit = f"{zeit_match.group(1)}:{zeit_match.group(2)} Uhr"

        # Gremium und Link extrahieren
        link = ''
        gremium = 'Unbekannt'

        if hasattr(elem, 'find'):
            # Bevorzugt: SessionNet-Sitzungslink (class="smc_datatype_si")
            link_elem = elem.find('a', class_='smc_datatype_si')
            # Alternativ: Link in der Sitzungszelle (class="silink")
            silink_td = elem.find('td', class_='silink')
            if not link_elem and silink_td:
                link_elem = silink_td.find('a', href=True)
            # Fallback: Erster Link mit nicht-leerem href
            if not link_elem:
                for a in elem.find_all('a'):
                    href = a.get('href', '')
                    if href and 'si00' in href:
                        link_elem = a
                        break

            if link_elem:
                link = link_elem.get('href', '')
                gremium = link_elem.get_text(strip=True) or gremium
                if link and not link.startswith('http'):
                    base = '/'.join(self.termine_url.split('/')[:-1])
                    link = f"{base}/{link}"

            # Gremiumsname aus smc-el-h extrahieren, auch wenn kein Link vorhanden
            if gremium == 'Unbekannt':
                el_h = silink_td.find('div', class_='smc-el-h') if silink_td else None
                if el_h:
                    gremium = el_h.get_text(strip=True) or gremium

        # Fallback: Link zur Terminübersicht des Monats
        if not link:
            link = f"{self.termine_url}?__cjahr={datum.year}&__cmonat={datum.month}"

        return Termin(
            stadt=self.stadt_name,
            datum=datum,
            uhrzeit=uhrzeit,
            gremium=gremium[:100],
            ort='',
            link=link
        )
