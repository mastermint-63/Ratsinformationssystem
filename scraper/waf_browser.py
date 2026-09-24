"""iCal-Abruf per echtem Browser für Ratsinfosysteme hinter der rescaled-WAF.

Seit 09/2026 verlangen die meisten *.ratsinfomanagement.net-Systeme (und
ratsinfo.bocholt.de) eine JavaScript-Browserprüfung. Einfache HTTP-Abrufe
(requests) erhalten nur die Prüfseite, Headless-Chromium wird abgewiesen und
löst eine vorübergehende Sperre der IP aus.

Deshalb: ein normales Chromium-Fenster (außerhalb des Bildschirms), Kommunen
strikt nacheinander mit Pause, iCal per fetch() aus der Seite heraus. Jede
Kommune wird pro Lauf genau einmal abgerufen (vorher: einmal pro Monat).

Erkennung: Der Hostname löst per DNS auf *.waf.rescaled.com auf.
"""
import asyncio
import socket
import time
from urllib.parse import urlparse

WAF_TITLE_MARKER = "rescaled WAF"
WAF_BLOCK_MARKERS = ("blockiert", "Blocked")
OFFSCREEN_ARGS = ["--window-position=-2400,-2400", "--window-size=1280,900"]
CHALLENGE_TIMEOUT_S = 25
PAUSE_ZWISCHEN_KOMMUNEN_S = 3

_JS_FETCH_TEXT = """async (u) => {
  try {
    const r = await fetch(u, {credentials: 'include', redirect: 'error'});
    return {status: r.status, text: await r.text()};
  } catch (e) {
    return {status: 0, text: String(e)};
  }
}"""

# Ergebnis des Vorab-Abrufs: iCal-URL -> Text oder Exception
ICS_CACHE: dict[str, object] = {}


class WafGesperrt(Exception):
    """Die WAF sperrt diese IP für die Kommune vorübergehend."""


def hinter_waf(url: str) -> bool:
    host = urlparse(url).hostname or ""
    try:
        return "waf.rescaled.com" in socket.gethostbyname_ex(host)[0]
    except OSError:
        return False


async def _titel(page) -> str:
    for _ in range(6):
        try:
            return await page.title()
        except Exception:
            await asyncio.sleep(0.5)
    return ""


async def _pruefung_bestehen(page, start_url: str) -> None:
    await page.goto(start_url, timeout=30000)
    titel = await _titel(page)
    ende = time.monotonic() + CHALLENGE_TIMEOUT_S
    while WAF_TITLE_MARKER in titel:
        if any(m in titel for m in WAF_BLOCK_MARKERS):
            raise WafGesperrt(f"WAF-Sperre ({urlparse(start_url).hostname})")
        if time.monotonic() > ende:
            raise WafGesperrt(f"WAF-Prüfung nicht abgeschlossen ({urlparse(start_url).hostname})")
        await asyncio.sleep(1)
        titel = await _titel(page)


async def _hole_alle(ics_urls: list[str], log) -> dict[str, object]:
    from playwright.async_api import async_playwright

    ergebnis: dict[str, object] = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=OFFSCREEN_ARGS)
        try:
            for i, ics in enumerate(ics_urls):
                if i:
                    await asyncio.sleep(PAUSE_ZWISCHEN_KOMMUNEN_S)
                parsed = urlparse(ics)
                start = f"{parsed.scheme}://{parsed.netloc}/"
                ctx = await browser.new_context(locale="de-DE")
                page = await ctx.new_page()
                try:
                    await _pruefung_bestehen(page, start)
                    res = await page.evaluate(_JS_FETCH_TEXT, ics)
                    text = res.get("text", "")
                    if res.get("status") != 200 or "BEGIN:VCALENDAR" not in text:
                        raise RuntimeError(f"iCal HTTP {res.get('status')} ({parsed.hostname})")
                    ergebnis[ics] = text
                except Exception as e:  # pro Kommune isolieren
                    ergebnis[ics] = e
                    log(f"  Browser-Abruf fehlgeschlagen: {parsed.hostname}: {e}")
                finally:
                    await ctx.close()
        finally:
            await browser.close()
    return ergebnis


def vorab_abrufen(ics_urls: list[str], log=print) -> None:
    """Holt alle iCal-Feeds hinter der WAF einmal per Browser in ICS_CACHE."""
    urls = [u for u in dict.fromkeys(ics_urls) if hinter_waf(u)]
    if not urls:
        return
    log(f"WAF: {len(urls)} Kommunen per Browser abrufen (nacheinander, {PAUSE_ZWISCHEN_KOMMUNEN_S}s Pause)...")
    try:
        ICS_CACHE.update(asyncio.run(_hole_alle(urls, log)))
    except ImportError:
        fehler = RuntimeError("Playwright nicht installiert - Browser-Abruf nicht möglich")
        ICS_CACHE.update({u: fehler for u in urls})
        log(f"  FEHLER: {fehler}")
    except Exception as e:
        # z.B. Browser startet nicht: alle als Fehler markieren, nicht per requests nachhämmern
        ICS_CACHE.update({u: e for u in urls if u not in ICS_CACHE})
        log(f"  FEHLER beim Browser-Abruf: {e}")
    ok = sum(1 for u in urls if isinstance(ICS_CACHE.get(u), str))
    log(f"WAF: {ok}/{len(urls)} Kommunen erfolgreich per Browser abgerufen")
