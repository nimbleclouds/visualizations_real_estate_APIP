import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import statsmodels.formula.api as smf
import streamlit as st


st.set_page_config(
    page_title="Real Estate Dashboard",
    layout="wide",  # ← makes the page use the full width
    initial_sidebar_state="expanded"
)


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
    "Average Sale Price by District and Class",
    "Average Sale Price % Difference by District",
    "Total Available Area by District and Class",
    "Listing Composition by District",
    "Average Price per sqm Heatmap",
    "Property Price vs Area",
    "Property Price vs Area by Class",
    "Property Value Analysis",
    "Top Undervalued vs Overpriced Listings by Class",
    "Price per sqm Distribution by Class"
])

# --- Custom color palette ---
color_map = {
    "Office": "#a14f2a",
    "Mall": "#d8c7a3",
    "Residential": "#bfae8c",
    "Other": "#8c7a5a"
}

# --- Page 1: Average Sale Price ---
if page == "Average Sale Price by District and Class":
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
if page == "Average Sale Price % Difference by District":
    st.header("Average Sale Price % Difference by District")
    df_grouped = df.groupby(["district", "class"]).agg({"psqm":"mean"}).reset_index()
    df_grouped = df_grouped.sort_values("psqm", ascending=False)
    df_grouped['pct_diff_prev'] = df_grouped.groupby('class')['psqm'].pct_change() * 100
    df_grouped['pct_diff_prev'] = df_grouped['pct_diff_prev'].fillna(0)
    classes = df_grouped['class'].unique()
    custom_palette = ["#a14f2a", "#d8c7a3", "#bfae8c", "#8c7a5a", "#5f665a"]
    color_map = {cls: custom_palette[i % len(custom_palette)] for i, cls in enumerate(classes)}
    
    fig = make_subplots(
        rows=1, cols=len(classes),
        shared_yaxes=False,
        subplot_titles=[f"{cls} % Difference" for cls in classes]
    )
    for i, cls in enumerate(classes):
        df_cls = df_grouped[df_grouped['class'] == cls].sort_values('pct_diff_prev', ascending=True)
        fig.add_trace(
            go.Bar(
                x=df_cls['pct_diff_prev'],
                y=df_cls['district'],
                orientation='h',
                text=df_cls['pct_diff_prev'],
                texttemplate="%{text:,.0f}%",
                textposition="outside",
                marker_color=color_map[cls],
                showlegend=False
            ),
            row=1,
            col=i+1
        )
    
    fig.update_layout(
        title="Average Sale Price % Difference by District (per Class)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rockwell", color="white"),
        height=400,
        width=1200
    )
    for i in range(len(classes)):
        fig.update_xaxes(title_text="%", row=1, col=i+1, showgrid=True, gridcolor='rgba(200, 200, 200, 0.2)')
        fig.update_yaxes(title_text="District", row=1, col=i+1, showgrid=True, gridcolor='rgba(200, 200, 200, 0.2)')
    st.plotly_chart(fig, use_container_width=True)
    
if page == "Total Available Area by District and Class":
    st.header("Total Available Area by District and Class")
    df_area = df.groupby(["district", "class"])["area"].sum().reset_index()
    df_area['area'] = df_area['area'].round()
    df_total = df_area.groupby("district")["area"].sum().reset_index().sort_values(by="area", ascending=True)
    district_order = df_total["district"].tolist()
    df_area["district"] = pd.Categorical(df_area["district"], categories=district_order, ordered=True)
    df_area = df_area.merge(df_area.groupby("district")["area"].sum().reset_index().sort_values(by="area", ascending=True),on='district',how='left')
    df_area = df_area.sort_values(by=['area_y','area_x'])
    df_area.columns = ['district','class','area','area_y']
    df_area = df_area.drop(columns='area_y')
    custom_palette = ["#a14f2a", "#d8c7a3", "#bfae8c", "#8c7a5a", "#5f665a"]
    classes = df_area['class'].unique()
    color_map = {cls: custom_palette[i % len(custom_palette)] for i, cls in enumerate(classes)}
    fig = px.bar(
        df_area,
        y="district",
        x="area",
        color="class",
        text="area",
        orientation='h',  # horizontal
        color_discrete_map=color_map
    )
    fig.update_traces(
        texttemplate="%{text:,.0f} m²",
        textposition="inside"
    )
    for idx, row in df_total.iterrows():
        fig.add_annotation(
            x=row['area'],
            y=row['district'],
            text=f"{row['area']:,.0f} m²",
            showarrow=False,
            xshift=50,  # shift right for horizontal
            font=dict(color="gold", size=14, style='italic'),
        )
    fig.update_layout(
        title="Total Available Area by District and Class",
        barmode="stack",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rockwell", color="white"),
        xaxis=dict(
            title="m²",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        yaxis=dict(
            title="District",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        )
    )
    st.plotly_chart(fig, use_container_width=True)

if page == "Listing Composition by District":
    st.header("Listing Composition by District")
    df_count = df.groupby(["district", "class"]).size().reset_index(name="count")
    df_pct = df_count.copy()
    df_pct['pct'] = df_pct.groupby('district')['count'].transform(lambda x: x / x.sum())
    fig = px.bar(
        df_pct,
        x="district",
        y="pct",
        color="class",
        color_discrete_map=color_map,
        text=df_pct['pct'].map(lambda x: f"{x:.0%}")
    )
    
    fig.update_traces(textposition="inside")
    fig.update_layout(
        title="Listing Composition by District (%)",
        barmode="stack",
        yaxis=dict(title="Percentage"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rockwell", color="white")
    )
    st.plotly_chart(fig, use_container_width=True)

if page == "Average Price per sqm Heatmap":
    st.header("Average Price per sqm Heatmap")
    df_count = df.groupby(["district", "class"]).mean(numeric_only=True)['psqm'].reset_index()
    pivot = df_count.pivot(index="district", columns="class", values="psqm").fillna(0)
    fig = px.imshow(
        pivot,
        text_auto=".2s",
        color_continuous_scale=["#5b5151", "#bbb3b2"],
        labels=dict(color="Avg ₮ / sqm")
    )
    
    fig.update_layout(
        title="Average Price per sqm Heatmap (District vs Class)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rockwell", color="white"),
        coloraxis_colorbar=dict(
            x=1.02,
            thickness=15,
            len=0.8
        )
    )
    fig.update_layout(
        margin=dict(l=40, r=20, t=60, b=40)  # 👈 reduces empty space
    )
    st.plotly_chart(fig, use_container_width=True)

if page == "Property Price vs Area":
    st.header("Property Price vs Area")
    fig = px.scatter(
    df,
    x="area",
    y="price",
    size="psqm",              # 👈 bubble size
    color="class",            # 👈 use your class dimension
    hover_name="name",
    size_max=40,
    color_discrete_map=color_map  # reuse your palette
    )
    
    fig.update_layout(
        title="Property Price vs Area (Bubble = ₮/sqm)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rockwell", color="white"),
        xaxis=dict(
            title="Area (m²)",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        yaxis=dict(
            title="Total Price (₮)",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        )
    )
    
    fig.show()
    st.plotly_chart(fig, use_container_width=True)

if page == "Property Price vs Area by Class":
    st.header("Property Price vs Area by Class")
    df2 = df.copy()
    df2['label'] = ""

    top_n = df2.nlargest(10, "price").index   # 👈 change N if needed
    df2.loc[top_n, 'label'] = df2.loc[top_n, 'name']
    
    # --- Step 2: Scatter plot ---
    fig = px.scatter(
        df2,
        x="area",
        y="price",
        size="psqm",
        color="class",
        facet_col="class",
        hover_name="name",
        text="label",                 # 👈 controlled labeling
        size_max=35,
        trendline="ols",
        color_discrete_map=color_map
    )
    
    # --- Step 3: Improve label placement & marker style ---
    fig.update_traces(
        textposition="top center",
        marker=dict(opacity=0.7)      # 👈 reduce overlap clutter
    )
    
    # --- Step 4: Clean facet titles ---
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    
    # --- Step 5: Layout styling ---
    fig.update_layout(
        title="Property Price vs Area by Class (Bubble = ₮/sqm)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rockwell", color="white"),
    )
    
    # --- Step 6: Axes styling ---
    fig.update_xaxes(
        title="Area (m²)",
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.2)'
    )
    
    fig.update_yaxes(
        title="Total Price (₮)",
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.2)',
        type="log"   # 👈 log scale (VERY important for price spread)
    )
    st.plotly_chart(fig, use_container_width=True)
# Fit model with categorical variables
model = smf.ols(
    formula="price ~ area + C(Q('class')) + C(district)",
    data=df
).fit()
# Predict expected price
df["expected_price"] = model.predict(df)
# Compute value metrics
df["value_diff"] = df["price"] - df["expected_price"]
df["value_pct"] = df["value_diff"] / df["expected_price"] * 100

if page == "Property Value Analysis":
    st.header("Property Value Analysis")
    fig = px.scatter(
    df,
    x="area",
    y="price",
    size="psqm",
    color="value_pct",   # 👈 TRUE VALUE SIGNAL
    hover_name="name",
    size_max=35,
    color_continuous_scale=[
        "#a14f2a",   # overpriced (bad)
        "#d8c7a3",   # neutral
        "#5f665a"    # undervalued (good)
    ]
    )
    
    fig.update_layout(
        title="Property Value Analysis (Adjusted for District & Class)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rockwell", color="white"),
    )
    
    fig.update_xaxes(
        title="Area (m²)",
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.2)'
    )
    
    fig.update_yaxes(
        title="Total Price (₮)",
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.2)',
        type="log"
    )
    st.plotly_chart(fig, use_container_width=True)

if page == "Most Undervalued vs Overpriced Listings":
    st.header("Most Undervalued vs Overpriced Listings")
    df_sorted = df.sort_values("value_pct")
    fig = px.bar(
        df_sorted,
        x="value_pct",
        y="name",
        orientation="h",
        color="value_pct",
        color_continuous_scale=["#a14f2a", "#d8c7a3", "#5f665a"],
        text="value_pct"
    )
    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )
    fig.update_layout(
        title="Most Undervalued vs Overpriced Listings",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rockwell", color="white"),
        yaxis=dict(title=""),
        xaxis=dict(
            title="Value Difference (%)",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        )
    )
    st.plotly_chart(fig, use_container_width=True)

if page == "Top Undervalued vs Overpriced Listings by Class":
    st.header("Top Undervalued vs Overpriced Listings by Class")
    # --- Step 1: Select top N per class (best + worst) ---
    N = 5  # 👈 adjust as needed
    
    df_top = df.groupby("class", group_keys=False).apply(
        lambda x: pd.concat([
            x.nsmallest(N, "value_pct"),   # most undervalued
            x.nlargest(N, "value_pct")     # most overpriced
        ])
    )

    # Step 2: sort within each class for clean bars
    df_top = df_top.reset_index().sort_values(["value_pct"])
    
    # --- Step 3: symmetric range ---
    max_abs = df_top["value_pct"].abs().max()
    range_limit = round(max_abs / 10) * 10  # nice rounded axis
    
    # --- Step 4: Plot ---
    fig = px.bar(
        df_top,
        x="value_pct",
        y="name",
        orientation="h",
        color="value_pct",
        facet_col="class",
        color_continuous_scale=["#a14f2a", "#d8c7a3", "#5f665a"],
        text="value_pct"
    )
    
    # --- Step 5: text styling ---
    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )
    
    # --- Step 6: clean facet titles ---
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    
    # --- Step 7: layout ---
    fig.update_layout(
        title="Top Undervalued vs Overpriced Listings by Class",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rockwell", color="white"),
        showlegend=False
    )
    
    # --- Step 8: symmetric axis ---
    fig.update_xaxes(
        range=[-range_limit, range_limit],
        title="Value Difference (%)",
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.2)',
        zeroline=True,
        zerolinecolor="white",
        zerolinewidth=2
    )
    
    fig.update_yaxes(showgrid=False)
    
    fig.show()
    st.plotly_chart(fig, use_container_width=True)

if page == "Price per sqm Distribution by Class":
    st.header("Price per sqm Distribution by Class")
    # --- 1️⃣ Price Violin ---
    fig_price = px.violin(
        df,
        x="class",
        y="price",
        color="class",
        color_discrete_map=color_map,
        points="all",
        title="Price per sqm Distribution by Class"
    )
    
    # Add median labels
    for cls in df['class'].unique():
        median_val = df.loc[df['class']==cls, 'price'].median()
        fig_price.add_annotation(
            x=cls,
            y=median_val,
            text=f"Median: {median_val:,.0f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor="white",
            font=dict(color="gold", size=12)
        )
    
    fig_price.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rockwell", color="white"),
        showlegend=False
    )
    
    fig_price.update_yaxes(title="Price (₮)", showgrid=True, gridcolor='rgba(200,200,200,0.2)')
    fig_price.update_xaxes(title="Class", showgrid=False)
    
    fig_price.show()
    
    
    # --- 2️⃣ Area Violin ---
    fig_area = px.violin(
        df,
        x="class",
        y="area",
        color="class",
        color_discrete_map=color_map,
        points="all",
        title="Area Distribution by Class"
    )
    
    # Add median labels
    for cls in df['class'].unique():
        median_val = df.loc[df['class']==cls, 'area'].median()
        fig_area.add_annotation(
            x=cls,
            y=median_val,
            text=f"Median: {median_val:,.0f} m²",
            showarrow=True,
            arrowhead=2,
            arrowcolor="white",
            font=dict(color="gold", size=12)
        )
    
    fig_area.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rockwell", color="white"),
        showlegend=False
    )
    
    fig_area.update_yaxes(title="Area (m²)", showgrid=True, gridcolor='rgba(200,200,200,0.2)')
    fig_area.update_xaxes(title="Class", showgrid=False)
    
    fig_area.show()
    st.plotly_chart(fig, use_container_width=True)
