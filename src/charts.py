"""
Charts module for creating visualization components.
Uses Plotly for interactive charts.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

from config import Colors, AssetType, AssetCategory, AssetUnit
from models import AssetValuation, PortfolioSummary, PriceHistory


class ChartBuilder:
    """Builder class for creating various charts."""
    
    @staticmethod
    def _get_layout_template() -> Dict[str, Any]:
        """
        Get the base layout template for charts.
        
        Returns:
            Layout configuration dictionary
        """
        return {
            "template": "plotly_dark",
            "paper_bgcolor": Colors.PRIMARY,
            "plot_bgcolor": Colors.SECONDARY,
            "font": {"color": Colors.TEXT_PRIMARY, "family": "Arial"},
            "title_font": {"size": 18, "color": Colors.ACCENT},
            "legend": {
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": Colors.TEXT_SECONDARY,
            },
            "xaxis": {
                "gridcolor": "rgba(255,255,255,0.1)",
                "linecolor": Colors.TEXT_SECONDARY,
            },
            "yaxis": {
                "gridcolor": "rgba(255,255,255,0.1)",
                "linecolor": Colors.TEXT_SECONDARY,
            },
        }
    
    @staticmethod
    def create_portfolio_overview_chart(summary: PortfolioSummary) -> go.Figure:
        """
        Create a portfolio overview pie chart.
        
        Args:
            summary: Portfolio summary data
            
        Returns:
            Plotly figure object
        """
        # Create data
        labels = []
        values = []
        colors = []
        
        if summary.total_gold_value > 0:
            labels.append("Vàng")
            values.append(summary.total_gold_value)
            colors.append(Colors.GOLD)
        
        if summary.total_silver_value > 0:
            labels.append("Bạc")
            values.append(summary.total_silver_value)
            colors.append(Colors.SILVER)
        
        if not values:
            labels = ["Chưa có dữ liệu"]
            values = [1]
            colors = [Colors.TEXT_SECONDARY]
        
        # Create figure
        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(colors=colors),
                textinfo="label+percent",
                textposition="outside",
                textfont=dict(size=14, color=Colors.TEXT_PRIMARY),
                hovertemplate="<b>%{label}</b><br>" +
                              "Giá trị: %{value:,.0f} VNĐ<br>" +
                              "Tỷ lệ: %{percent}<extra></extra>",
            )
        ])
        
        # Update layout
        layout = ChartBuilder._get_layout_template()
        layout.update({
            "title": "Phân Bổ Danh Mục Theo Loại Tài Sản",
            "showlegend": True,
            "height": 400,
        })
        fig.update_layout(**layout)
        
        return fig
    
    @staticmethod
    def create_category_distribution_chart(
        existing_valuations: List[AssetValuation],
        investment_valuations: List[AssetValuation],
    ) -> go.Figure:
        """
        Create a category distribution bar chart.
        
        Args:
            existing_valuations: Existing asset valuations
            investment_valuations: Investment asset valuations
            
        Returns:
            Plotly figure object
        """
        categories = ["Tài sản sẵn có", "Tài sản đầu tư"]
        existing_value = sum(v.current_value for v in existing_valuations)
        investment_value = sum(v.current_value for v in investment_valuations)
        values = [existing_value, investment_value]
        
        # Create figure
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker=dict(
                    color=[Colors.ACCENT, Colors.ACCENT_LIGHT],
                    line=dict(width=2, color=Colors.TEXT_PRIMARY),
                ),
                text=[f"{v:,.0f} VNĐ" for v in values],
                textposition="outside",
                textfont=dict(size=12, color=Colors.TEXT_PRIMARY),
                hovertemplate="<b>%{x}</b><br>" +
                              "Giá trị: %{y:,.0f} VNĐ<extra></extra>",
            )
        ])
        
        # Update layout
        layout = ChartBuilder._get_layout_template()
        layout.update({
            "title": "Giá Trị Theo Danh Mục",
            "xaxis_title": "Danh Mục",
            "yaxis_title": "Giá Trị (VNĐ)",
            "showlegend": False,
            "height": 400,
        })
        fig.update_layout(**layout)
        
        return fig
    
    @staticmethod
    def create_profit_loss_chart(
        valuations: List[AssetValuation],
    ) -> go.Figure:
        """
        Create a profit/loss bar chart for investment assets.
        
        Args:
            valuations: List of investment valuations
            
        Returns:
            Plotly figure object
        """
        if not valuations:
            # Empty chart
            fig = go.Figure()
            layout = ChartBuilder._get_layout_template()
            layout.update({
                "title": "Lãi/Lỗ Tài Sản Đầu Tư",
                "height": 400,
                "annotations": [{
                    "text": "Chưa có dữ liệu tài sản đầu tư",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16, "color": Colors.TEXT_SECONDARY},
                }],
            })
            fig.update_layout(**layout)
            return fig
        
        # Prepare data
        names = [v.asset_name for v in valuations]
        profit_loss = [v.profit_loss_vnd or 0 for v in valuations]
        colors = [
            Colors.SUCCESS if pl >= 0 else Colors.DANGER
            for pl in profit_loss
        ]
        
        # Create figure
        fig = go.Figure(data=[
            go.Bar(
                x=names,
                y=profit_loss,
                marker=dict(color=colors),
                text=[f"{pl:+,.0f}" for pl in profit_loss],
                textposition="outside",
                textfont=dict(size=11, color=Colors.TEXT_PRIMARY),
                hovertemplate="<b>%{x}</b><br>" +
                              "Lãi/Lỗ: %{y:,.0f} VNĐ<extra></extra>",
            )
        ])
        
        # Add zero line
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color=Colors.TEXT_SECONDARY,
            opacity=0.7,
        )
        
        # Update layout
        layout = ChartBuilder._get_layout_template()
        layout.update({
            "title": "Lãi/Lỗ Theo Tài Sản Đầu Tư",
            "xaxis_title": "Tài Sản",
            "yaxis_title": "Lãi/Lỗ (VNĐ)",
            "showlegend": False,
            "height": 400,
        })
        fig.update_layout(**layout)
        
        return fig
    
    @staticmethod
    def create_profit_loss_percent_chart(
        valuations: List[AssetValuation],
    ) -> go.Figure:
        """
        Create a profit/loss percentage gauge chart.
        
        Args:
            valuations: List of investment valuations
            
        Returns:
            Plotly figure object
        """
        if not valuations:
            return ChartBuilder._create_empty_gauge()
        
        # Calculate overall percentage
        total_cost = sum(
            (v.purchase_price or 0) * v.quantity
            for v in valuations
        )
        total_current = sum(v.current_value for v in valuations)
        
        if total_cost > 0:
            overall_percent = ((total_current - total_cost) / total_cost) * 100
        else:
            overall_percent = 0
        
        # Determine color
        if overall_percent >= 0:
            color = Colors.SUCCESS
        else:
            color = Colors.DANGER
        
        # Create gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=overall_percent,
            number={"suffix": "%", "font": {"size": 40, "color": color}},
            delta={"reference": 0, "relative": False},
            title={"text": "Tổng Lãi/Lỗ (%)", "font": {"size": 16}},
            gauge={
                "axis": {"range": [-50, 50], "tickwidth": 1},
                "bar": {"color": color},
                "bgcolor": Colors.SECONDARY,
                "borderwidth": 2,
                "bordercolor": Colors.TEXT_SECONDARY,
                "steps": [
                    {"range": [-50, 0], "color": "rgba(220,53,69,0.3)"},
                    {"range": [0, 50], "color": "rgba(40,167,69,0.3)"},
                ],
                "threshold": {
                    "line": {"color": Colors.TEXT_PRIMARY, "width": 2},
                    "thickness": 0.75,
                    "value": overall_percent,
                },
            },
        ))
        
        # Update layout
        layout = ChartBuilder._get_layout_template()
        layout.update({"height": 300})
        fig.update_layout(**layout)
        
        return fig
    
    @staticmethod
    def _create_empty_gauge() -> go.Figure:
        """Create an empty gauge chart."""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=0,
            number={"suffix": "%"},
            title={"text": "Tổng Lãi/Lỗ (%)"},
            gauge={
                "axis": {"range": [-50, 50]},
                "bar": {"color": Colors.TEXT_SECONDARY},
                "bgcolor": Colors.SECONDARY,
            },
        ))
        
        layout = ChartBuilder._get_layout_template()
        layout.update({"height": 300})
        fig.update_layout(**layout)
        
        return fig
    
    @staticmethod
    def create_combined_bar_line_chart(
        valuations: List[AssetValuation],
        y_axis_type: str = "value",  # "value" or "percent"
        show_detail: bool = False,
    ) -> go.Figure:
        """
        Create a combined bar and line chart for asset management.
        
        Args:
            valuations: List of all valuations
            y_axis_type: Type of y-axis ("value" for VNĐ, "percent" for %)
            show_detail: Whether to show detailed breakdown
            
        Returns:
            Plotly figure object
        """
        if not valuations:
            fig = go.Figure()
            layout = ChartBuilder._get_layout_template()
            layout.update({
                "title": "Quản Lý Tài Sản Theo Thời Gian",
                "height": 500,
                "annotations": [{
                    "text": "Chưa có dữ liệu",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16, "color": Colors.TEXT_SECONDARY},
                }],
            })
            fig.update_layout(**layout)
            return fig
        
        # Create subplot with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Group by asset type and category
        gold_existing = [v for v in valuations if v.asset_type == AssetType.GOLD and v.category == AssetCategory.EXISTING]
        gold_investment = [v for v in valuations if v.asset_type == AssetType.GOLD and v.category == AssetCategory.INVESTMENT]
        silver_existing = [v for v in valuations if v.asset_type == AssetType.SILVER and v.category == AssetCategory.EXISTING]
        silver_investment = [v for v in valuations if v.asset_type == AssetType.SILVER and v.category == AssetCategory.INVESTMENT]
        
        if show_detail:
            # Show individual assets
            for v in valuations:
                y_value = v.current_value if y_axis_type == "value" else (v.profit_loss_percent or 0)
                color = Colors.GOLD if v.asset_type == AssetType.GOLD else Colors.SILVER
                pattern = "solid" if v.category == AssetCategory.EXISTING else "x"
                
                fig.add_trace(
                    go.Bar(
                        name=v.asset_name,
                        x=[v.asset_name],
                        y=[y_value],
                        marker=dict(
                            color=color,
                            pattern_shape=pattern,
                        ),
                        hovertemplate=f"<b>{v.asset_name}</b><br>" +
                                      f"Giá trị: {v.current_value:,.0f} VNĐ<br>" +
                                      f"Lãi/Lỗ: {v.profit_loss_percent or 0:+.2f}%<extra></extra>",
                    ),
                    secondary_y=False,
                )
        else:
            # Show aggregated data
            categories = []
            values = []
            colors = []
            
            if gold_existing:
                categories.append("Vàng\n(Sẵn có)")
                values.append(sum(v.current_value for v in gold_existing) if y_axis_type == "value" else 0)
                colors.append(Colors.GOLD)
            
            if gold_investment:
                categories.append("Vàng\n(Đầu tư)")
                val = sum(v.current_value for v in gold_investment) if y_axis_type == "value" else (
                    sum(v.profit_loss_percent or 0 for v in gold_investment) / len(gold_investment)
                )
                values.append(val)
                colors.append(Colors.GOLD)
            
            if silver_existing:
                categories.append("Bạc\n(Sẵn có)")
                values.append(sum(v.current_value for v in silver_existing) if y_axis_type == "value" else 0)
                colors.append(Colors.SILVER)
            
            if silver_investment:
                categories.append("Bạc\n(Đầu tư)")
                val = sum(v.current_value for v in silver_investment) if y_axis_type == "value" else (
                    sum(v.profit_loss_percent or 0 for v in silver_investment) / len(silver_investment)
                )
                values.append(val)
                colors.append(Colors.SILVER)
            
            # Add bar chart
            fig.add_trace(
                go.Bar(
                    name="Giá trị" if y_axis_type == "value" else "Tỷ lệ %",
                    x=categories,
                    y=values,
                    marker=dict(color=colors),
                    text=[f"{v:,.0f}" if y_axis_type == "value" else f"{v:.2f}%" for v in values],
                    textposition="outside",
                ),
                secondary_y=False,
            )
            
            # Add line chart for total trend (if investment)
            investment_vals = gold_investment + silver_investment
            if investment_vals and y_axis_type == "value":
                total_values = [sum(v.current_value for v in investment_vals)]
                fig.add_trace(
                    go.Scatter(
                        name="Tổng đầu tư",
                        x=["Tổng"],
                        y=total_values,
                        mode="lines+markers",
                        line=dict(color=Colors.ACCENT, width=3),
                        marker=dict(size=12),
                    ),
                    secondary_y=True,
                )
        
        # Update layout
        layout = ChartBuilder._get_layout_template()
        y_title = "Giá Trị (VNĐ)" if y_axis_type == "value" else "Tỷ Lệ (%)"
        layout.update({
            "title": "Quản Lý Tài Sản" + (" (Chi Tiết)" if show_detail else " (Tổng Hợp)"),
            "xaxis_title": "Danh Mục",
            "yaxis_title": y_title,
            "barmode": "group",
            "height": 500,
            "showlegend": True,
        })
        fig.update_layout(**layout)
        
        return fig
    
    @staticmethod
    def create_holding_period_chart(
        valuations: List[AssetValuation],
    ) -> go.Figure:
        """
        Create a scatter chart showing profit/loss vs holding period.
        
        Args:
            valuations: List of investment valuations
            
        Returns:
            Plotly figure object
        """
        investment_vals = [v for v in valuations if v.category == AssetCategory.INVESTMENT]
        
        if not investment_vals:
            fig = go.Figure()
            layout = ChartBuilder._get_layout_template()
            layout.update({
                "title": "Lãi/Lỗ Theo Thời Gian Nắm Giữ",
                "height": 400,
                "annotations": [{
                    "text": "Chưa có dữ liệu tài sản đầu tư",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16, "color": Colors.TEXT_SECONDARY},
                }],
            })
            fig.update_layout(**layout)
            return fig
        
        # Prepare data
        df = pd.DataFrame([
            {
                "name": v.asset_name,
                "months": v.holding_months or 0,
                "percent": v.profit_loss_percent or 0,
                "value": v.current_value,
                "type": "Vàng" if v.asset_type == AssetType.GOLD else "Bạc",
            }
            for v in investment_vals
        ])
        
        # Create figure
        fig = px.scatter(
            df,
            x="months",
            y="percent",
            size="value",
            color="type",
            hover_name="name",
            color_discrete_map={"Vàng": Colors.GOLD, "Bạc": Colors.SILVER},
            size_max=50,
        )
        
        # Add zero line
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color=Colors.TEXT_SECONDARY,
            opacity=0.7,
        )
        
        # Update layout
        layout = ChartBuilder._get_layout_template()
        layout.update({
            "title": "Lãi/Lỗ (%) Theo Thời Gian Nắm Giữ (Tháng)",
            "xaxis_title": "Thời Gian Nắm Giữ (Tháng)",
            "yaxis_title": "Lãi/Lỗ (%)",
            "height": 400,
        })
        fig.update_layout(**layout)
        
        return fig
