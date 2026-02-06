"""Konstanter for Nødvarsel-integrasjonen."""

from __future__ import annotations

import logging
from typing import Final

DOMAIN: Final = "nodvarsel"
LOGGER = logging.getLogger(__package__)

RSS_URL: Final = "https://www.nodvarsel.no/rss/rss-aktive-nodvarsler/"

CONF_SCAN_INTERVAL: Final = "scan_interval"
DEFAULT_SCAN_INTERVAL: Final = 90  # sekunder
MIN_SCAN_INTERVAL: Final = 30
MAX_SCAN_INTERVAL: Final = 600

ATOM_NS: Final = "http://www.w3.org/2005/Atom"

ATTRIBUTION: Final = "Data fra nodvarsel.no"
