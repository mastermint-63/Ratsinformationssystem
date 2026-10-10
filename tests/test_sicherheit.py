"""XSS-/RSS-Regressionstests (Audit 10.10.2026, Befunde #4 und #12).

Termine kommen aus fremden iCal-Feeds und HTML-Seiten der Kommunen. Links
duerfen nur mit http(s)-Schema klickbar werden, Textfelder werden escaped,
der RSS-Feed bleibt valides XML.
"""
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from app import generiere_html, generiere_rss
from scraper.base import Termin


def _termin(**kwargs):
    defaults = dict(
        stadt='Münster', datum=datetime(2026, 10, 12, 17), uhrzeit='17:00',
        gremium='Rat', ort='Rathaus', link='https://www.stadt-muenster.de/sessionnet/si0057.php?__ksinr=1&x=2',
    )
    defaults.update(kwargs)
    return Termin(**defaults)


@pytest.mark.parametrize(
    "link",
    ['javascript:alert(1)', 'JaVaScRiPt:alert(1)', ' javascript:alert(1)', '\tjavascript:alert(1)',
     'java\nscript:alert(1)', 'data:text/html,<script>alert(1)</script>', 'vbscript:x', '//evil.example/x'],
)
def test_nicht_http_link_wird_verworfen(link):
    t = _termin(link=link)
    assert t.link == ''
    html = generiere_html([t], 2026, 10, [(2026, 10)])
    low = html.lower()
    assert 'href="javascript' not in low
    assert 'href=" javascript' not in low
    assert 'href="data:' not in low
    assert 'href="vbscript' not in low
    assert 'ratsinfo-lesen.reporter.ruhr/?url=' not in html
    # Gremium bleibt als Text sichtbar
    assert 'Rat' in html


def test_http_link_bleibt_und_wird_escaped():
    t = _termin(link='https://example.org/a"onmouseover="alert(1)')
    html = generiere_html([t], 2026, 10, [(2026, 10)])
    assert '"onmouseover="' not in html
    assert 'href="https://example.org/a&quot;onmouseover=&quot;alert(1)"' in html


def test_script_in_textfeldern_wird_escaped():
    t = _termin(gremium='<script>alert("g")</script>', ort='<script>alert("o")</script>',
                uhrzeit='<b>17</b>')
    html = generiere_html([t], 2026, 10, [(2026, 10)])
    assert '<script>alert(' not in html
    assert '&lt;script&gt;alert(' in html
    assert '<b>17</b>' not in html


def test_rss_bleibt_valides_xml_bei_sonderzeichen():
    t = _termin(gremium='Ausschuss <Bau> & "Planung"', ort='Saal <1> & 2',
                link='https://x.example/si0057.php?a=1&b=<2>')
    t2 = _termin(link='javascript:alert(1)', gremium='Ohne Link & Co')
    xml = generiere_rss([t, t2], 2026, 10)
    root = ET.fromstring(xml)  # wirft bei ungueltigem XML
    items = root.findall('./channel/item')
    assert items[0].find('link').text == 'https://x.example/si0057.php?a=1&b=<2>'
    assert 'Ausschuss <Bau> & "Planung"' in items[0].find('title').text
    assert items[1].find('link') is None
    assert '&' in items[1].find('guid').text


def test_client_js_nutzt_kein_innerhtml_mit_eingaben():
    html = generiere_html([_termin()], 2026, 10, [(2026, 10)])
    script = html.split('<script>')[-1]
    assert '${searchTerm}' not in script
    assert "removeFilter('${stadt}')" not in script
    assert 'innerHTML = staedte' not in script
