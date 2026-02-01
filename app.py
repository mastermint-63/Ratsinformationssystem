#!/usr/bin/env python3
"""
Ratstermine Dashboard - Sitzungstermine aus dem Münsterland
Sammelt Termine von allen Ratsinformationssystemen und generiert ein HTML-Dashboard.

Verwendung:
    python3 app.py              # Generiert aktuellen + 2 weitere Monate
    python3 app.py 2026 2       # Generiert ab Februar 2026 (3 Monate)
    python3 app.py 2026 2 6     # Generiert 6 Monate ab Februar 2026
"""

import os
import webbrowser
import calendar
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import STAEDTE, SystemTyp, get_staedte_nach_typ
from scraper import SessionNetScraper, RatsinfoScraper, Termin


def dateiname_fuer_monat(jahr: int, monat: int) -> str:
    """Generiert den Dateinamen für einen Monat."""
    return f"termine_{jahr}_{monat:02d}.html"


def hole_alle_termine(jahr: int, monat: int) -> tuple[list[Termin], list[str]]:
    """Holt Termine von allen unterstützten Städten parallel.

    Returns:
        Tuple aus (Termine-Liste, Liste fehlgeschlagener Städtenamen)
    """
    termine = []
    fehler_staedte = []
    scraper_aufgaben = []

    # SessionNet-Städte
    for stadt in get_staedte_nach_typ(SystemTyp.SESSIONNET):
        scraper_aufgaben.append((SessionNetScraper(stadt.name, stadt.url), jahr, monat))

    # Ratsinfomanagement-Städte
    for stadt in get_staedte_nach_typ(SystemTyp.RATSINFO):
        scraper_aufgaben.append((RatsinfoScraper(stadt.name, stadt.url), jahr, monat))

    # Parallel abrufen
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(scraper.hole_termine, j, m): scraper
            for scraper, j, m in scraper_aufgaben
        }

        for future in as_completed(futures):
            scraper = futures[future]
            try:
                result = future.result()
                termine.extend(result)
                if result:
                    print(f"  {scraper.stadt_name}: {len(result)} Termine")
            except Exception as e:
                print(f"  Fehler bei {scraper.stadt_name}: {e}")
                fehler_staedte.append(scraper.stadt_name)

    # Nach Datum sortieren
    termine.sort()
    return termine, fehler_staedte


def generiere_kalender(jahr: int, monat: int, tage_mit_terminen: set[int]) -> str:
    """Generiert ein Kalenderblatt als HTML-Tabelle."""
    cal = calendar.Calendar(firstweekday=0)  # Montag = 0
    wochen = cal.monthdayscalendar(jahr, monat)

    html = '<table class="kalender" id="kalender">\n'
    html += '<tr>'
    for tag_name in ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']:
        html += f'<th>{tag_name}</th>'
    html += '</tr>\n'

    for woche in wochen:
        html += '<tr>'
        for tag in woche:
            if tag == 0:
                html += '<td></td>'
            elif tag in tage_mit_terminen:
                datum_key = f"{jahr}-{monat:02d}-{tag:02d}"
                html += f'<td><a href="#datum-{datum_key}" class="kal-link">{tag}</a></td>'
            else:
                html += f'<td class="kal-leer">{tag}</td>'
        html += '</tr>\n'

    html += '</table>'
    return html


def generiere_html(termine: list[Termin], jahr: int, monat: int,
                   verfuegbare_monate: list[tuple[int, int]]) -> str:
    """Generiert das HTML-Dashboard.

    Args:
        termine: Liste der Termine
        jahr: Aktuelles Jahr
        monat: Aktueller Monat
        verfuegbare_monate: Liste von (jahr, monat) Tupeln für die Navigation
    """
    monatsnamen = [
        '', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
        'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
    ]

    # Termine nach Datum gruppieren
    termine_nach_datum = {}
    for t in termine:
        datum_key = t.datum.strftime('%Y-%m-%d')
        if datum_key not in termine_nach_datum:
            termine_nach_datum[datum_key] = []
        termine_nach_datum[datum_key].append(t)

    # Alle Städte für Filter sammeln
    alle_staedte = sorted(set(t.stadt for t in termine))

    # Termine-HTML generieren
    termine_html = ""
    for datum_key in sorted(termine_nach_datum.keys()):
        tage_termine = termine_nach_datum[datum_key]
        datum_obj = datetime.strptime(datum_key, '%Y-%m-%d')
        datum_formatiert = tage_termine[0].datum_formatiert()

        termine_html += f'''
        <div class="datum-gruppe" id="datum-{datum_key}">
            <div class="datum-header">{datum_formatiert}</div>
            <div class="termine-liste">
        '''

        for t in sorted(tage_termine, key=lambda x: x.uhrzeit):
            abgesagt_class = ' abgesagt' if '[ABGESAGT]' in t.gremium else ''
            gremium_clean = t.gremium.replace('[ABGESAGT]', '').strip()

            termine_html += f'''
                <div class="termin{abgesagt_class}" data-stadt="{t.stadt}">
                    <div class="termin-zeit">{t.uhrzeit}</div>
                    <div class="termin-info">
                        <div class="termin-gremium">
                            <a href="{t.link}" target="_blank">{gremium_clean}</a>
                        </div>
                        <div class="termin-stadt">{t.stadt}</div>
                        {f'<div class="termin-ort">{t.ort}</div>' if t.ort else ''}
                    </div>
                </div>
            '''

        termine_html += '''
            </div>
            <div class="zurueck-link"><a href="#kalender">↑ Kalender</a></div>
        </div>
        '''

    # Filter-Optionen generieren
    filter_html = '<option value="">Alle Städte</option>'
    for stadt in alle_staedte:
        filter_html += f'<option value="{stadt}">{stadt}</option>'

    # Monatsnavigation
    prev_monat = monat - 1 if monat > 1 else 12
    prev_jahr = jahr if monat > 1 else jahr - 1
    next_monat = monat + 1 if monat < 12 else 1
    next_jahr = jahr if monat < 12 else jahr + 1

    # Prüfen ob vorheriger/nächster Monat verfügbar ist
    prev_verfuegbar = (prev_jahr, prev_monat) in verfuegbare_monate
    next_verfuegbar = (next_jahr, next_monat) in verfuegbare_monate

    prev_link = dateiname_fuer_monat(prev_jahr, prev_monat) if prev_verfuegbar else "#"
    next_link = dateiname_fuer_monat(next_jahr, next_monat) if next_verfuegbar else "#"

    prev_class = "" if prev_verfuegbar else " disabled"
    next_class = "" if next_verfuegbar else " disabled"

    # Kalenderblatt generieren
    tage_mit_terminen = set(int(k.split('-')[2]) for k in termine_nach_datum.keys())
    kalender_html = generiere_kalender(jahr, monat, tage_mit_terminen)

    html = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ratstermine {monatsnamen[monat]} {jahr}</title>
    <style>
        :root {{
            --bg-color: #f5f5f7;
            --card-bg: #ffffff;
            --text-color: #1d1d1f;
            --text-secondary: #86868b;
            --border-color: #d2d2d7;
            --accent-color: #0066cc;
            --hover-color: #f0f0f5;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg-color: #1d1d1f;
                --card-bg: #2d2d2f;
                --text-color: #f5f5f7;
                --text-secondary: #a1a1a6;
                --border-color: #424245;
                --accent-color: #2997ff;
                --hover-color: #3a3a3c;
            }}
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-color);
            color: var(--text-color);
            line-height: 1.5;
            padding: 20px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 30px;
        }}

        h1 {{
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 10px;
        }}

        .nav {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
        }}

        .nav-btn {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            color: var(--accent-color);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            text-decoration: none;
        }}

        .nav-btn:hover {{
            background: var(--hover-color);
        }}

        .nav-btn.disabled {{
            opacity: 0.3;
            pointer-events: none;
            cursor: default;
        }}

        .monat-titel {{
            font-size: 1.2rem;
            font-weight: 500;
        }}

        .filter-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 10px 15px;
            background: var(--card-bg);
            border-radius: 10px;
            border: 1px solid var(--border-color);
        }}

        .filter-bar select {{
            padding: 8px 12px;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            background: var(--bg-color);
            color: var(--text-color);
            font-size: 14px;
        }}

        .stats {{
            font-size: 14px;
            color: var(--text-secondary);
        }}

        .datum-gruppe {{
            margin-bottom: 20px;
        }}

        .datum-header {{
            font-weight: 600;
            font-size: 1rem;
            padding: 10px 15px;
            background: var(--accent-color);
            color: white;
            border-radius: 10px 10px 0 0;
        }}

        .termine-liste {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-top: none;
            border-radius: 0 0 10px 10px;
        }}

        .termin {{
            display: flex;
            padding: 12px 15px;
            border-bottom: 1px solid var(--border-color);
            transition: background 0.2s;
        }}

        .termin:last-child {{
            border-bottom: none;
        }}

        .termin:hover {{
            background: var(--hover-color);
        }}

        .termin.abgesagt {{
            opacity: 0.5;
            text-decoration: line-through;
        }}

        .termin-zeit {{
            width: 80px;
            font-weight: 500;
            color: var(--accent-color);
            flex-shrink: 0;
        }}

        .termin-info {{
            flex: 1;
        }}

        .termin-gremium {{
            font-weight: 500;
            margin-bottom: 2px;
        }}

        .termin-gremium a {{
            color: var(--text-color);
            text-decoration: none;
        }}

        .termin-gremium a:hover {{
            color: var(--accent-color);
            text-decoration: underline;
        }}

        .termin-stadt {{
            font-size: 13px;
            color: var(--text-secondary);
        }}

        .termin-ort {{
            font-size: 12px;
            color: var(--text-secondary);
            font-style: italic;
        }}

        .kalender {{
            width: 100%;
            max-width: 400px;
            margin: 0 auto 25px;
            border-collapse: collapse;
            text-align: center;
        }}

        .kalender th {{
            padding: 6px;
            font-size: 13px;
            color: var(--text-secondary);
            font-weight: 500;
        }}

        .kalender td {{
            padding: 6px;
            font-size: 14px;
            border-radius: 6px;
        }}

        .kalender .kal-leer {{
            color: var(--text-secondary);
            opacity: 0.5;
        }}

        .kalender .kal-link {{
            display: inline-block;
            width: 32px;
            height: 32px;
            line-height: 32px;
            border-radius: 50%;
            background: var(--accent-color);
            color: white;
            text-decoration: none;
            font-weight: 600;
        }}

        .kalender .kal-link:hover {{
            opacity: 0.8;
        }}

        .zurueck-link {{
            text-align: right;
            padding: 6px 15px;
            font-size: 13px;
        }}

        .zurueck-link a {{
            color: var(--accent-color);
            text-decoration: none;
            font-weight: 500;
        }}

        .zurueck-link a:hover {{
            color: var(--accent-color);
        }}

        .keine-termine {{
            text-align: center;
            padding: 40px;
            color: var(--text-secondary);
        }}

        .hidden {{
            display: none !important;
        }}

        footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: var(--text-secondary);
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Ratstermine Münsterland</h1>
            <div class="nav">
                <a href="{prev_link}" class="nav-btn{prev_class}">&larr; {monatsnamen[prev_monat]}</a>
                <span class="monat-titel">{monatsnamen[monat]} {jahr}</span>
                <a href="{next_link}" class="nav-btn{next_class}">{monatsnamen[next_monat]} &rarr;</a>
            </div>
        </header>

        {kalender_html}

        <div class="filter-bar">
            <select id="stadt-filter" onchange="filterTermine()">
                {filter_html}
            </select>
            <div class="stats">
                <span id="termine-count">{len(termine)}</span> Termine von <span id="staedte-count">{len(alle_staedte)}</span> Kommunen
            </div>
        </div>

        <main id="termine-container">
            {termine_html if termine else '<div class="keine-termine">Keine Termine gefunden</div>'}
        </main>

        <footer>
            Generiert am {datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')}<br>
            Daten aus {len(alle_staedte)} Ratsinformationssystemen
        </footer>
    </div>

    <script>
        function filterTermine() {{
            const filter = document.getElementById('stadt-filter').value;
            const termine = document.querySelectorAll('.termin');
            let sichtbar = 0;

            termine.forEach(t => {{
                if (!filter || t.dataset.stadt === filter) {{
                    t.classList.remove('hidden');
                    sichtbar++;
                }} else {{
                    t.classList.add('hidden');
                }}
            }});

            document.getElementById('termine-count').textContent = sichtbar;

            // Leere Datum-Gruppen ausblenden
            document.querySelectorAll('.datum-gruppe').forEach(g => {{
                const sichtbareTermine = g.querySelectorAll('.termin:not(.hidden)');
                g.classList.toggle('hidden', sichtbareTermine.length === 0);
            }});
        }}
    </script>
</body>
</html>'''

    return html


def berechne_monate(start_jahr: int, start_monat: int, anzahl: int) -> list[tuple[int, int]]:
    """Berechnet eine Liste von (jahr, monat) Tupeln."""
    monate = []
    jahr, monat = start_jahr, start_monat
    for _ in range(anzahl):
        monate.append((jahr, monat))
        monat += 1
        if monat > 12:
            monat = 1
            jahr += 1
    return monate


def main():
    """Hauptfunktion."""
    import sys

    # --no-browser Flag prüfen
    no_browser = '--no-browser' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]

    # Parameter: Jahr, Monat, Anzahl Monate (optional)
    jetzt = datetime.now()
    jahr = int(args[0]) if len(args) > 0 else jetzt.year
    monat = int(args[1]) if len(args) > 1 else jetzt.month
    anzahl_monate = int(args[2]) if len(args) > 2 else 3

    # Liste der zu generierenden Monate
    monate_liste = berechne_monate(jahr, monat, anzahl_monate)

    print(f"Generiere {anzahl_monate} Monate ab {monat}/{jahr}...")
    print("=" * 50)

    basis_pfad = os.path.dirname(__file__)
    erster_dateiname = None
    alle_fehler = []

    for idx, (j, m) in enumerate(monate_liste):
        monatsnamen = ['', 'Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
        print(f"\n[{idx+1}/{anzahl_monate}] {monatsnamen[m]} {j}:")

        termine, fehler_staedte = hole_alle_termine(j, m)
        alle_fehler.extend(fehler_staedte)
        print(f"  → {len(termine)} Termine gefunden")

        # HTML generieren
        html = generiere_html(termine, j, m, monate_liste)

        # Datei speichern
        dateiname = dateiname_fuer_monat(j, m)
        ausgabe_pfad = os.path.join(basis_pfad, dateiname)
        with open(ausgabe_pfad, 'w', encoding='utf-8') as f:
            f.write(html)

        if idx == 0:
            erster_dateiname = ausgabe_pfad

    print("\n" + "=" * 50)
    print(f"Fertig! {anzahl_monate} Dateien generiert.")

    # Fehlerbericht ausgeben
    if alle_fehler:
        eindeutige_fehler = sorted(set(alle_fehler))
        print(f"\nFEHLER: {len(eindeutige_fehler)} Städte nicht erreichbar: {', '.join(eindeutige_fehler)}")

    # Ersten Monat im Browser öffnen (außer bei --no-browser)
    if erster_dateiname and not no_browser:
        webbrowser.open(f'file://{erster_dateiname}')


if __name__ == '__main__':
    main()
