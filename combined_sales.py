import streamlit as st
import plotly.express as px
import pandas as pd

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
    df_price = df.groupby("district")["psqm"].mean().reset_index()
    fig = px.bar(
        df_price,
        x="district",
        y="psqm",
        text="psqm",
        color="psqm",
        color_continuous_scale=["#5b5151", "#bbb3b2"]
    )
    st.plotly_chart(fig, use_container_width=True)
