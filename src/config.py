"""
Configuration settings for the Portfolio Manager application.
Contains constants, color schemes, and business settings.
"""

from enum import Enum
from typing import Dict, List


# Dark Sunset theme colors from coolors.co
class Colors:
    """Dark Sunset theme color palette."""
    
    PRIMARY = "#1a1a2e"        # Dark blue background
    SECONDARY = "#16213e"      # Darker blue
    ACCENT = "#e94560"         # Coral/sunset red
    ACCENT_LIGHT = "#ff6b6b"   # Light coral
    WARNING = "#ffc107"        # Gold/yellow for profit
    DANGER = "#dc3545"         # Red for loss
    SUCCESS = "#28a745"        # Green for positive
    TEXT_PRIMARY = "#eaeaea"   # Light text
    TEXT_SECONDARY = "#a0a0a0" # Muted text
    GOLD = "#ffd700"           # Gold color for gold assets
    SILVER = "#c0c0c0"         # Silver color for silver assets
    CHART_BG = "#0f3460"       # Chart background


# Unit conversion constants
class UnitConversion:
    """Conversion rates between different units."""
    
    # 1 luong (tael) = 10 chi (mace)
    # 1 kilogram = 26.67 luong (approximately)
    CHI_TO_LUONG = 0.1           # 1 chi = 0.1 luong
    LUONG_TO_CHI = 10.0          # 1 luong = 10 chi
    KG_TO_LUONG = 26.67          # 1 kg ≈ 26.67 luong
    LUONG_TO_KG = 0.0375         # 1 luong ≈ 37.5 gram = 0.0375 kg
    KG_TO_CHI = 266.7            # 1 kg ≈ 266.7 chi
    CHI_TO_KG = 0.00375          # 1 chi ≈ 3.75 gram = 0.00375 kg


class AssetUnit(str, Enum):
    """Available units for assets."""
    
    CHI = "chi"
    LUONG = "luong"
    KILOGRAM = "kg"


class AssetType(str, Enum):
    """Types of precious metal assets."""
    
    GOLD = "gold"
    SILVER = "silver"


class AssetCategory(str, Enum):
    """Categories of assets."""
    
    EXISTING = "existing"       # Tài sản sẵn có
    INVESTMENT = "investment"   # Tài sản đầu tư


class BusinessReference(str, Enum):
    """Reference businesses for price tracking."""
    
    BAO_TIN_MINH_CHAU = "Bảo Tín Minh Châu"
    BAO_TIN_MANH_HAI = "Bảo Tín Mạnh Hải"
    PHU_QUY = "Phú Quý"
    PHU_TAI = "Phú Tài"
    ANCARAT = "Ancarat"


# Business configuration with scraping details
BUSINESS_CONFIG: Dict[str, Dict] = {
    BusinessReference.BAO_TIN_MINH_CHAU.value: {
        "url": "https://btmc.vn/",
        "asset_type": AssetType.GOLD,
        "product_name": "Nhẫn tròn trơn Bảo Tín Minh Châu",
        "price_unit": AssetUnit.CHI,
        "price_multiplier": 1000,  # Price is in 1000 VND
    },
    BusinessReference.BAO_TIN_MANH_HAI.value: {
        "url": "https://baotinmanhhai.vn/",
        "asset_type": AssetType.GOLD,
        "product_name": "Nhẫn ép vỉ Vàng Rồng Thăng Long",
        "price_unit": AssetUnit.CHI,
        "price_multiplier": 1,  # Price is in VND
    },
    BusinessReference.PHU_QUY.value: {
        "url": "https://phuquy.com.vn/",  # Alternative URL
        "asset_type": AssetType.SILVER,
        "product_name": "Bạc thỏi Phú Quý 999 1Kilo",
        "price_unit": AssetUnit.KILOGRAM,
        "price_multiplier": 1000,  # Price is in 1000 VND
    },
    BusinessReference.PHU_TAI.value: {
        "url": "https://www.vangphutai.vn/",
        "asset_type": AssetType.GOLD,
        "product_name": "Nhẫn tròn trơn 999.9",
        "price_unit": AssetUnit.CHI,
        "price_multiplier": 1000,  # Price is in 1000 VND
    },
    BusinessReference.ANCARAT.value: {
        "url": "https://giabac.ancarat.com/",
        "asset_type": AssetType.SILVER,
        "product_name": "Ngân Long Quảng Tiến 999 - 1 lượng",
        "price_unit": AssetUnit.LUONG,
        "price_multiplier": 1,  # Price is already in VND (with comma)
    },
}


# Default sample data for demonstration
DEFAULT_EXISTING_ASSETS = [
    {
        "name": "Vàng BTMC",
        "asset_type": AssetType.GOLD.value,
        "quantity": 5.0,
        "unit": AssetUnit.CHI.value,
        "reference": BusinessReference.BAO_TIN_MINH_CHAU.value,
    },
]

DEFAULT_INVESTMENT_ASSETS = [
    {
        "name": "Vàng Phú Tài",
        "asset_type": AssetType.GOLD.value,
        "quantity": 3.0,
        "unit": AssetUnit.CHI.value,
        "reference": BusinessReference.PHU_TAI.value,
        "purchase_price": 14500000,
        "purchase_date": "2024-06-15",
    },
]


# Streamlit page config
PAGE_CONFIG = {
    "page_title": "Quản Lý Danh Mục Đầu Tư Vàng/Bạc",
    "page_icon": "💰",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}


# Chart configuration
CHART_CONFIG = {
    "template": "plotly_dark",
    "color_discrete_sequence": [
        Colors.ACCENT,
        Colors.WARNING,
        Colors.SUCCESS,
        Colors.ACCENT_LIGHT,
    ],
}
