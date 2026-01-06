"""
Data models for the Portfolio Manager application.
Using Pydantic for data validation and serialization.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from config import AssetType, AssetUnit, AssetCategory


class PriceData(BaseModel):
    """Model for price data from a business reference."""
    
    business_name: str = Field(..., description="Name of the business")
    buy_price: float = Field(..., ge=0, description="Buy price in VND")
    sell_price: Optional[float] = Field(None, ge=0, description="Sell price in VND")
    price_unit: AssetUnit = Field(..., description="Unit of the price")
    asset_type: AssetType = Field(..., description="Type of asset (gold/silver)")
    product_name: str = Field(..., description="Name of the product")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update time")
    
    class Config:
        use_enum_values = True


class ExistingAsset(BaseModel):
    """Model for existing assets (tài sản sẵn có)."""
    
    id: str = Field(
        default_factory=lambda: f"existing_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        description="Unique identifier"
    )
    name: str = Field(..., min_length=1, description="Asset name")
    asset_type: AssetType = Field(..., description="Type of asset")
    quantity: float = Field(..., gt=0, description="Quantity of asset")
    unit: AssetUnit = Field(..., description="Unit of measurement")
    reference: str = Field(..., description="Reference business for pricing")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation time")
    
    class Config:
        use_enum_values = True


class InvestmentAsset(BaseModel):
    """Model for investment assets (tài sản đầu tư)."""
    
    id: str = Field(
        default_factory=lambda: f"investment_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        description="Unique identifier"
    )
    name: str = Field(..., min_length=1, description="Asset name")
    asset_type: AssetType = Field(..., description="Type of asset")
    quantity: float = Field(..., gt=0, description="Quantity of asset")
    unit: AssetUnit = Field(..., description="Unit of measurement")
    reference: str = Field(..., description="Reference business for pricing")
    purchase_price: float = Field(..., gt=0, description="Purchase price in VND per unit")
    purchase_date: date = Field(..., description="Date of purchase")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation time")
    
    class Config:
        use_enum_values = True


class AssetValuation(BaseModel):
    """Model for asset valuation with profit/loss calculation."""
    
    asset_id: str = Field(..., description="Reference to asset ID")
    asset_name: str = Field(..., description="Asset name")
    asset_type: AssetType = Field(..., description="Type of asset")
    category: AssetCategory = Field(..., description="Asset category")
    quantity: float = Field(..., description="Quantity")
    unit: AssetUnit = Field(..., description="Unit")
    reference: str = Field(..., description="Reference business")
    
    # Purchase info (only for investment assets)
    purchase_price: Optional[float] = Field(None, description="Purchase price per unit")
    purchase_date: Optional[date] = Field(None, description="Purchase date")
    
    # Current valuation
    current_price: float = Field(..., description="Current buy price per unit")
    current_value: float = Field(..., description="Current total value")
    
    # Profit/Loss (only for investment assets)
    profit_loss_vnd: Optional[float] = Field(None, description="Profit/Loss in VND")
    profit_loss_percent: Optional[float] = Field(None, description="Profit/Loss percentage")
    holding_months: Optional[float] = Field(None, description="Holding period in months")
    
    # Metadata
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update time")
    
    class Config:
        use_enum_values = True


class PortfolioSummary(BaseModel):
    """Model for portfolio summary."""
    
    total_existing_value: float = Field(0, description="Total value of existing assets")
    total_investment_value: float = Field(0, description="Total value of investment assets")
    total_portfolio_value: float = Field(0, description="Total portfolio value")
    
    total_gold_value: float = Field(0, description="Total gold assets value")
    total_silver_value: float = Field(0, description="Total silver assets value")
    
    total_profit_loss_vnd: float = Field(0, description="Total profit/loss in VND")
    total_profit_loss_percent: float = Field(0, description="Total profit/loss percentage")
    
    existing_asset_count: int = Field(0, description="Number of existing assets")
    investment_asset_count: int = Field(0, description="Number of investment assets")
    
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update time")


class PriceHistory(BaseModel):
    """Model for historical price data."""
    
    business_name: str = Field(..., description="Business name")
    asset_type: AssetType = Field(..., description="Asset type")
    price: float = Field(..., description="Price in VND")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp")
    
    class Config:
        use_enum_values = True
