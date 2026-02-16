"""Scraper für more!rubin-Systeme auf gremien.info (via iCal-WebCalendar-Export)."""

from .ratsinfo import RatsinfoScraper


class GremienInfoScraper(RatsinfoScraper):
    """Scraper für more!rubin-basierte Ratsinformationssysteme auf gremien.info."""

    def __init__(self, stadt_name: str, base_url: str):
        super().__init__(stadt_name, base_url)
        self.ical_url = f"{self.base_domain}/api.php?id=calendar&action=webcalendar"
