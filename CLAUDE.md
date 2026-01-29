# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projektbeschreibung

Ratstermine-Dashboard für das Münsterland. Sammelt Sitzungstermine von 29 Ratsinformationssystemen und generiert verlinkte HTML-Dashboards mit Monatsnavigation.

## Struktur

```
├── app.py                    # Hauptanwendung - Scraper + HTML-Generator
├── config.py                 # Städte-Konfiguration (Name, URL, SystemTyp)
├── update.sh                 # Wrapper für automatische Aktualisierung (mit terminal-notifier)
├── scraper/
│   ├── __init__.py           # Exports: Termin, SessionNetScraper, RatsinfoScraper
│   ├── base.py               # Termin-Dataclass und BaseScraper (ABC)
│   ├── sessionnet.py         # SessionNet-Scraper (si0046.asp/php)
│   └── ratsinfo.py           # Ratsinfomanagement-Scraper (iCal)
├── termine_YYYY_MM.html      # Generierte Dashboards (pro Monat)
├── launchd.log               # Log der automatischen Aktualisierungen
└── Kreise und Städte...html  # Original-Linkliste
```

## Ausführung

```bash
python3 app.py                    # 3 Monate ab heute, öffnet Browser
python3 app.py 2026 2             # 3 Monate ab Feb 2026
python3 app.py 2026 1 12          # 12 Monate (ganzes Jahr)
python3 app.py --no-browser       # Ohne Browser öffnen (für Cronjobs)

./update.sh                       # Manuell aktualisieren (mit Benachrichtigung)
tail -20 launchd.log              # Letzte Aktualisierungen anzeigen
```

## Automatische Aktualisierung

Launchd-Job läuft täglich um 6:00 Uhr (oder beim Aufwachen aus Ruhezustand):
- Plist: `~/Library/LaunchAgents/de.ratstermine.update.plist`
- Log: `launchd.log`
- Benachrichtigung: Klickbar via `terminal-notifier` (öffnet Terminal mit Log)

```bash
launchctl list | grep ratstermine          # Status prüfen
launchctl start de.ratstermine.update      # Manuell auslösen
```

**Wichtig:** `update.sh` verwendet den hardcodierten Python-Pfad `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3` und `terminal-notifier` unter `/opt/homebrew/bin/terminal-notifier`. Bei Python-Updates oder auf anderen Systemen müssen diese Pfade angepasst werden.

## Architektur

### Datenfluss
1. `app.py:hole_alle_termine()` erstellt Scraper-Instanzen basierend auf `config.py:STAEDTE`
2. Scraper werden parallel ausgeführt (ThreadPoolExecutor, 10 Workers)
3. Jeder Scraper erbt von `BaseScraper` und implementiert `hole_termine(jahr, monat)`
4. Rückgabe: Liste von `Termin`-Dataclass-Objekten
5. `app.py:generiere_html()` gruppiert Termine nach Datum und generiert HTML mit:
   - Apple-Design mit Dark Mode Support
   - Stadt-Filter (JavaScript)
   - Monatsnavigation (nur verfügbare Monate verlinkt)

### Scraper-Typen

**SessionNet** (19 Städte):
- URL-Format: `https://example.com/si0046.asp?__cjahr=2026&__cmonat=1`
- Parsing-Strategie: 3-stufig (Tabellen → zk-Struktur → Text-basiert)
- Herausforderung: Verschiedene HTML-Strukturen pro Stadt
- Fallback: Link zur Monatsübersicht wenn kein Detail-Link gefunden

**Ratsinfomanagement.net** (10 Städte):
- URL-Format: `https://stadt.ratsinfomanagement.net/termine/ics/SD.NET_RIM.ics`
- Methode: iCal-Parsing (VEVENT-Blöcke mit DTSTART, SUMMARY, LOCATION, URL)
- Vorteil: Strukturierte Daten, alle Termine auf einmal

### HTML-Dashboard-Features
- Responsive Design (max-width: 900px)
- Filter nach Stadt (JavaScript, versteckt leere Datum-Gruppen)
- Abgesagte Termine: Durchgestrichen, 50% Opacity
- Automatische Link-Konvertierung (relativ → absolut)
- Generierungs-Timestamp im Footer

## Unterstützte Systeme

| System | Anzahl | Methode |
|--------|--------|---------|
| SessionNet (si0046) | 19 | HTML-Parsing mit BeautifulSoup (lxml) |
| Ratsinfomanagement.net | 10 | iCal-Export parsen (Regex) |
| Nicht unterstützt | 4 | Bocholt, Ahlen, Ochtrup (defekt), Ladbergen |

## Neuen Scraper hinzufügen

1. **SystemTyp definieren** in `config.py`:
   ```python
   class SystemTyp(Enum):
       NEUES_SYSTEM = "neues_system"
   ```

2. **Stadt(e) zur STAEDTE-Liste** hinzufügen mit neuem SystemTyp

3. **Scraper-Klasse erstellen** in `scraper/neues_system.py`:
   ```python
   from .base import BaseScraper, Termin

   class NeuesScraper(BaseScraper):
       def hole_termine(self, jahr: int, monat: int) -> list[Termin]:
           # Termine abrufen und als Termin-Objekte zurückgeben
           pass
   ```

4. **Export** in `scraper/__init__.py`:
   ```python
   from .neues_system import NeuesScraper
   __all__ = [..., 'NeuesScraper']
   ```

5. **Integration** in `app.py:hole_alle_termine()`:
   ```python
   for stadt in get_staedte_nach_typ(SystemTyp.NEUES_SYSTEM):
       scraper_aufgaben.append((NeuesScraper(stadt.name, stadt.url), jahr, monat))
   ```

## Dependencies

- `requests` - HTTP-Requests
- `beautifulsoup4` + `lxml` - HTML-Parsing (SessionNet)
- Keine `icalendar`-Library - Ratsinfo-Scraper verwendet Regex-basiertes Parsing

## Bekannte Probleme

- DNS-Fehler bei Netzwerkproblemen führen zu 0 Terminen für betroffene Städte
- SessionNet HTML-Struktur variiert stark → Multi-Strategie-Parsing nötig
- Relative Links manchmal schwer zu erkennen → Heuristiken in Scrapern
