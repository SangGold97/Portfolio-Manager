"""
Main Streamlit application for Portfolio Manager.
Gold and Silver Investment Portfolio Management Dashboard.
"""

import sys
from pathlib import Path
from datetime import datetime, date
from typing import List, Optional

import streamlit as st
import pandas as pd
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import (
    PAGE_CONFIG,
    Colors,
    AssetType,
    AssetUnit,
    AssetCategory,
    BusinessReference,
    BUSINESS_CONFIG,
)
from models import (
    ExistingAsset,
    InvestmentAsset,
    AssetValuation,
    PortfolioSummary,
)
from price_service import price_service
from storage import storage_service
from charts import ChartBuilder


# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")


def init_session_state():
    """Initialize session state variables."""
    if "prices_loaded" not in st.session_state:
        st.session_state.prices_loaded = False
    
    if "existing_assets" not in st.session_state:
        st.session_state.existing_assets = storage_service.load_existing_assets()
    
    if "investment_assets" not in st.session_state:
        st.session_state.investment_assets = storage_service.load_investment_assets()
    
    if "existing_valuations" not in st.session_state:
        st.session_state.existing_valuations = []
    
    if "investment_valuations" not in st.session_state:
        st.session_state.investment_valuations = []
    
    if "portfolio_summary" not in st.session_state:
        st.session_state.portfolio_summary = None


def apply_custom_css():
    """Apply custom CSS for Dark Sunset theme."""
    st.markdown(f"""
    <style>
        /* Main background */
        .stApp {{
            background-color: {Colors.PRIMARY};
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {Colors.SECONDARY};
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: {Colors.ACCENT} !important;
        }}
        
        /* Metrics */
        [data-testid="stMetricValue"] {{
            color: {Colors.TEXT_PRIMARY};
        }}
        
        /* Cards */
        .stCard {{
            background-color: {Colors.SECONDARY};
            border: 1px solid {Colors.ACCENT};
            border-radius: 10px;
            padding: 20px;
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: {Colors.ACCENT};
            color: {Colors.TEXT_PRIMARY};
            border: none;
            border-radius: 5px;
        }}
        
        .stButton > button:hover {{
            background-color: {Colors.ACCENT_LIGHT};
        }}
        
        /* Tables */
        .stDataFrame {{
            background-color: {Colors.SECONDARY};
        }}
        
        /* Success/Error messages */
        .success-msg {{
            background-color: {Colors.SUCCESS};
            padding: 10px;
            border-radius: 5px;
            color: white;
        }}
        
        .error-msg {{
            background-color: {Colors.DANGER};
            padding: 10px;
            border-radius: 5px;
            color: white;
        }}
        
        /* Profit/Loss indicators */
        .profit {{
            color: {Colors.SUCCESS} !important;
        }}
        
        .loss {{
            color: {Colors.DANGER} !important;
        }}
        
        /* Info boxes */
        .info-box {{
            background-color: {Colors.SECONDARY};
            border-left: 4px solid {Colors.ACCENT};
            padding: 15px;
            margin: 10px 0;
            border-radius: 0 5px 5px 0;
        }}
    </style>
    """, unsafe_allow_html=True)


def refresh_prices():
    """Refresh all prices from web sources."""
    with st.spinner("Đang cập nhật giá..."):
        prices = price_service.refresh_prices()
        st.session_state.prices_loaded = True
        
        # Recalculate valuations
        calculate_valuations()
        
        return prices


def calculate_valuations():
    """Calculate valuations for all assets."""
    # Existing assets
    existing_valuations = []
    for asset in st.session_state.existing_assets:
        valuation = price_service.valuate_existing_asset(asset)
        if valuation:
            existing_valuations.append(valuation)
    
    # Investment assets
    investment_valuations = []
    for asset in st.session_state.investment_assets:
        valuation = price_service.valuate_investment_asset(asset)
        if valuation:
            investment_valuations.append(valuation)
    
    # Update session state
    st.session_state.existing_valuations = existing_valuations
    st.session_state.investment_valuations = investment_valuations
    
    # Calculate portfolio summary
    st.session_state.portfolio_summary = price_service.calculate_portfolio_summary(
        existing_valuations, investment_valuations
    )


def format_currency(value: float) -> str:
    """Format value as Vietnamese currency."""
    return f"{value:,.0f} VNĐ"


def format_percent(value: float) -> str:
    """Format value as percentage."""
    return f"{value:+.2f}%"


def render_sidebar():
    """Render sidebar with controls and asset forms."""
    with st.sidebar:
        st.title("💰 Quản Lý Danh Mục")
        st.markdown("---")
        
        # Refresh button
        if st.button("🔄 Cập Nhật Giá", width="stretch"):
            refresh_prices()
            st.success("Đã cập nhật giá thành công!")
            st.rerun()
        
        # Show last refresh time
        last_refresh = price_service.get_last_refresh_time()
        if last_refresh:
            st.caption(f"Cập nhật lần cuối: {last_refresh.strftime('%H:%M:%S %d/%m/%Y')}")
        
        st.markdown("---")
        
        # Add asset forms
        st.subheader("➕ Thêm Tài Sản")
        
        asset_tab = st.radio(
            "Loại tài sản",
            ["Tài sản sẵn có", "Tài sản đầu tư"],
            horizontal=True,
        )
        
        if asset_tab == "Tài sản sẵn có":
            render_existing_asset_form()
        else:
            render_investment_asset_form()
        
        st.markdown("---")
        
        # Show current prices
        st.subheader("📊 Giá Hiện Tại")
        
        cached_prices = price_service.get_all_cached_prices()
        if cached_prices:
            for business, price_data in cached_prices.items():
                if price_data:
                    icon = "🥇" if price_data.asset_type == AssetType.GOLD else "🥈"
                    st.markdown(f"""
                    **{icon} {business}**  
                    `{format_currency(price_data.buy_price)}/{price_data.price_unit}`
                    """)
        else:
            st.info("Nhấn 'Cập Nhật Giá' để xem giá hiện tại")


def render_existing_asset_form():
    """Render form for adding existing asset."""
    with st.form("existing_asset_form"):
        # Name
        name = st.text_input("Tên tài sản", placeholder="VD: Vàng BTMC")
        
        # Asset type
        asset_type = st.selectbox(
            "Loại tài sản",
            options=[AssetType.GOLD.value, AssetType.SILVER.value],
            format_func=lambda x: "Vàng" if x == AssetType.GOLD.value else "Bạc"
        )
        
        # Quantity and unit
        col1, col2 = st.columns([2, 1])
        with col1:
            quantity = st.number_input("Số lượng", min_value=0.01, step=0.1, value=1.0)
        with col2:
            unit = st.selectbox(
                "Đơn vị",
                options=[u.value for u in AssetUnit],
                format_func=lambda x: {"chi": "Chỉ", "luong": "Lượng", "kg": "Kilogram"}[x]
            )
        
        # Filter references by asset type
        if asset_type == AssetType.GOLD.value:
            refs = [
                BusinessReference.BAO_TIN_MINH_CHAU.value,
                BusinessReference.BAO_TIN_MANH_HAI.value,
                BusinessReference.PHU_TAI.value,
            ]
        else:
            refs = [
                BusinessReference.PHU_QUY.value,
                BusinessReference.ANCARAT.value,
            ]
        
        reference = st.selectbox("Cơ sở kinh doanh tham chiếu", options=refs)
        
        # Submit button
        submitted = st.form_submit_button("Thêm Tài Sản", width="stretch")
        
        if submitted:
            if not name:
                st.error("Vui lòng nhập tên tài sản")
            else:
                # Create asset
                asset = ExistingAsset(
                    name=name,
                    asset_type=asset_type,
                    quantity=quantity,
                    unit=unit,
                    reference=reference,
                )
                
                # Save
                st.session_state.existing_assets.append(asset)
                storage_service.save_existing_assets(st.session_state.existing_assets)
                
                # Recalculate
                if st.session_state.prices_loaded:
                    calculate_valuations()
                
                st.success(f"Đã thêm tài sản: {name}")
                st.rerun()


def render_investment_asset_form():
    """Render form for adding investment asset."""
    with st.form("investment_asset_form"):
        # Name
        name = st.text_input("Tên tài sản", placeholder="VD: Vàng đầu tư BTMC")
        
        # Asset type
        asset_type = st.selectbox(
            "Loại tài sản",
            options=[AssetType.GOLD.value, AssetType.SILVER.value],
            format_func=lambda x: "Vàng" if x == AssetType.GOLD.value else "Bạc"
        )
        
        # Quantity and unit
        col1, col2 = st.columns([2, 1])
        with col1:
            quantity = st.number_input("Số lượng", min_value=0.01, step=0.1, value=1.0)
        with col2:
            unit = st.selectbox(
                "Đơn vị",
                options=[u.value for u in AssetUnit],
                format_func=lambda x: {"chi": "Chỉ", "luong": "Lượng", "kg": "Kilogram"}[x]
            )
        
        # Purchase price
        purchase_price = st.number_input(
            "Giá mua (VNĐ/đơn vị)",
            min_value=0,
            step=100000,
            value=15000000,
        )
        
        # Purchase date
        purchase_date = st.date_input(
            "Ngày mua",
            value=date.today(),
            max_value=date.today(),
        )
        
        # Filter references by asset type
        if asset_type == AssetType.GOLD.value:
            refs = [
                BusinessReference.BAO_TIN_MINH_CHAU.value,
                BusinessReference.BAO_TIN_MANH_HAI.value,
                BusinessReference.PHU_TAI.value,
            ]
        else:
            refs = [
                BusinessReference.PHU_QUY.value,
                BusinessReference.ANCARAT.value,
            ]
        
        reference = st.selectbox("Cơ sở kinh doanh tham chiếu", options=refs)
        
        # Submit button
        submitted = st.form_submit_button("Thêm Tài Sản", width="stretch")
        
        if submitted:
            if not name:
                st.error("Vui lòng nhập tên tài sản")
            elif purchase_price <= 0:
                st.error("Vui lòng nhập giá mua hợp lệ")
            else:
                # Create asset
                asset = InvestmentAsset(
                    name=name,
                    asset_type=asset_type,
                    quantity=quantity,
                    unit=unit,
                    reference=reference,
                    purchase_price=purchase_price,
                    purchase_date=purchase_date,
                )
                
                # Save
                st.session_state.investment_assets.append(asset)
                storage_service.save_investment_assets(st.session_state.investment_assets)
                
                # Recalculate
                if st.session_state.prices_loaded:
                    calculate_valuations()
                
                st.success(f"Đã thêm tài sản đầu tư: {name}")
                st.rerun()


def render_summary_metrics():
    """Render portfolio summary metrics."""
    summary = st.session_state.portfolio_summary
    
    if not summary:
        st.info("Nhấn 'Cập Nhật Giá' để xem tổng quan danh mục")
        return
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Tổng Giá Trị",
            format_currency(summary.total_portfolio_value),
        )
    
    with col2:
        st.metric(
            "🥇 Tổng Vàng",
            format_currency(summary.total_gold_value),
        )
    
    with col3:
        st.metric(
            "🥈 Tổng Bạc",
            format_currency(summary.total_silver_value),
        )
    
    with col4:
        delta_color = "normal" if summary.total_profit_loss_vnd >= 0 else "inverse"
        st.metric(
            "📈 Tổng Lãi/Lỗ",
            format_currency(summary.total_profit_loss_vnd),
            delta=format_percent(summary.total_profit_loss_percent),
            delta_color=delta_color,
        )
    
    # Secondary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📦 Tài Sản Sẵn Có",
            format_currency(summary.total_existing_value),
            delta=f"{summary.existing_asset_count} tài sản",
        )
    
    with col2:
        st.metric(
            "📊 Tài Sản Đầu Tư",
            format_currency(summary.total_investment_value),
            delta=f"{summary.investment_asset_count} tài sản",
        )


def render_asset_table():
    """Render the asset statistics table."""
    st.subheader("📋 Bảng Thống Kê Tài Sản")
    
    all_valuations = (
        st.session_state.existing_valuations +
        st.session_state.investment_valuations
    )
    
    if not all_valuations:
        st.info("Chưa có dữ liệu tài sản. Hãy thêm tài sản và cập nhật giá.")
        return
    
    # Build dataframe
    data = []
    for v in all_valuations:
        row = {
            "Danh Mục": "Sẵn có" if v.category == AssetCategory.EXISTING else "Đầu tư",
            "Sản Phẩm": v.asset_name,
            "Loại": "Vàng" if v.asset_type == AssetType.GOLD else "Bạc",
            "Số Lượng": f"{v.quantity:.2f}",
            "Đơn Vị": {"chi": "Chỉ", "luong": "Lượng", "kg": "Kg"}[v.unit],
            "CSKD": v.reference,
            "Giá Mua": format_currency(v.purchase_price) if v.purchase_price else "-",
            "Giá Hiện Tại": format_currency(v.current_price),
            "Giá Trị HT": format_currency(v.current_value),
            "Lãi/Lỗ (VNĐ)": format_currency(v.profit_loss_vnd) if v.profit_loss_vnd is not None else "-",
            "Lãi/Lỗ (%)": format_percent(v.profit_loss_percent) if v.profit_loss_percent is not None else "-",
            "TG (Tháng)": f"{v.holding_months:.2f}" if v.holding_months is not None else "-",
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    st.dataframe(df, width="stretch", hide_index=True)
    
    # Delete buttons section
    st.markdown("---")
    with st.expander("🗑️ Xóa Tài Sản"):
        for v in all_valuations:
            col1, col2 = st.columns([4, 1])
            with col1:
                category_text = "Sẵn có" if v.category == AssetCategory.EXISTING else "Đầu tư"
                type_text = "Vàng" if v.asset_type == AssetType.GOLD else "Bạc"
                st.text(f"{category_text} | {v.asset_name} | {type_text} | {v.quantity:.2f} {v.unit}")
            with col2:
                if st.button("Xóa", key=f"del_{v.asset_id}", width="content"):
                    st.session_state.delete_confirm_id = v.asset_id
                    st.session_state.delete_confirm_name = v.asset_name
                    st.session_state.delete_confirm_category = v.category
                    st.rerun()
    
    # Delete confirmation dialog
    if "delete_confirm_id" in st.session_state:
        @st.dialog("Xác Nhận Xóa Tài Sản")
        def confirm_delete():
            st.warning(f"Bạn có chắc chắn muốn xóa tài sản **{st.session_state.delete_confirm_name}**?")
            col1, col2 = st.columns(2)
            if col1.button("✅ Xác Nhận", width="stretch", type="primary"):
                if st.session_state.delete_confirm_category == AssetCategory.EXISTING:
                    storage_service.delete_existing_asset(st.session_state.delete_confirm_id)
                    st.session_state.existing_assets = storage_service.load_existing_assets()
                else:
                    storage_service.delete_investment_asset(st.session_state.delete_confirm_id)
                    st.session_state.investment_assets = storage_service.load_investment_assets()
                calculate_valuations()
                del st.session_state.delete_confirm_id
                del st.session_state.delete_confirm_name
                del st.session_state.delete_confirm_category
                st.success("Đã xóa tài sản thành công!")
                st.rerun()
            if col2.button("❌ Hủy", width="stretch"):
                del st.session_state.delete_confirm_id
                del st.session_state.delete_confirm_name
                del st.session_state.delete_confirm_category
                st.rerun()
        confirm_delete()
    


def render_charts():
    """Render visualization charts."""
    st.subheader("📈 Biểu Đồ Quản Lý Tài Sản")
    
    all_valuations = (
        st.session_state.existing_valuations +
        st.session_state.investment_valuations
    )
    
    summary = st.session_state.portfolio_summary
    
    if not summary or not all_valuations:
        st.info("Chưa có dữ liệu để hiển thị biểu đồ. Hãy thêm tài sản và cập nhật giá.")
        return
    
    # Chart controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        y_axis_type = st.selectbox(
            "Trục Y",
            options=["value", "percent"],
            format_func=lambda x: "Giá trị (VNĐ)" if x == "value" else "Tỷ lệ (%)",
        )
    
    with col2:
        show_detail = st.checkbox("Xem chi tiết", value=False)
    
    # Row 1: Overview charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig = ChartBuilder.create_portfolio_overview_chart(summary)
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        fig = ChartBuilder.create_category_distribution_chart(
            st.session_state.existing_valuations,
            st.session_state.investment_valuations,
        )
        st.plotly_chart(fig, width="stretch")
    
    # Row 2: Combined chart
    fig = ChartBuilder.create_combined_bar_line_chart(
        all_valuations,
        y_axis_type=y_axis_type,
        show_detail=show_detail,
    )
    st.plotly_chart(fig, width="stretch")
    
    # Row 3: Profit/Loss charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig = ChartBuilder.create_profit_loss_chart(
            st.session_state.investment_valuations
        )
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        fig = ChartBuilder.create_profit_loss_percent_chart(
            st.session_state.investment_valuations
        )
        st.plotly_chart(fig, width="stretch")
    
    # Row 4: Holding period scatter
    fig = ChartBuilder.create_holding_period_chart(all_valuations)
    st.plotly_chart(fig, width="stretch")


def main():
    """Main application entry point."""
    # Page config
    st.set_page_config(**PAGE_CONFIG)
    
    # Initialize
    init_session_state()
    apply_custom_css()
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    st.title("💰 Gold & Silver Portfolio Manager")
    st.markdown("---")
    
    # Summary metrics
    render_summary_metrics()
    
    st.markdown("---")
    
    # Tabs for main content
    tab1, tab2 = st.tabs(["📋 Bảng Thống Kê", "📈 Biểu Đồ"])
    
    with tab1:
        render_asset_table()
    
    with tab2:
        render_charts()
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: {Colors.TEXT_SECONDARY};">
            <small>
                Portfolio Manager v1.0 | 
                Dữ liệu giá từ: BTMC, BTMH, Phú Quý, Phú Tài, Ancarat |
                Cập nhật: {datetime.now().strftime('%d/%m/%Y')}
            </small>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
