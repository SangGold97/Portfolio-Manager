"""
Storage service for managing asset data persistence.
Uses JSON file storage for simplicity.
"""

import json
import os
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pathlib import Path
from loguru import logger

from models import ExistingAsset, InvestmentAsset


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""
    
    def default(self, obj):
        """Handle datetime and date serialization."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


class StorageService:
    """Service for persisting asset data to JSON files."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the storage service.
        
        Args:
            data_dir: Directory for storing data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.existing_assets_file = self.data_dir / "existing_assets.json"
        self.investment_assets_file = self.data_dir / "investment_assets.json"
        self.price_history_file = self.data_dir / "price_history.json"
    
    def _load_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Load JSON data from file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List of data dictionaries
        """
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading {file_path}: {e}")
            return []
    
    def _save_json(self, file_path: Path, data: List[Dict[str, Any]]) -> bool:
        """
        Save data to JSON file.
        
        Args:
            file_path: Path to JSON file
            data: List of data dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, cls=DateTimeEncoder, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            logger.error(f"Error saving {file_path}: {e}")
            return False
    
    # Existing Assets CRUD
    def load_existing_assets(self) -> List[ExistingAsset]:
        """
        Load all existing assets.
        
        Returns:
            List of ExistingAsset objects
        """
        data = self._load_json(self.existing_assets_file)
        assets = []
        needs_save = False
        
        for item in data:
            try:
                # Parse datetime
                if "created_at" in item and isinstance(item["created_at"], str):
                    item["created_at"] = datetime.fromisoformat(item["created_at"])
                
                # Generate new ID if null
                if item.get("id") is None:
                    item["id"] = f"existing_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
                    needs_save = True
                
                assets.append(ExistingAsset(**item))
            except Exception as e:
                logger.error(f"Error parsing existing asset: {e}")
        
        # Save back if any IDs were generated
        if needs_save:
            self.save_existing_assets(assets)
        
        return assets
    
    def save_existing_assets(self, assets: List[ExistingAsset]) -> bool:
        """
        Save all existing assets.
        
        Args:
            assets: List of ExistingAsset objects
            
        Returns:
            True if successful
        """
        data = [asset.model_dump() for asset in assets]
        return self._save_json(self.existing_assets_file, data)
    
    def add_existing_asset(self, asset: ExistingAsset) -> bool:
        """
        Add a new existing asset.
        
        Args:
            asset: ExistingAsset to add
            
        Returns:
            True if successful
        """
        assets = self.load_existing_assets()
        assets.append(asset)
        return self.save_existing_assets(assets)
    
    def update_existing_asset(self, asset_id: str, updated_asset: ExistingAsset) -> bool:
        """
        Update an existing asset.
        
        Args:
            asset_id: ID of asset to update
            updated_asset: Updated asset data
            
        Returns:
            True if successful
        """
        assets = self.load_existing_assets()
        
        for i, asset in enumerate(assets):
            if asset.id == asset_id:
                assets[i] = updated_asset
                return self.save_existing_assets(assets)
        
        logger.warning(f"Asset not found: {asset_id}")
        return False
    
    def delete_existing_asset(self, asset_id: str) -> bool:
        """
        Delete an existing asset.
        
        Args:
            asset_id: ID of asset to delete
            
        Returns:
            True if successful
        """
        assets = self.load_existing_assets()
        original_count = len(assets)
        
        assets = [a for a in assets if a.id != asset_id]
        
        if len(assets) < original_count:
            return self.save_existing_assets(assets)
        
        logger.warning(f"Asset not found: {asset_id}")
        return False
    
    # Investment Assets CRUD
    def load_investment_assets(self) -> List[InvestmentAsset]:
        """
        Load all investment assets.
        
        Returns:
            List of InvestmentAsset objects
        """
        data = self._load_json(self.investment_assets_file)
        assets = []
        needs_save = False
        
        for item in data:
            try:
                # Parse datetime
                if "created_at" in item and isinstance(item["created_at"], str):
                    item["created_at"] = datetime.fromisoformat(item["created_at"])
                
                # Parse date
                if "purchase_date" in item and isinstance(item["purchase_date"], str):
                    item["purchase_date"] = date.fromisoformat(item["purchase_date"])
                
                # Generate new ID if null
                if item.get("id") is None:
                    item["id"] = f"investment_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
                    needs_save = True
                
                assets.append(InvestmentAsset(**item))
            except Exception as e:
                logger.error(f"Error parsing investment asset: {e}")
        
        # Save back if any IDs were generated
        if needs_save:
            self.save_investment_assets(assets)
        
        return assets
    
    def save_investment_assets(self, assets: List[InvestmentAsset]) -> bool:
        """
        Save all investment assets.
        
        Args:
            assets: List of InvestmentAsset objects
            
        Returns:
            True if successful
        """
        data = [asset.model_dump() for asset in assets]
        return self._save_json(self.investment_assets_file, data)
    
    def add_investment_asset(self, asset: InvestmentAsset) -> bool:
        """
        Add a new investment asset.
        
        Args:
            asset: InvestmentAsset to add
            
        Returns:
            True if successful
        """
        assets = self.load_investment_assets()
        assets.append(asset)
        return self.save_investment_assets(assets)
    
    def update_investment_asset(self, asset_id: str, updated_asset: InvestmentAsset) -> bool:
        """
        Update an investment asset.
        
        Args:
            asset_id: ID of asset to update
            updated_asset: Updated asset data
            
        Returns:
            True if successful
        """
        assets = self.load_investment_assets()
        
        for i, asset in enumerate(assets):
            if asset.id == asset_id:
                assets[i] = updated_asset
                return self.save_investment_assets(assets)
        
        logger.warning(f"Asset not found: {asset_id}")
        return False
    
    def delete_investment_asset(self, asset_id: str) -> bool:
        """
        Delete an investment asset.
        
        Args:
            asset_id: ID of asset to delete
            
        Returns:
            True if successful
        """
        assets = self.load_investment_assets()
        original_count = len(assets)
        
        assets = [a for a in assets if a.id != asset_id]
        
        if len(assets) < original_count:
            return self.save_investment_assets(assets)
        
        logger.warning(f"Asset not found: {asset_id}")
        return False


# Create singleton instance
storage_service = StorageService()
