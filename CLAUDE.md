# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projektbeschreibung

Ratstermine-Dashboard für das Münsterland. Sammelt Sitzungstermine von 72 Kommunen (70 Gemeinden, LWL, Bezirksregierung Münster) mit vollständiger Scraper-Unterstützung und generiert verlinkte HTML-Dashboards mit Monatsnavigation.

## Struktur

```
├── app.py                    # Hauptanwendung - Scraper + HTML-Generator
├── config.py                 # Städte-Konfiguration (Name, URL, SystemTyp, Kreis)
├── ratsinfos_upd_fs.sh       # Wrapper für automatische Aktualisierung (mit terminal-notifier)
├── scraper/
│   ├── __init__.py           # Exports: Termin, SessionNetScraper, RatsinfoScraper, AllrisScraper, GremienInfoScraper
│   ├── base.py               # Termin-Dataclass und BaseScraper (ABC)
│   ├── sessionnet.py         # SessionNet-Scraper (si0046.asp/php)
│   ├── ratsinfo.py           # Ratsinfomanagement-Scraper (iCal/SD.NET RIM)
│   ├── allris.py             # ALLRIS net-Scraper (Wicket-AJAX)
│   └── gremieninfo.py        # more!rubin-Scraper (gremien.info WebCalendar-API)
├── feed.xml                  # RSS-Feed (aktueller Monat, automatisch generiert)
├── termine_YYYY_MM.html      # Generierte Dashboards (pro Monat)
└── launchd.log               # Log der automatischen Aktualisierungen
```

## Ausführung

```bash
python3 app.py                    # 3 Monate ab heute, öffnet Browser
python3 app.py 2026 2             # 3 Monate ab Feb 2026
python3 app.py 2026 1 12          # 12 Monate (ganzes Jahr)
python3 app.py --no-browser       # Ohne Browser öffnen (für Cronjobs)

./ratsinfos_upd_fs.sh                       # Manuell aktualisieren (mit Benachrichtigung)
tail -20 launchd.log              # Letzte Aktualisierungen anzeigen
```

## Automatische Aktualisierung

Vollautomatischer Workflow via macOS launchd:

```
06:00 Uhr (oder Mac wacht auf)
        │
        ▼
┌─ ratsinfos_upd_fs.sh ─────────────────────────────┐
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
./ratsinfos_upd_fs.sh                                 # Direkt ausführen (mit Push)
```

**Wichtig:** `ratsinfos_upd_fs.sh` verwendet hardcodierte Pfade:
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

**SessionNet** (31 Städte):
- URL-Format: `https://example.com/si0046.asp?__cjahr=2026&__cmonat=1`
- Parsing-Strategie: 3-stufig (Tabellen → zk-Struktur → Text-basiert)
- Herausforderung: Verschiedene HTML-Strukturen pro Stadt
- Fallback: Link zur Monatsübersicht wenn kein Detail-Link gefunden

**Ratsinfomanagement.net / SD.NET RIM via iCal** (35 Kommunen):
- URL-Format: `https://stadt.ratsinfomanagement.net/termine/ics/SD.NET_RIM.ics` (oder eigene Domain wie `ratsinfo.bocholt.de`, `regionalrat-muenster.nrw.de`)
- Methode: iCal-Parsing (VEVENT-Blöcke mit DTSTART, SUMMARY, LOCATION, URL/DESCRIPTION)
- DTSTART ist UTC (Z-Suffix), wird als Lokalzeit interpretiert (1–2h Abweichung toleriert)

**ALLRIS net** (2 – LWL + Ahlen):
- URLs: `https://allris.lwl.org/public/` und `https://www.ahlen.sitzung-online.de/public/`
- Methode: Wicket-AJAX (Session starten → Timer-AJAX → Monat/Jahr navigieren → HTML-Tabelle parsen)
- Besonderheit: Kalender lädt per AJAX nach, benötigt Session-Cookie (JSESSIONID)

**more!rubin / gremien.info** (4 – Rhede, Südlohn, Ochtrup, Sendenhorst):
- URL-Format: `https://stadtname.gremien.info/api.php?id=calendar&action=webcalendar`
- Methode: `GremienInfoScraper` ist eine Subklasse von `RatsinfoScraper` – identisches iCal-Parsing, nur andere URL-Konstruktion
- Entdeckung: Subdomain `stadtname.gremien.info` prüfen; `api.php?id=system&action=index` liefert System-Info ohne Auth

### HTML-Dashboard-Features
- Responsive Design (max-width: 900px)
- Kalenderblatt (Mo–So) oberhalb der Termine (`id="kalender"`), Tage mit Sitzungen als blaue Kreise anklickbar, springt per Anker (`#datum-YYYY-MM-DD`) zum jeweiligen Datum; jede Datumsgruppe hat einen „↑ Kalender"-Rücksprunglink
- Kreis-basierte Filter: 5 Dropdowns (Münsterland, Steinfurt, Borken, Coesfeld, Warendorf)
- Kombiniertes Filtern: Mehrere Kommunen gleichzeitig auswählbar
- Aktive Filter als Tags mit Entfernen-Button, "Alle zurücksetzen"-Button
- Abgesagte Termine: Durchgestrichen, 50% Opacity
- Automatische Link-Konvertierung (relativ → absolut)
- RSS-Feed (`feed.xml`) für den aktuellen Monat, auto-discoverable via `<link rel="alternate">`
- Generierungs-Timestamp im Footer

## Unterstützte Systeme

| System | Anzahl | Methode |
|--------|--------|---------|
| SessionNet (si0046) | 31 | HTML-Parsing mit BeautifulSoup (lxml) |
| Ratsinfomanagement.net / SD.NET RIM | 35 | iCal-Export parsen (Regex) |
| ALLRIS net | 2 | Wicket-AJAX mit Session-Cookie + HTML-Parsing (LWL, Ahlen) |
| more!rubin (gremien.info) | 4 | WebCalendar-API: `api.php?id=calendar&action=webcalendar` |

### Aktualisierungen
*   **16. Feb 2026:** Bezirksregierung Münster (SD.NET RIM via iCal) integriert – Regionalrat-Termine über `regionalrat-muenster.nrw.de/termine/ics/SD.NET_RIM.ics`
*   **16. Feb 2026:** Ahlen (ALLRIS/sitzung-online.de), Ennigerloh + Oelde (SessionNet/owl-it.de), Sendenhorst (gremien.info), Olfen (SessionNet/ratsinfo.olfen.de) integriert – alle Gemeinden nun vollständig abgedeckt
*   **16. Feb 2026:** Rhede + Südlohn (more!rubin/gremien.info) integriert – `GremienInfoScraper` (Subklasse RatsinfoScraper), iCal via `api.php?id=calendar&action=webcalendar`
*   **16. Feb 2026:** Bocholt (SD.NET RIM via iCal) integriert – iCal-URL `ratsinfo.bocholt.de/termine/ics/SD.NET_RIM.ics` funktioniert mit bestehendem `RatsinfoScraper`
*   **15. Feb 2026:** LWL (ALLRIS net) integriert, Kreisverwaltungen und Stadt Münster ins "Münsterland"-Dropdown zusammengefasst
*   **06. Feb 2026:** Kreis-basierte Filter-Dropdowns eingeführt (5 Dropdowns statt "Alle Städte"), kombiniertes Filtern möglich
*   **03. Feb 2026:** Ahaus (SessionNet) wurde erfolgreich in die Konfiguration aufgenommen und wird nun gescrapt

## Neuen Scraper hinzufügen

1. **SystemTyp definieren** in `config.py`:
   ```python
   class SystemTyp(Enum):
       NEUES_SYSTEM = "neues_system"
   ```

2. **Stadt(e) zur STAEDTE-Liste** hinzufügen mit SystemTyp und Kreis (z.B. `Kreis.STEINFURT`)

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
- `requests` - HTTP-Requests (Timeout: SessionNet 15s, Ratsinfo 30s, ALLRIS 15s)
- `beautifulsoup4` + `lxml` - HTML-Parsing (SessionNet, ALLRIS)
- Keine `icalendar`-Library - Ratsinfo-Scraper verwendet Regex-basiertes Parsing

## GitHub Pages Deployment

- **URL:** `https://ms-raete.reporter.ruhr/` (Custom Domain)
- **Repo:** `github.com/mastermint-63/Ratsinformationssystem` (öffentlich)
- **Workflow:** `.github/workflows/deploy.yml` – deployed automatisch bei Push von HTML-Dateien

**Automatisch:** `ratsinfos_upd_fs.sh` (via launchd) scrapt täglich und pusht zu GitHub.

**Manuell:** Falls nötig, kann manuell aktualisiert werden:
```bash
./ratsinfos_upd_fs.sh                                # Scrapen + Push (empfohlen)
# oder einzeln:
python3 app.py --no-browser && git add termine_*.html index.html feed.xml && git commit -m "Termine aktualisiert" && git push
```

```bash
gh run list --workflow=deploy.yml          # Deployment-Status prüfen
```

## Neues System identifizieren

Wenn eine Stadt noch kein System hat oder als `NICHT_UNTERSTUETZT` gelistet ist:

1. `stadtname.ratsinfomanagement.net` → Redirect zu `sitzungsdienst.net`? → Dann gremien.info testen: `stadtname.gremien.info/api.php?id=calendar&action=webcalendar`
2. Gemeinde-Website → Seite "Ratsinformation" oder "Rat und Ausschüsse" → externen Link prüfen
3. `sessionnet.owl-it.de/stadtname/bi/si0046.asp` direkt testen
4. `stadtname.gremien.info`, `ratsinfo.stadtname.de` als URL-Muster ausprobieren
5. Wenn `BEGIN:VCALENDAR` zurückkommt → iCal-kompatibel → `RatsinfoScraper` oder `GremienInfoScraper` nutzbar
6. Wenn SessionNet-HTML zurückkommt → `SessionNetScraper` nutzbar
7. Wenn Wicket-AJAX (`si010`-Pfad) → `AllrisScraper` nutzbar

## Bekannte Probleme

- **Ratsinfomanagement.net blockiert Cloud-IPs** - GitHub Actions, AWS etc. bekommen 503-Fehler → Termine müssen lokal generiert werden
- DNS-Fehler bei Netzwerkproblemen führen zu 0 Terminen für betroffene Städte
- SessionNet HTML-Struktur variiert stark → Multi-Strategie-Parsing nötig
- Relative Links manchmal schwer zu erkennen → Heuristiken in Scrapern
