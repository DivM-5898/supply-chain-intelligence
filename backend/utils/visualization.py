"""
Visualization Utilities
Reusable Plotly charts and visualization functions
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


class Visualizer:
    """Visualization utilities for dashboard"""
    
    @staticmethod
    def create_supplier_ranking_chart(df: pd.DataFrame, score_col: str = 'score',
                                     top_n: int = 10) -> go.Figure:
        """Create horizontal bar chart for supplier rankings"""
        top_suppliers = df.nlargest(top_n, score_col)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=top_suppliers['supplier_id'],
            x=top_suppliers[score_col],
            orientation='h',
            marker=dict(
                color=top_suppliers[score_col],
                colorscale='Viridis',
                showscale=True
            ),
            text=[f"{score:.3f}" for score in top_suppliers[score_col]],
            textposition='outside'
        ))
        
        fig.update_layout(
            title=f"Top {top_n} Supplier Rankings",
            xaxis_title="Score",
            yaxis_title="Supplier ID",
            height=400,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_radar_chart(supplier_data: Dict[str, float], 
                          categories: List[str]) -> go.Figure:
        """Create radar/spider chart for multi-dimensional comparison"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=[supplier_data.get(cat, 0) for cat in categories],
            theta=categories,
            fill='toself',
            name='Supplier'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="Multi-Dimensional Supplier Comparison"
        )
        
        return fig
    
    @staticmethod
    def create_risk_heatmap(df: pd.DataFrame, risk_columns: List[str]) -> go.Figure:
        """Create heatmap for risk comparison"""
        risk_data = df[['supplier_id'] + risk_columns].set_index('supplier_id')
        
        fig = go.Figure(data=go.Heatmap(
            z=risk_data.values,
            x=risk_columns,
            y=risk_data.index,
            colorscale='RdYlGn_r',
            showscale=True
        ))
        
        fig.update_layout(
            title="Risk Profile Heatmap",
            xaxis_title="Risk Dimensions",
            yaxis_title="Suppliers",
            height=600
        )
        
        return fig
    
    @staticmethod
    def create_comparison_matrix(suppliers: List[str], metrics: Dict[str, Dict[str, float]]) -> go.Figure:
        """Create comparison matrix for multiple suppliers"""
        fig = go.Figure()
        
        for supplier in suppliers:
            values = [metrics[supplier].get(metric, 0) for metric in metrics[suppliers[0]].keys()]
            fig.add_trace(go.Bar(
                name=supplier,
                x=list(metrics[suppliers[0]].keys()),
                y=values
            ))
        
        fig.update_layout(
            title="Supplier Comparison Matrix",
            xaxis_title="Metrics",
            yaxis_title="Score",
            barmode='group',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_3d_scatter(df: pd.DataFrame, x_col: str, y_col: str, z_col: str,
                          color_col: Optional[str] = None, size_col: Optional[str] = None) -> go.Figure:
        """Create 3D scatter plot"""
        fig = px.scatter_3d(
            df,
            x=x_col,
            y=y_col,
            z=z_col,
            color=color_col if color_col else None,
            size=size_col if size_col else None,
            hover_data=['supplier_id'] if 'supplier_id' in df.columns else None,
            title="3D Supplier Analysis"
        )
        
        fig.update_layout(height=600)
        return fig
    
    @staticmethod
    def create_geographic_risk_map(df: pd.DataFrame, country_col: str = 'country',
                                   risk_col: str = 'geopolitical_risk_score') -> go.Figure:
        """Create geographic risk visualization"""
        country_risk = df.groupby(country_col)[risk_col].mean().reset_index()
        
        fig = px.choropleth(
            country_risk,
            locations=country_col,
            locationmode='country names',
            color=risk_col,
            color_continuous_scale='RdYlGn_r',
            title="Geographic Risk Distribution",
            labels={risk_col: 'Risk Score'}
        )
        
        fig.update_layout(height=500)
        return fig
    
    @staticmethod
    def create_time_series(df: pd.DataFrame, date_col: str, value_col: str,
                          group_col: Optional[str] = None) -> go.Figure:
        """Create time series plot"""
        fig = px.line(
            df,
            x=date_col,
            y=value_col,
            color=group_col if group_col else None,
            title="Time Series Analysis"
        )
        
        fig.update_layout(height=400)
        return fig
    
    @staticmethod
    def create_feature_importance_chart(importance_dict: Dict[str, float], 
                                       top_n: int = 10) -> go.Figure:
        """Create feature importance bar chart"""
        sorted_features = sorted(importance_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:top_n]
        features, importances = zip(*sorted_features)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(importances),
            y=list(features),
            orientation='h',
            marker=dict(
                color=list(importances),
                colorscale='RdBu',
                showscale=True
            )
        ))
        
        fig.update_layout(
            title=f"Top {top_n} Feature Importances",
            xaxis_title="Importance",
            yaxis_title="Feature",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_network_graph(nodes: List[Dict], edges: List[Dict]) -> go.Figure:
        """Create network graph visualization"""
        # Extract node positions (simplified - would need proper layout algorithm)
        node_x = [node.get('x', np.random.random()) for node in nodes]
        node_y = [node.get('y', np.random.random()) for node in nodes]
        node_text = [node.get('label', '') for node in nodes]
        
        edge_x = []
        edge_y = []
        for edge in edges:
            x0, y0 = node_x[edge['source']], node_y[edge['source']]
            x1, y1 = node_x[edge['target']], node_y[edge['target']]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="middle center",
            hoverinfo='text',
            marker=dict(
                size=20,
                color=[node.get('value', 1) for node in nodes],
                colorscale='Viridis',
                showscale=True
            )
        ))
        
        fig.update_layout(
            title="Supply Chain Network",
            showlegend=False,
            hovermode='closest',
            height=600
        )
        
        return fig


# Global instance
visualizer = Visualizer()

