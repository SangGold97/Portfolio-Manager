"""
Price service module for managing prices and calculating asset valuations.
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from loguru import logger

from config import (
    AssetType,
    AssetUnit,
    AssetCategory,
    UnitConversion,
    BusinessReference,
    BUSINESS_CONFIG,
)
from models import (
    PriceData,
    ExistingAsset,
    InvestmentAsset,
    AssetValuation,
    PortfolioSummary,
    PriceHistory,
)
from scraper import PriceScraperFactory


class UnitConverter:
    """Utility class for converting between different units."""
    
    @staticmethod
    def convert_to_chi(quantity: float, from_unit: AssetUnit) -> float:
        """
        Convert quantity to chi (chỉ) unit.
        
        Args:
            quantity: Amount to convert
            from_unit: Source unit
            
        Returns:
            Quantity in chi
        """
        if from_unit == AssetUnit.CHI:
            return quantity
        elif from_unit == AssetUnit.LUONG:
            return quantity * UnitConversion.LUONG_TO_CHI
        elif from_unit == AssetUnit.KILOGRAM:
            return quantity * UnitConversion.KG_TO_CHI
        return quantity
    
    @staticmethod
    def convert_to_luong(quantity: float, from_unit: AssetUnit) -> float:
        """
        Convert quantity to lượng unit.
        
        Args:
            quantity: Amount to convert
            from_unit: Source unit
            
        Returns:
            Quantity in luong
        """
        if from_unit == AssetUnit.LUONG:
            return quantity
        elif from_unit == AssetUnit.CHI:
            return quantity * UnitConversion.CHI_TO_LUONG
        elif from_unit == AssetUnit.KILOGRAM:
            return quantity * UnitConversion.KG_TO_LUONG
        return quantity
    
    @staticmethod
    def convert_to_kg(quantity: float, from_unit: AssetUnit) -> float:
        """
        Convert quantity to kilogram unit.
        
        Args:
            quantity: Amount to convert
            from_unit: Source unit
            
        Returns:
            Quantity in kg
        """
        if from_unit == AssetUnit.KILOGRAM:
            return quantity
        elif from_unit == AssetUnit.CHI:
            return quantity * UnitConversion.CHI_TO_KG
        elif from_unit == AssetUnit.LUONG:
            return quantity * UnitConversion.LUONG_TO_KG
        return quantity
    
    @staticmethod
    def convert_price_to_unit(
        price: float,
        from_unit: AssetUnit,
        to_unit: AssetUnit
    ) -> float:
        """
        Convert price from one unit to another.
        
        Args:
            price: Price per unit
            from_unit: Source price unit
            to_unit: Target price unit
            
        Returns:
            Price per target unit
        """
        # Convert 1 unit of to_unit to from_unit
        if from_unit == to_unit:
            return price
        
        # Calculate conversion factor
        if from_unit == AssetUnit.CHI:
            if to_unit == AssetUnit.LUONG:
                return price * UnitConversion.LUONG_TO_CHI  # Multiply by 10
            elif to_unit == AssetUnit.KILOGRAM:
                return price * UnitConversion.KG_TO_CHI  # Multiply by 266.7
        
        elif from_unit == AssetUnit.LUONG:
            if to_unit == AssetUnit.CHI:
                return price * UnitConversion.CHI_TO_LUONG  # Multiply by 0.1
            elif to_unit == AssetUnit.KILOGRAM:
                return price * UnitConversion.KG_TO_LUONG  # Multiply by 26.67
        
        elif from_unit == AssetUnit.KILOGRAM:
            if to_unit == AssetUnit.CHI:
                return price * UnitConversion.CHI_TO_KG  # Multiply by 0.00375
            elif to_unit == AssetUnit.LUONG:
                return price * UnitConversion.LUONG_TO_KG  # Multiply by 0.0375
        
        return price


class PriceService:
    """Service for managing prices and calculating valuations."""
    
    def __init__(self):
        """Initialize the price service."""
        self._cached_prices: Dict[str, PriceData] = {}
        self._price_history: List[PriceHistory] = []
        self._last_refresh: Optional[datetime] = None
    
    def refresh_prices(self) -> Dict[str, Optional[PriceData]]:
        """
        Refresh all prices from web sources.
        
        Returns:
            Dictionary of business name to PriceData
        """
        logger.info("Refreshing prices from all sources...")
        
        # Fetch all prices
        prices = PriceScraperFactory.fetch_all_prices()
        
        # Update cache
        for business_name, price_data in prices.items():
            if price_data:
                self._cached_prices[business_name] = price_data
                
                # Add to history
                self._price_history.append(
                    PriceHistory(
                        business_name=business_name,
                        asset_type=price_data.asset_type,
                        price=price_data.buy_price,
                        timestamp=datetime.now(),
                    )
                )
        
        self._last_refresh = datetime.now()
        logger.info(f"Prices refreshed at {self._last_refresh}")
        
        return prices
    
    def get_cached_price(self, business_name: str) -> Optional[PriceData]:
        """
        Get cached price for a business.
        
        Args:
            business_name: Name of the business
            
        Returns:
            Cached PriceData or None
        """
        return self._cached_prices.get(business_name)
    
    def get_all_cached_prices(self) -> Dict[str, PriceData]:
        """
        Get all cached prices.
        
        Returns:
            Dictionary of cached prices
        """
        return self._cached_prices.copy()
    
    def get_last_refresh_time(self) -> Optional[datetime]:
        """Get the last refresh timestamp."""
        return self._last_refresh
    
    def calculate_current_value(
        self,
        quantity: float,
        unit: AssetUnit,
        business_name: str,
    ) -> Tuple[float, float]:
        """
        Calculate current value of an asset.
        
        Args:
            quantity: Quantity of asset
            unit: Unit of measurement
            business_name: Reference business for pricing
            
        Returns:
            Tuple of (current_price_per_unit, total_value)
        """
        # Get price data
        price_data = self._cached_prices.get(business_name)
        if not price_data:
            logger.warning(f"No cached price for {business_name}")
            return 0.0, 0.0
        
        # Convert price to asset's unit
        price_per_unit = UnitConverter.convert_price_to_unit(
            price_data.buy_price,
            price_data.price_unit,
            unit
        )
        
        # Calculate total value
        total_value = quantity * price_per_unit
        
        return price_per_unit, total_value
    
    def calculate_profit_loss(
        self,
        purchase_price: float,
        current_price: float,
        quantity: float,
    ) -> Tuple[float, float]:
        """
        Calculate profit/loss for an investment.
        
        Args:
            purchase_price: Purchase price per unit
            current_price: Current price per unit
            quantity: Quantity of asset
            
        Returns:
            Tuple of (profit_loss_vnd, profit_loss_percent)
        """
        # Calculate total costs and current value
        total_cost = purchase_price * quantity
        current_value = current_price * quantity
        
        # Calculate profit/loss
        profit_loss_vnd = current_value - total_cost
        
        # Calculate percentage
        if total_cost > 0:
            profit_loss_percent = round((profit_loss_vnd / total_cost) * 100, 2)
        else:
            profit_loss_percent = 0.0
        
        return profit_loss_vnd, profit_loss_percent
    
    def calculate_holding_months(self, purchase_date: date) -> float:
        """
        Calculate holding period in months.
        
        Args:
            purchase_date: Date of purchase
            
        Returns:
            Holding period in months (rounded to 2 decimal places)
        """
        today = date.today()
        
        # Calculate difference in days
        delta = today - purchase_date
        
        # Convert to months (approximately 30.44 days per month)
        months = delta.days / 30.44
        
        return round(months, 2)
    
    def valuate_existing_asset(
        self,
        asset: ExistingAsset,
    ) -> Optional[AssetValuation]:
        """
        Calculate valuation for an existing asset.
        
        Args:
            asset: The existing asset to valuate
            
        Returns:
            AssetValuation object or None if price not available
        """
        # Get current price and value
        current_price, current_value = self.calculate_current_value(
            asset.quantity,
            asset.unit,
            asset.reference,
        )
        
        if current_price == 0:
            return None
        
        return AssetValuation(
            asset_id=asset.id,
            asset_name=asset.name,
            asset_type=asset.asset_type,
            category=AssetCategory.EXISTING,
            quantity=asset.quantity,
            unit=asset.unit,
            reference=asset.reference,
            current_price=current_price,
            current_value=current_value,
        )
    
    def valuate_investment_asset(
        self,
        asset: InvestmentAsset,
    ) -> Optional[AssetValuation]:
        """
        Calculate valuation for an investment asset.
        
        Args:
            asset: The investment asset to valuate
            
        Returns:
            AssetValuation object or None if price not available
        """
        # Get current price and value
        current_price, current_value = self.calculate_current_value(
            asset.quantity,
            asset.unit,
            asset.reference,
        )
        
        if current_price == 0:
            return None
        
        # Calculate profit/loss
        profit_loss_vnd, profit_loss_percent = self.calculate_profit_loss(
            asset.purchase_price,
            current_price,
            asset.quantity,
        )
        
        # Calculate holding months
        holding_months = self.calculate_holding_months(asset.purchase_date)
        
        return AssetValuation(
            asset_id=asset.id,
            asset_name=asset.name,
            asset_type=asset.asset_type,
            category=AssetCategory.INVESTMENT,
            quantity=asset.quantity,
            unit=asset.unit,
            reference=asset.reference,
            purchase_price=asset.purchase_price,
            purchase_date=asset.purchase_date,
            current_price=current_price,
            current_value=current_value,
            profit_loss_vnd=profit_loss_vnd,
            profit_loss_percent=profit_loss_percent,
            holding_months=holding_months,
        )
    
    def calculate_portfolio_summary(
        self,
        existing_valuations: List[AssetValuation],
        investment_valuations: List[AssetValuation],
    ) -> PortfolioSummary:
        """
        Calculate portfolio summary from valuations.
        
        Args:
            existing_valuations: List of existing asset valuations
            investment_valuations: List of investment asset valuations
            
        Returns:
            PortfolioSummary object
        """
        # Calculate totals
        total_existing_value = sum(v.current_value for v in existing_valuations)
        total_investment_value = sum(v.current_value for v in investment_valuations)
        
        # Calculate gold/silver totals
        all_valuations = existing_valuations + investment_valuations
        total_gold = sum(
            v.current_value for v in all_valuations
            if v.asset_type == AssetType.GOLD
        )
        total_silver = sum(
            v.current_value for v in all_valuations
            if v.asset_type == AssetType.SILVER
        )
        
        # Calculate total profit/loss from investments
        total_profit_loss = sum(
            v.profit_loss_vnd or 0 for v in investment_valuations
        )
        
        # Calculate total profit/loss percentage
        total_investment_cost = sum(
            (v.purchase_price or 0) * v.quantity
            for v in investment_valuations
        )
        
        if total_investment_cost > 0:
            total_profit_loss_percent = round(
                (total_profit_loss / total_investment_cost) * 100, 2
            )
        else:
            total_profit_loss_percent = 0.0
        
        return PortfolioSummary(
            total_existing_value=total_existing_value,
            total_investment_value=total_investment_value,
            total_portfolio_value=total_existing_value + total_investment_value,
            total_gold_value=total_gold,
            total_silver_value=total_silver,
            total_profit_loss_vnd=total_profit_loss,
            total_profit_loss_percent=total_profit_loss_percent,
            existing_asset_count=len(existing_valuations),
            investment_asset_count=len(investment_valuations),
        )
    
    def get_price_history(
        self,
        business_name: Optional[str] = None,
        asset_type: Optional[AssetType] = None,
    ) -> List[PriceHistory]:
        """
        Get price history with optional filters.
        
        Args:
            business_name: Filter by business name
            asset_type: Filter by asset type
            
        Returns:
            Filtered list of price history
        """
        history = self._price_history.copy()
        
        if business_name:
            history = [h for h in history if h.business_name == business_name]
        
        if asset_type:
            history = [h for h in history if h.asset_type == asset_type]
        
        return sorted(history, key=lambda x: x.timestamp)


# Create singleton instance
price_service = PriceService()
