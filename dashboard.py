import streamlit as st
import os
import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processor import DataProcessor

# Set page config (must be first Streamlit command)
st.set_page_config(
    page_title="Airbnb NYC Dashboard",
    page_icon="🏠",
    layout="wide"
)

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Helper function to extract numeric min and max from price range strings
def extract_min_max_from_price_ranges(price_ranges):
    min_prices = []
    max_prices = []
    for range_str in price_ranges:
        try:
            parts = range_str.replace('$', '').split('-')
            min_prices.append(int(parts[0]))
            max_prices.append(int(parts[1]))
        except:
            continue
    return min(min_prices), max(max_prices)

# Initialize data processor
try:
    @st.cache_data
    def load_data():
        return DataProcessor('attached_assets/AB_NYC_2019.csv')
    
    data_processor = load_data()
    logger.info("Data loaded successfully")
except Exception as e:
    logger.error(f"Error loading data: {e}")
    data_processor = None
    st.error("Failed to load data. Please check logs.")
    st.stop()

# Title and description
st.title("🏠 NYC Airbnb Dashboard")
st.markdown("Explore Airbnb listings data in New York City")

# Sidebar for filters
st.sidebar.header("Filters")

# Get filter options
neighborhood_groups = data_processor.get_neighborhood_groups()
room_types = data_processor.get_room_types()
price_ranges = data_processor.get_price_ranges()

# Create filters in sidebar
neighborhood_group = st.sidebar.selectbox(
    "Neighborhood Group",
    ["All"] + neighborhood_groups
)
neighborhood_group = "" if neighborhood_group == "All" else neighborhood_group

room_type = st.sidebar.selectbox(
    "Room Type",
    ["All"] + room_types
)
room_type = "" if room_type == "All" else room_type

# Extract numeric price bounds and create slider
min_value, max_value = extract_min_max_from_price_ranges(price_ranges)
min_price, max_price = st.sidebar.slider(
    "Price Range ($)",
    min_value=min_value,
    max_value=max_value,
    value=(min_value, max_value)
)

# Apply filters
data_processor_filtered = data_processor.get_filtered_data(
    neighborhood_group, room_type, min_price, max_price
)

# Get overview stats
overview_stats = data_processor.get_overview_stats()
# Safely extract each stat with defaults
total_listings = overview_stats.get('total_listings', 0)
avg_price = overview_stats.get('avg_price', 0.0)
avg_reviews = overview_stats.get('avg_reviews', 0.0)
neighborhoods = overview_stats.get('neighborhoods', 0)

# Overview metrics
st.subheader("Overview")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Listings", f"{total_listings:,}")
with col2:
    st.metric("Average Price", f"${avg_price:.2f}")
with col3:
    st.metric("Average Reviews", f"{avg_reviews:.1f}")
with col4:
    st.metric("Neighborhoods", f"{neighborhoods}")

# Create tabs for different visualizations
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Price Analysis", 
    "Room Types", 
    "Availability", 
    "Reviews",
    "Map View"
])

with tab1:
    st.subheader("Price Analysis by Neighborhood")
    price_data = data_processor.get_price_by_neighborhood(neighborhood_group, room_type)
    if price_data and len(price_data) > 0:
        fig = px.bar(
            price_data,
            x='labels',
            y='average_prices',
            color='average_prices',
            labels={'labels': 'Neighborhood', 'average_prices': 'Average Price ($)'},
            title="Average Price by Neighborhood",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with tab2:
    st.subheader("Room Type Distribution")
    room_type_data = data_processor.get_room_type_distribution(neighborhood_group)
    if room_type_data and len(room_type_data) > 0:
        fig = px.pie(
            room_type_data,
            names='labels',
            values='counts',
            title="Room Type Distribution",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with tab3:
    st.subheader("Availability Analysis")
    availability_data = data_processor.get_availability_data(neighborhood_group, room_type)
    if availability_data and len(availability_data) > 0:
        fig = px.bar(
            availability_data,
            x='labels',
            y='counts',
            labels={'labels': 'Days Available (per year)', 'counts': 'Number of Listings'},
            title="Listing Availability Distribution",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with tab4:
    st.subheader("Reviews Distribution")
    reviews_data = data_processor.get_reviews_data(neighborhood_group, room_type)
    if reviews_data and len(reviews_data) > 0:
        fig = px.bar(
            reviews_data,
            x='labels',
            y='counts',
            labels={'labels': 'Review Category', 'counts': 'Number of Listings'},
            title="Review Distribution",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with tab5:
    st.subheader("Map View")
    location_data = data_processor.get_location_data(
        neighborhood_group, room_type, min_price, max_price
    )
    if location_data and len(location_data) > 0:
        df_map = pd.DataFrame(location_data)
        fig = px.scatter_mapbox(
            df_map,
            lat="latitude",
            lon="longitude",
            color="price",
            color_continuous_scale=px.colors.cyclical.IceFire,
            zoom=10,
            hover_name="name",
            hover_data={
                "price": True,
                "room_type": True
            },
            labels={
                "price": "Price ($)",
                "room_type": "Room Type"
            },
            title="Airbnb Listings in NYC",
            height=700
        )
        fig.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

# Display filtered data table
st.subheader("Filtered Listings Data")
if data_processor_filtered and len(data_processor_filtered) > 0:
    df = pd.DataFrame(data_processor_filtered)
    # Display all available columns to avoid KeyError
    st.dataframe(df, use_container_width=True)
else:
    st.info("No data available for the selected filters.")

# Footer
st.markdown("---")
st.markdown("Data source: Airbnb NYC 2019 Dataset")
