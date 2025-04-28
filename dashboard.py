import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # For 3D plots

# Page config
st.set_page_config(page_title="Book Sales Dashboard (Revised)", layout="wide")

# Title
st.title("📚 Book Portfolio Analysis Dashboard")

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/sales_data.csv")
        return df
    except FileNotFoundError:
        st.error("Error: The file 'data/sales_data.csv' was not found. Make sure it exists and the path is correct.")
        return None


df = load_data()

if df is not None:
    df["Date"] = pd.to_datetime(df["Date"])

    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    ratings = st.sidebar.multiselect("Select Ratings", options=df["Rating"].unique(), default=df["Rating"].unique())
    categories = st.sidebar.multiselect("Select Categories", options=df["Category"].unique(), default=df["Category"].unique())
    regions = st.sidebar.multiselect("Select Regions", options=df["Region"].unique(), default=df["Region"].unique())

    df_filtered = df[df["Rating"].isin(ratings) & df["Category"].isin(categories) & df["Region"].isin(regions)]

    # KPIs
    avg_price = round(df_filtered["Price"].mean(), 2)
    max_price = df_filtered["Price"].max()
    total_books = len(df_filtered)

    col1, col2, col3 = st.columns(3)
    col1.metric("💵 Average Book Price", f"£{avg_price}")
    col2.metric("📈 Highest Priced Book", f"£{max_price}")
    col3.metric("📚 Total Number of Books", total_books)

    st.markdown("---")

    st.header("Book Portfolio Overview")

    # 1. Scatter Plot: Price vs. Rating, Colored by Category
    fig_scatter = px.scatter(
        df_filtered,
        x="Rating",
        y="Price",
        color="Category",
        hover_name="Title",
        title="Price vs. Rating by Category",
        labels={"Price": "Price (£)", "Rating": "Rating"},
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    # Interpretation: Shows the relationship between price and rating for different book categories. Useful for identifying price points that align with high ratings.

    # 2. Treemap of Category Sizes and Price Contributions
    category_summary = df_filtered.groupby("Category").agg(
        {"Title": "count", "Price": "sum"}
    ).reset_index()
    fig_treemap = px.treemap(
        category_summary,
        path=["Category"],
        values="Title",  # Size of the treemap tiles based on the number of books
        color="Price",  # Color of the tiles based on the total price contribution of that category
        color_continuous_scale="RdYlGn",  # Red-Yellow-Green color scale
        title="Book Category Breakdown: Size (Number of Books) and Value (Price)",
        hover_data=["Price"],
    )
    st.plotly_chart(fig_treemap, use_container_width=True)
    # Interpretation: A hierarchical view of the book categories. The size of each tile represents the number of books, and the color represents the category's contribution to the overall price value.

    # 3. 3D Scatter Plot: Price vs. Rating vs. (Dummy Z-axis).
    # Due to limited data and the lack of a third meaningful dimension, I'm adding a dummy z-axis for visualization. Remove it in real use case.
    df_filtered['Dummy'] = 0  # create a dummy Z axis
    fig_3d = px.scatter_3d(df_filtered, x='Rating', y='Price', z='Dummy',
                          color='Category', symbol='Category',
                          hover_name='Title',
                          title='3D Visualization of Book Prices and Ratings',
                          labels={"Price": "Price (£)", "Rating": "Rating"},
                          )
    fig_3d.update_layout(scene_zaxis_visible=False)  # Hide the z-axis
    st.plotly_chart(fig_3d, use_container_width=True)
    # Interpretation: A scatter plot showing the relations between rating and price, while dummy z-axis is hide.
    # Warning: This 3D Plot is not really a three-dimensional insight and only a demo. It's better to not use it if no real third dimension is available.

    st.subheader("Book Data Table")
    st.dataframe(df_filtered.sort_values("Price", ascending=False))

else:
    st.warning("Data could not be loaded. Please check the file path and ensure the file exists.")