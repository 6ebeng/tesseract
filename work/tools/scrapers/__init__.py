"""
Kurdish News Scrapers Package
Modular scraping framework for Kurdish corpus expansion
"""

from .base_scraper import BaseScraper, SimpleQC
from .kurdsat_scraper import KurdsatScraper
from .rudaw_scraper import RudawScraper
from .khak_scraper import KhakScraper
from .nrt_scraper import NRTScraper
from .awene_scraper import AweneScraper
from .kurdistan24_scraper import Kurdistan24Scraper
from .xendan_scraper import XendanScraper
from .sekokurd_scraper import SekokurdScraper
from .govkrd_scraper import GovKrdScraper
from .sharpress_scraper import SharpressScraper
from .lvinpress_scraper import LvinpressScraper
from .balinde_scraper import BalindeScraper

__all__ = [
    'BaseScraper',
    'SimpleQC',
    'KurdsatScraper',
    'RudawScraper',
    'KhakScraper',
    'NRTScraper',
    'AweneScraper',
    'Kurdistan24Scraper',
    'XendanScraper',
    'SekokurdScraper',
    'GovKrdScraper',
    'SharpressScraper',
    'LvinpressScraper',
    'BalindeScraper',
]

__version__ = '2.0.0'
