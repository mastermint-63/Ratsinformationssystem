# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projektbeschreibung

Ratstermine-Dashboard für das Münsterland. Sammelt Sitzungstermine von 29 Ratsinformationssystemen und generiert verlinkte HTML-Dashboards mit Monatsnavigation.

## Struktur

```
├── app.py                    # Hauptanwendung - Scraper + HTML-Generator
├── config.py                 # Städte-Konfiguration (Name, URL, SystemTyp)
├── update.sh                 # Wrapper für automatische Aktualisierung
├── scraper/
│   ├── base.py               # Termin-Dataclass und BaseScraper
│   ├── sessionnet.py         # SessionNet-Scraper (si0046.asp/php)
│   └── ratsinfo.py           # Ratsinfomanagement-Scraper (iCal)
├── termine_YYYY_MM.html      # Generierte Dashboards (pro Monat)
└── Kreise und Städte...html  # Original-Linkliste
```

## Ausführung

```bash
python3 app.py                    # 3 Monate ab heute, öffnet Browser
python3 app.py 2026 2             # 3 Monate ab Feb 2026
python3 app.py 2026 1 12          # 12 Monate (ganzes Jahr)
python3 app.py --no-browser       # Ohne Browser öffnen (für Cronjobs)

./update.sh                       # Manuell aktualisieren (mit Benachrichtigung)
```

## Automatische Aktualisierung

Launchd-Job läuft täglich um 6:00 Uhr (oder beim Aufwachen aus Ruhezustand):
- Plist: `~/Library/LaunchAgents/de.ratstermine.update.plist`
- Log: `launchd.log`

```bash
launchctl list | grep ratstermine          # Status prüfen
launchctl start de.ratstermine.update      # Manuell auslösen
```

## Unterstützte Systeme

| System | Anzahl | Methode |
|--------|--------|---------|
| SessionNet (si0046) | 19 | HTML-Parsing mit BeautifulSoup |
| Ratsinfomanagement.net | 10 | iCal-Export parsen |
| Nicht unterstützt | 4 | Bocholt, Ahlen, Ochtrup (defekt), Ladbergen |

## Neuen Scraper hinzufügen

1. Neuen SystemTyp in `config.py` definieren
2. Scraper-Klasse in `scraper/` erstellen (erbt von `BaseScraper`)
3. In `scraper/__init__.py` exportieren
4. In `app.py` bei `hole_alle_termine()` einbinden
