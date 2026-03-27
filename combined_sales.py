import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import statsmodels.formula.api as smf
import streamlit as st
# --- Load your dataframe ---
office = pd.read_excel('All_Sales_Prices (2).xlsx',sheet_name='Office Sale')
res = pd.read_excel('All_Sales_Prices (2).xlsx',sheet_name='Residential Sale')
mall = pd.read_excel('All_Sales_Prices (2).xlsx',sheet_name='Mall Sale')
office['class'] = 'OFFICE'
res['class'] = 'RESIDENTIAL'
mall['class'] = 'MALL'
df = pd.concat([office,res,mall])

# --- Sidebar menu ---
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a chart", [
    "Average Sale Price",
    "Total Area",
    "Listings Count",
    "Price vs Area Scatter",
    "Price & Area Violin",
    "Heatmap"
])

# --- Custom color palette ---
color_map = {
    "Office": "#a14f2a",
    "Mall": "#d8c7a3",
    "Residential": "#bfae8c",
    "Other": "#8c7a5a"
}

# --- Page 1: Average Sale Price ---
if page == "Average Sale Price":
    st.header("Average Sale Price by District")
    df_grouped = df.groupby(["district", "class"]).agg({"price": "mean"}).reset_index()
    df_total = df_grouped.groupby("district")["price"].sum().reset_index()
    df_total = df_total.sort_values("price", ascending=False)
    district_order = df_total["district"].tolist()
    df_grouped["district"] = pd.Categorical(df_grouped["district"], categories=district_order, ordered=True)
    df_grouped = df_grouped.sort_values("district")
    custom_palette = ["#a14f2a", "#d8c7a3", "#bfae8c", "#8c7a5a", "#5f665a"]
    fig = go.Figure()
    classes = df_grouped['class'].unique()
    for i, cls in enumerate(classes):
        df_cls = df_grouped[df_grouped['class'] == cls]
        fig.add_trace(go.Bar(
            x=df_cls['district'],
            y=df_cls['price'],
            name=cls,
            marker_color=custom_palette[i % len(custom_palette)],
            text=df_cls['price'],
            texttemplate="₮%{text:,.0f}",
            textposition="inside"
        ))
    for idx, row in df_total.iterrows():
        fig.add_annotation(
            x=row['district'],
            y=row['price'],
            text=f"₮{row['price']:,.0f}",  # format as MNT
            showarrow=False,
            yshift=7,
            font=dict(color="gold", size=14, style='italic')
        )
    fig.update_layout(
        title="Average Sale Price by District and Class (Total on Top)",
        barmode="stack",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rockwell", color="white"),
        xaxis=dict(
            title="District",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        yaxis=dict(
            title="Average Price (MNT)",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    
