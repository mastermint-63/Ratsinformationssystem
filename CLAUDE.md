# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projektbeschreibung

**Politikradar Münsterland** – Dashboard für Ratstermine im Münsterland. Sammelt Sitzungstermine von 72 Kommunen (70 Gemeinden, LWL, Bezirksregierung Münster) und generiert verlinkte HTML-Dashboards mit Monatsnavigation.

- **Repo:** `github.com/mastermint-63/Ratsinformationssystem`
- **Live:** `https://ms-raete.reporter.ruhr`
- **Schwester-Projekt:** `../ratsinfo_el/` (Politikradar Emscher-Lippe) – gleiche Codebasis, eigene config.py
- **Container:** Dieses Repo liegt in `/Users/fs/claude/ratsinfo/ratsinfo_ms/` – das Elternverzeichnis ist kein Git-Repo

## Ausführung

```bash
python3 app.py                    # 3 Monate ab heute, öffnet Browser
python3 app.py 2026 2             # 3 Monate ab Feb 2026
python3 app.py 2026 1 12          # 12 Monate (ganzes Jahr)
python3 app.py --no-browser       # Ohne Browser (für Cronjobs)

./ratsinfos_upd_fs.sh             # Manuell aktualisieren (Scraping + Push + Benachrichtigung)
tail -20 launchd.log              # Letzte Aktualisierungen anzeigen
```

## Automatische Aktualisierung

- **launchd-Job:** `de.ratstermine.update` – täglich 06:00 Uhr
- **Plist:** `~/Library/LaunchAgents/de.ratstermine.update.plist`
- **Python:** `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`
- **terminal-notifier:** `/opt/homebrew/bin/terminal-notifier`
- **Warum lokal?** Ratsinfomanagement.net blockiert Cloud-IPs (503-Fehler bei GitHub Actions)

```bash
launchctl list | grep ratstermine          # Status prüfen
launchctl start de.ratstermine.update      # Manuell auslösen
gh run list --workflow=deploy.yml          # Deployment-Status prüfen
```

## Architektur

### Datenfluss
1. `app.py:hole_alle_termine()` erstellt Scraper-Instanzen aus `config.py:STAEDTE`, führt sie parallel aus (ThreadPoolExecutor, 10 Workers)
2. Jeder Scraper erbt von `BaseScraper` und implementiert `hole_termine(jahr, monat)` → gibt `Termin`-Dataclass-Objekte zurück
3. `app.py:generiere_kalender()` erzeugt Monatskalender-Tabelle mit Anker-Links
4. `app.py:generiere_html()` gruppiert Termine nach Datum (`id="datum-YYYY-MM-DD"`) und generiert vollständiges HTML inkl. CSS + JS

### Scraper-Typen

| System | Anzahl | Klasse | Methode |
|--------|--------|--------|---------|
| SessionNet (si0046) | 31 | `SessionNetScraper` | HTML-Parsing, 3-stufig: Tabellen → zk-Struktur → Text |
| Ratsinfomanagement / SD.NET RIM | 35 | `RatsinfoScraper` | iCal-Export (`/termine/ics/SD.NET_RIM.ics`), Regex-Parsing |
| ALLRIS net | 2 (LWL, Ahlen) | `AllrisScraper` | Wicket-AJAX, Session-Cookie (JSESSIONID) nötig |
| more!rubin (gremien.info) | 4 (Rhede, Südlohn, Ochtrup, Sendenhorst) | `GremienInfoScraper` | iCal via `api.php?id=calendar&action=webcalendar` |

`GremienInfoScraper` ist eine Subklasse von `RatsinfoScraper` – identisches iCal-Parsing, andere URL-Konstruktion.

ALLRIS-URLs brauchen `/public/`-Suffix: `https://allris.lwl.org/public/` → `base_url/si010` ist der Wicket-Endpunkt.

### HTML-Dashboard

Das gesamte HTML-Template in `app.py:generiere_html()` ist ein einziger f-string:
- CSS und JavaScript müssen geschweifte Klammern **verdoppeln**: `{{` und `}}` statt `{` und `}`
- Bereits generierte `termine_*.html` werden bei app.py-Änderungen **nicht** automatisch neu generiert → neuen Scraper-Lauf starten

**Features:**
- Apple-Design, Dark Mode via `prefers-color-scheme`, max-width 900px
- Kalenderblatt (Mo–So) mit klickbaren Tagen (`#datum-YYYY-MM-DD`), Rücksprunglinks
- 5 Kreis-Dropdowns, kombiniertes Filtern, aktive Filter als Tags
- Sticky Filterleiste: `position:sticky; top:0`, Glaseffekt via `backdrop-filter:blur(12px)`, `rgba(255,255,255,0.5)` / `rgba(45,45,47,0.5)`, `is-sticky`-Klasse via IntersectionObserver
- Auto-Scroll: `window.scrollTo()` + `getBoundingClientRect()` zum nächsten Datum ≥ heute (kein `scrollIntoView` – `scroll-margin-top` per JS unzuverlässig)

## Scraper testen

```python
from config import STAEDTE
from scraper import RatsinfoScraper, SessionNetScraper, AllrisScraper, GremienInfoScraper

stadt = next(s for s in STAEDTE if 'Bezirksregierung' in s.name)
scraper = RatsinfoScraper(stadt.name, stadt.url)
for t in scraper.hole_termine(2026, 3):
    print(f"{t.datum.strftime('%d.%m.%Y')} {t.uhrzeit} – {t.gremium}")
```

Fehlerhafte Städte werden gesammelt und am Ende als `FEHLER:`-Zeile ausgegeben – der Lauf läuft weiter.

## Neues System identifizieren

1. `stadtname.ratsinfomanagement.net` → iCal? → `RatsinfoScraper`; Redirect zu `sitzungsdienst.net`? → gremien.info testen
2. `sessionnet.owl-it.de/stadtname/bi/si0046.asp` → `SessionNetScraper`
3. `stadtname.gremien.info/api.php?id=calendar&action=webcalendar` → `GremienInfoScraper`
4. `/public/` mit Wicket-AJAX (`si010`) → `AllrisScraper`
5. `api.php?id=system&action=index` liefert System-Info ohne Auth (more!rubin-Erkennung)

## Neuen Scraper hinzufügen

1. `config.py`: `SystemTyp`-Enum erweitern, Stadt zur `STAEDTE`-Liste hinzufügen
2. `scraper/neues_system.py`: Klasse mit `hole_termine(jahr, monat) → list[Termin]`
3. `scraper/__init__.py`: Export ergänzen
4. `app.py:hole_alle_termine()`: Schleife für neuen Typ ergänzen

## Dependencies

```bash
pip install -r requirements.txt   # requests, beautifulsoup4, lxml
```

Keine `icalendar`-Library – iCal wird per Regex geparst.

## Mac mini Setup (2026-03-14)

Migration MacBook Pro → Mac mini M4:

- **Git-Remote auf SSH umgestellt**: `git remote set-url origin git@github.com:mastermint-63/Ratsinformationssystem.git`
- **Force-Push nötig**: MacBook hatte heute Morgen noch 3 Commits gepusht (DNS-Fehler beim Netz, aber Push lief durch). Mac-mini-Lauf (20:14 Uhr) hatte aktuellere Daten → `git push --force origin main`
- **DNS-Fehler beim ersten Lauf**: launchd-Run um 06:00 Uhr schlug fehl weil Mac mini direkt nach Start noch kein Netz hatte. Im Dauerbetrieb kein Problem – kein Fix nötig.

## Bekannte Probleme

- Ratsinfomanagement.net blockiert Cloud-IPs → Scraping muss lokal laufen
- SessionNet HTML-Struktur variiert stark → 3-stufiges Parsing nötig
- DTSTART in iCal ist UTC (Z-Suffix), wird als Lokalzeit interpretiert (1–2h Abweichung toleriert)
