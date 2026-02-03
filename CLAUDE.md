# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projektbeschreibung

Ratstermine-Dashboard für das Münsterland. Sammelt Sitzungstermine von 70 Gemeinden (60 mit Scraper-Unterstützung) und generiert verlinkte HTML-Dashboards mit Monatsnavigation.

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

Vollautomatischer Workflow via macOS launchd:

```
06:00 Uhr (oder Mac wacht auf)
        │
        ▼
┌─ update.sh ─────────────────────────────┐
│  1. Scraping: Alle Kommunen abfragen    │
│  2. HTML-Dateien generieren             │
│  3. git add/commit/push (bei Änderung)  │
│  4. macOS Benachrichtigung anzeigen     │
└─────────────────────────────────────────┘
        │
        ▼
GitHub Actions deployed automatisch
        │
        ▼
https://ms-raete.reporter.ruhr ist aktuell
```

**Warum lokal?** Ratsinfomanagement.net blockiert Cloud-IPs (GitHub Actions bekommt 503-Fehler). Dein Mac hat eine normale IP und wird nicht blockiert.

**Voraussetzung:** Mac muss um 6:00 Uhr an oder im Ruhezustand sein (nicht ausgeschaltet).

### Konfiguration

- Plist: `~/Library/LaunchAgents/de.ratstermine.update.plist`
- Log: `launchd.log`
- Benachrichtigung: Klickbar via `terminal-notifier` (öffnet Terminal mit Log)

```bash
launchctl list | grep ratstermine          # Status prüfen
launchctl start de.ratstermine.update      # Manuell auslösen
./update.sh                                 # Direkt ausführen (mit Push)
```

**Wichtig:** `update.sh` verwendet hardcodierte Pfade:
- Python: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`
- terminal-notifier: `/opt/homebrew/bin/terminal-notifier`

Bei Python-Updates oder auf anderen Systemen müssen diese Pfade angepasst werden.

## Architektur

### Datenfluss
1. `app.py:hole_alle_termine()` erstellt Scraper-Instanzen basierend auf `config.py:STAEDTE`
2. Scraper werden parallel ausgeführt (ThreadPoolExecutor, 10 Workers)
3. Jeder Scraper erbt von `BaseScraper` und implementiert `hole_termine(jahr, monat)`
4. Rückgabe: Liste von `Termin`-Dataclass-Objekten
5. `app.py:generiere_kalender()` erzeugt Monatskalender-Tabelle mit Anker-Links
6. `app.py:generiere_html()` gruppiert Termine nach Datum (`id="datum-YYYY-MM-DD"`) und generiert HTML mit:
   - Apple-Design mit Dark Mode Support
   - Kalenderblatt mit klickbaren Tagen und Rücksprunglinks
   - Stadt-Filter (JavaScript)
   - Monatsnavigation (nur verfügbare Monate verlinkt)

### Scraper-Typen

**SessionNet** (27 Städte):
- URL-Format: `https://example.com/si0046.asp?__cjahr=2026&__cmonat=1`
- Parsing-Strategie: 3-stufig (Tabellen → zk-Struktur → Text-basiert)
- Herausforderung: Verschiedene HTML-Strukturen pro Stadt
- Fallback: Link zur Monatsübersicht wenn kein Detail-Link gefunden

**Ratsinfomanagement.net** (33 Städte):
- URL-Format: `https://stadt.ratsinfomanagement.net/termine/ics/SD.NET_RIM.ics`
- Methode: iCal-Parsing (VEVENT-Blöcke mit DTSTART, SUMMARY, LOCATION, URL)
- Vorteil: Strukturierte Daten, alle Termine auf einmal

### HTML-Dashboard-Features
- Responsive Design (max-width: 900px)
- Kalenderblatt (Mo–So) oberhalb der Termine (`id="kalender"`), Tage mit Sitzungen als blaue Kreise anklickbar, springt per Anker (`#datum-YYYY-MM-DD`) zum jeweiligen Datum; jede Datumsgruppe hat einen „↑ Kalender"-Rücksprunglink
- Filter nach Stadt (JavaScript, versteckt leere Datum-Gruppen)
- Abgesagte Termine: Durchgestrichen, 50% Opacity
- Automatische Link-Konvertierung (relativ → absolut)
- Generierungs-Timestamp im Footer

## Unterstützte Systeme

| System | Anzahl | Methode |
|--------|--------|---------|
| SessionNet (si0046) | 27 | HTML-Parsing mit BeautifulSoup (lxml) |
| Ratsinfomanagement.net | 33 | iCal-Export parsen (Regex) |
| Nicht unterstützt | 10 | ALLRIS: Ahlen · SD.NET RIM: Bocholt · more!rubin: Ochtrup, Rhede, Südlohn · Kein System: Ennigerloh, Oelde, Sendenhorst · Nicht erreichbar: Ahaus, Olfen |

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

Installieren mit `pip install -r requirements.txt`:
- `requests` - HTTP-Requests (Timeout: SessionNet 15s, Ratsinfo 30s)
- `beautifulsoup4` + `lxml` - HTML-Parsing (SessionNet)
- Keine `icalendar`-Library - Ratsinfo-Scraper verwendet Regex-basiertes Parsing

## GitHub Pages Deployment

- **URL:** `https://ms-raete.reporter.ruhr/` (Custom Domain)
- **Repo:** `github.com/mastermint-63/Ratsinformationssystem` (öffentlich)
- **Workflow:** `.github/workflows/deploy.yml` – deployed automatisch bei Push von HTML-Dateien

**Automatisch:** `update.sh` (via launchd) scrapt täglich und pusht zu GitHub.

**Manuell:** Falls nötig, kann manuell aktualisiert werden:
```bash
./update.sh                                # Scrapen + Push (empfohlen)
# oder einzeln:
python3 app.py --no-browser && git add termine_*.html index.html && git commit -m "Termine aktualisiert" && git push
```

```bash
gh run list --workflow=deploy.yml          # Deployment-Status prüfen
```

## Bekannte Probleme

- **Ratsinfomanagement.net blockiert Cloud-IPs** - GitHub Actions, AWS etc. bekommen 503-Fehler → Termine müssen lokal generiert werden
- DNS-Fehler bei Netzwerkproblemen führen zu 0 Terminen für betroffene Städte
- SessionNet HTML-Struktur variiert stark → Multi-Strategie-Parsing nötig
- Relative Links manchmal schwer zu erkennen → Heuristiken in Scrapern
