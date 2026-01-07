"""
Web scraping module for fetching gold and silver prices from various businesses.
Uses BeautifulSoup for HTML parsing.
"""

import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any

import requests
from bs4 import BeautifulSoup
from loguru import logger

from config import (
    AssetType,
    AssetUnit,
    BusinessReference,
    BUSINESS_CONFIG,
)
from models import PriceData


class BaseScraper(ABC):
    """Abstract base class for price scrapers."""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the scraper.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        }
    
    def _fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from URL.
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content or None if failed
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def _parse_price(self, price_str: str) -> float:
        """
        Parse price string to float.
        
        Args:
            price_str: Price string (e.g., "15,550,000" or "15550" or "15.550.000")
            
        Returns:
            Price as float
        """
        # Handle Vietnamese number format: dots as thousand separators
        # First, replace Vietnamese format (15.550.000) to plain number
        cleaned = price_str.strip()
        
        # Remove all dots (thousand separators in Vietnamese)
        cleaned = cleaned.replace(".", "")
        
        # Remove commas (thousand separators in some formats)
        cleaned = cleaned.replace(",", "")
        
        # Remove all non-numeric characters
        cleaned = re.sub(r"[^\d]", "", cleaned)
        
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            logger.warning(f"Could not parse price: {price_str}")
            return 0.0
    
    @abstractmethod
    def fetch_price(self) -> Optional[PriceData]:
        """Fetch price data from the business website."""
        pass


class BTMCScraper(BaseScraper):
    """Scraper for Bảo Tín Minh Châu (btmc.vn)."""
    
    def __init__(self):
        super().__init__()
        self.config = BUSINESS_CONFIG[BusinessReference.BAO_TIN_MINH_CHAU.value]
    
    def fetch_price(self) -> Optional[PriceData]:
        """
        Fetch gold price from BTMC.
        
        Returns:
            PriceData object or None if failed
        """
        html = self._fetch_html(self.config["url"])
        if not html:
            return None
        
        try:
            soup = BeautifulSoup(html, "lxml")
            
            # Find the price table - looking for specific text patterns
            tables = soup.find_all("table")
            
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    # Get all text content from the row
                    row_text = row.get_text(strip=True).upper()
                    
                    # Look for "NHẪN TRÒN TRƠN" in the row
                    if "NHẪN TRÒN TRƠN" in row_text and "BẢO TÍN MINH CHÂU" in row_text:
                        cells = row.find_all("td")
                        if len(cells) >= 4:
                            # Buy price is typically in the 4th column (index 3)
                            buy_price = self._parse_price(cells[3].get_text(strip=True))
                            
                            # Apply multiplier (price in 1000 VND)
                            buy_price *= self.config["price_multiplier"]
                            
                            return PriceData(
                                business_name=BusinessReference.BAO_TIN_MINH_CHAU.value,
                                buy_price=buy_price,
                                price_unit=self.config["price_unit"],
                                asset_type=self.config["asset_type"],
                                product_name=self.config["product_name"],
                            )
            
            # Alternative: Look for pattern in any td containing the product name
            all_tds = soup.find_all("td")
            for i, td in enumerate(all_tds):
                td_text = td.get_text(strip=True).upper()
                if "NHẪN TRÒN TRƠN" in td_text:
                    # Try to find price in sibling or nearby cells
                    parent_row = td.find_parent("tr")
                    if parent_row:
                        cells = parent_row.find_all("td")
                        for j, cell in enumerate(cells):
                            cell_text = cell.get_text(strip=True)
                            # Look for a cell that looks like a price (contains digits)
                            if j > 0 and re.match(r"^\d+[\d.,]*$", cell_text.replace(" ", "")):
                                buy_price = self._parse_price(cell_text)
                                if buy_price > 10000:  # Sanity check for gold price
                                    buy_price *= self.config["price_multiplier"]
                                    return PriceData(
                                        business_name=BusinessReference.BAO_TIN_MINH_CHAU.value,
                                        buy_price=buy_price,
                                        price_unit=self.config["price_unit"],
                                        asset_type=self.config["asset_type"],
                                        product_name=self.config["product_name"],
                                    )
            
            logger.warning("Could not find BTMC gold price in table")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing BTMC page: {e}")
            return None


class BTMHScraper(BaseScraper):
    """Scraper for Bảo Tín Mạnh Hải (baotinmanhhai.vn)."""
    
    def __init__(self):
        super().__init__()
        self.config = BUSINESS_CONFIG[BusinessReference.BAO_TIN_MANH_HAI.value]
    
    def fetch_price(self) -> Optional[PriceData]:
        """
        Fetch gold price from BTMH.
        
        Returns:
            PriceData object or None if failed
        """
        html = self._fetch_html(self.config["url"])
        if not html:
            return None
        
        try:
            soup = BeautifulSoup(html, "lxml")
            
            # Find the price table
            tables = soup.find_all("table")
            
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        # Look for "Nhẫn ép vỉ Vàng Rồng Thăng Long"
                        product_text = cells[0].get_text(strip=True)
                        if "Kim Gia Bảo" in product_text and "24K" in product_text:
                            buy_price = self._parse_price(cells[1].get_text(strip=True))
                            
                            # Apply multiplier
                            buy_price *= self.config["price_multiplier"]
                            
                            return PriceData(
                                business_name=BusinessReference.BAO_TIN_MANH_HAI.value,
                                buy_price=buy_price,
                                price_unit=self.config["price_unit"],
                                asset_type=self.config["asset_type"],
                                product_name=self.config["product_name"],
                            )
            
            logger.warning("Could not find BTMH gold price in table")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing BTMH page: {e}")
            return None


class PhuQuyScraper(BaseScraper):
    """Scraper for Phú Quý (giabac.vn / phuquy.com.vn)."""
    
    def __init__(self):
        super().__init__()
        self.config = BUSINESS_CONFIG[BusinessReference.PHU_QUY.value]
        # Try alternative URLs
        self.urls = [
            "https://phuquy.com.vn/",
            "https://www.phuquy.com.vn/gia-vang",
        ]
    
    def fetch_price(self) -> Optional[PriceData]:
        """
        Fetch silver price from Phú Quý.
        Note: Using BTMC prices for Phú Quý silver as fallback.
        
        Returns:
            PriceData object or None if failed
        """
        # Try to get price from BTMC silver table as Phú Quý reference
        html = self._fetch_html("https://btmc.vn/")
        if not html:
            return None
        
        try:
            soup = BeautifulSoup(html, "lxml")
            
            # Find silver price table
            tables = soup.find_all("table")
            
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 3:
                        # Look for "BẠC MIẾNG PHÚ QUÝ Ag 999 1 KG"
                        product_text = cells[0].get_text(strip=True).upper()
                        if "PHÚ QUÝ" in product_text and "1 KG" in product_text:
                            # Parse raw price value
                            raw_price = self._parse_price(cells[1].get_text(strip=True))
                            
                            # If price is less than 10,000,000 VND, multiply by 10
                            if raw_price < 1000000:
                                buy_price = raw_price * 100
                            elif raw_price < 10000000:
                                buy_price = raw_price * 10
                            else:
                                buy_price = raw_price
                            
                            return PriceData(
                                business_name=BusinessReference.PHU_QUY.value,
                                buy_price=buy_price,
                                price_unit=AssetUnit.KILOGRAM,
                                asset_type=AssetType.SILVER,
                                product_name="Bạc thỏi Phú Quý 999 1Kilo",
                            )
            
            logger.warning("Could not find Phu Quy silver price")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Phu Quy page: {e}")
            return None


class PhuTaiScraper(BaseScraper):
    """Scraper for Phú Tài (vangphutai.vn)."""
    
    def __init__(self):
        super().__init__()
        self.config = BUSINESS_CONFIG[BusinessReference.PHU_TAI.value]
    
    def fetch_price(self) -> Optional[PriceData]:
        """
        Fetch gold price from Phú Tài.
        
        Returns:
            PriceData object or None if failed
        """
        html = self._fetch_html(self.config["url"])
        if not html:
            return None
        
        try:
            soup = BeautifulSoup(html, "lxml")
            
            # Find the price table
            tables = soup.find_all("table")
            
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        # Look for "Nhẫn tròn trơn 999.9"
                        product_text = cells[0].get_text(strip=True)
                        if "Nhẫn tròn trơn" in product_text and "999.9" in product_text:
                            buy_price = self._parse_price(cells[1].get_text(strip=True))
                            
                            # Price is in 1000 VND
                            buy_price *= self.config["price_multiplier"]
                            
                            return PriceData(
                                business_name=BusinessReference.PHU_TAI.value,
                                buy_price=buy_price,
                                price_unit=self.config["price_unit"],
                                asset_type=self.config["asset_type"],
                                product_name=self.config["product_name"],
                            )
            
            logger.warning("Could not find Phu Tai gold price in table")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Phu Tai page: {e}")
            return None


class AncaratScraper(BaseScraper):
    """Scraper for Ancarat (giabac.ancarat.com)."""
    
    def __init__(self):
        super().__init__()
        self.config = BUSINESS_CONFIG[BusinessReference.ANCARAT.value]
    
    def fetch_price(self) -> Optional[PriceData]:
        """
        Fetch silver price from Ancarat.
        
        Returns:
            PriceData object or None if failed
        """
        html = self._fetch_html(self.config["url"])
        if not html:
            return None
        
        try:
            soup = BeautifulSoup(html, "lxml")
            
            # Find the price table
            tables = soup.find_all("table")
            
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 3:
                        # Look for "Ngân Long Quảng Tiến 999 - 1 lượng"
                        product_text = cells[0].get_text(strip=True)
                        if "Ngân Long Quảng Tiến" in product_text and "1 lượng" in product_text:
                            # Buy price is in the last column (Mua vào)
                            buy_price = self._parse_price(cells[2].get_text(strip=True))
                            
                            return PriceData(
                                business_name=BusinessReference.ANCARAT.value,
                                buy_price=buy_price,
                                price_unit=self.config["price_unit"],
                                asset_type=self.config["asset_type"],
                                product_name=self.config["product_name"],
                            )
            
            logger.warning("Could not find Ancarat silver price in table")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Ancarat page: {e}")
            return None


class PriceScraperFactory:
    """Factory class to create price scrapers."""
    
    _scrapers: Dict[str, BaseScraper] = {
        BusinessReference.BAO_TIN_MINH_CHAU.value: BTMCScraper(),
        BusinessReference.BAO_TIN_MANH_HAI.value: BTMHScraper(),
        BusinessReference.PHU_QUY.value: PhuQuyScraper(),
        BusinessReference.PHU_TAI.value: PhuTaiScraper(),
        BusinessReference.ANCARAT.value: AncaratScraper(),
    }
    
    @classmethod
    def get_scraper(cls, business_name: str) -> Optional[BaseScraper]:
        """
        Get scraper for a specific business.
        
        Args:
            business_name: Name of the business
            
        Returns:
            Scraper instance or None if not found
        """
        return cls._scrapers.get(business_name)
    
    @classmethod
    def fetch_all_prices(cls) -> Dict[str, Optional[PriceData]]:
        """
        Fetch prices from all businesses.
        
        Returns:
            Dictionary of business name to PriceData
        """
        prices = {}
        
        for business_name, scraper in cls._scrapers.items():
            logger.info(f"Fetching price from {business_name}...")
            try:
                price_data = scraper.fetch_price()
                prices[business_name] = price_data
                if price_data:
                    logger.info(
                        f"  {business_name}: {price_data.buy_price:,.0f} VND/{price_data.price_unit}"
                    )
                else:
                    logger.warning(f"  {business_name}: Failed to fetch price")
            except Exception as e:
                logger.error(f"  {business_name}: Error - {e}")
                prices[business_name] = None
        
        return prices
    
    @classmethod
    def fetch_price(cls, business_name: str) -> Optional[PriceData]:
        """
        Fetch price from a specific business.
        
        Args:
            business_name: Name of the business
            
        Returns:
            PriceData or None if failed
        """
        scraper = cls.get_scraper(business_name)
        if scraper:
            return scraper.fetch_price()
        return None


# Utility function for testing
def test_scrapers():
    """Test all scrapers and print results."""
    from loguru import logger
    import sys
    
    # Configure logger
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    print("\n" + "=" * 60)
    print("Testing Price Scrapers")
    print("=" * 60 + "\n")
    
    prices = PriceScraperFactory.fetch_all_prices()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    for business, price_data in prices.items():
        if price_data:
            print(f"✓ {business}: {price_data.buy_price:,.0f} VND/{price_data.price_unit}")
        else:
            print(f"✗ {business}: Failed")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_scrapers()
