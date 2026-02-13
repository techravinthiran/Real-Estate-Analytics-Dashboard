import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Page config
st.set_page_config(
    page_title="Real Estate Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database Connection
def get_connection():
    """Create database connection"""
    try:
        username = "root"
        password = quote_plus("@RAVIn2004*")
        host = "localhost"
        database = "real_estate"
        
        engine = create_engine(
            f"mysql+pymysql://{username}:{password}@{host}/{database}"
        )
        return engine
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Load Data
def load_data():
    """Load and merge data from database"""
    engine = get_connection()
    if engine is None:
        return None, None
    
    try:
        # Load tables
        listings = pd.read_sql("SELECT * FROM listings", engine)
        sales = pd.read_sql("SELECT * FROM sales", engine)
        agents = pd.read_sql("SELECT * FROM agents", engine)
        property_attr = pd.read_sql("SELECT * FROM property_attributes", engine)
        
        # Convert to lowercase
        for df in [listings, sales, agents, property_attr]:
            df.columns = df.columns.str.lower()
        
        # Merge data
        merged = pd.merge(listings, property_attr, on="listing_id", how="left")
        merged = pd.merge(merged, sales, on="listing_id", how="left")
        
        # Convert dates
        merged["date_listed"] = pd.to_datetime(merged["date_listed"], errors="coerce")
        merged["date_sold"] = pd.to_datetime(merged["date_sold"], errors="coerce")
        
        return merged, agents
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

# Main App
def main():
    # Header
    st.title("Real Estate Analytics Dashboard")
    st.markdown("---")
    
    # Load data
    data, agents = load_data()
    if data is None:
        st.stop()
    
    # Side Bar Filters
    st.sidebar.header("Filters")
    
    # City Multi-select
    cities = sorted(data["city"].dropna().unique())
    selected_cities = st.sidebar.multiselect(
        "City",
        options=cities,
        default=cities[:3] if len(cities) >= 3 else cities,
        help="Filter listings by city"
    )
    
    # Property Type Dropdown
    property_types = ["All"] + sorted(data["property_type"].dropna().unique())
    selected_type = st.sidebar.selectbox(
        "Property Type",
        options=property_types,
        index=0,
        help="Filter by property type"
    )
    
    # Price Range Slider
    min_price = int(data["price"].min())
    max_price = int(data["price"].max())
    price_range = st.sidebar.slider(
        "Price Range ($)", 
        min_price, 
        max_price, 
        (min_price, max_price)
    )
    
    # Agent Searchable Dropdown
    if agents is not None and not agents.empty:
        agent_options = ["All"] + sorted(agents["name"].dropna().unique())
        selected_agent = st.sidebar.selectbox(
            "Agent",
            options=agent_options,
            index=0,
            help="Filter by agent name"
        )
    
    # Date Range Picker
    if "date_listed" in data.columns:
        min_date = data["date_listed"].min().date()
        max_date = data["date_listed"].max().date()
        date_range = st.sidebar.date_input(
            "Date Range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date,
            help="Filter by listing date range"
        )
    
    # Apply filters
    filtered_data = data.copy()
    
    if selected_cities:
        filtered_data = filtered_data[filtered_data["city"].isin(selected_cities)]
    
    if selected_type != "All":
        filtered_data = filtered_data[filtered_data["property_type"] == selected_type]
    
    filtered_data = filtered_data[
        (filtered_data["price"] >= price_range[0]) & 
        (filtered_data["price"] <= price_range[1])
    ]
    
    if 'selected_agent' in locals() and selected_agent != "All" and agents is not None:
        agent_id = agents[agents["name"] == selected_agent]["agent_id"].values[0]
        filtered_data = filtered_data[filtered_data["agent_id"] == agent_id]
    
    if 'date_range' in locals() and len(date_range) == 2:
        filtered_data = filtered_data[
            (filtered_data["date_listed"].dt.date >= date_range[0]) &
            (filtered_data["date_listed"].dt.date <= date_range[1])
        ]
    
    # Key Metrices
    st.markdown("## Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_properties = len(filtered_data)
        st.metric("Properties", f"{total_properties:,}")
    
    with col2:
        if "price" in filtered_data.columns:
            avg_price = filtered_data["price"].mean()
            st.metric("Avg Price", f"${avg_price:,.0f}")
    
    with col3:
        if "sale_price" in filtered_data.columns:
            sold_properties = filtered_data["sale_price"].notna().sum()
            st.metric("Sold", f"{sold_properties:,}")
    
    with col4:
        if "days_on_market" in filtered_data.columns:
            avg_days = filtered_data["days_on_market"].mean()
            st.metric("Avg Days", f"{avg_days:.0f}")
    
    # Visualizations
    st.markdown("## Visualizations")
    
    # Create tabs for different visualizations
    viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs(["Map", "Charts", "Trends", "Table"])
    
    with viz_tab1:
        st.subheader("Interactive Map of Property Listings")
        
        # Prepare map data
        map_cols = ["latitude", "longitude", "city", "property_type", "price"]
        map_data = filtered_data[map_cols].dropna()
        
        if not map_data.empty:
            # Create interactive map
            fig_map = px.scatter_map(
                map_data,
                lat="latitude",
                lon="longitude",
                color="city",
                size="price",
                hover_data=["city", "property_type", "price"],
                zoom=10,
                height=500,
                title="Property Listings by City"
            )
            st.plotly_chart(fig_map, width='stretch')
        else:
            st.warning("No location data available for the current filters")
    
    with viz_tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Number of Listings by City")
            if not filtered_data.empty:
                city_count = filtered_data["city"].value_counts().reset_index()
                city_count.columns = ["City", "Count"]
                
                fig_bar = px.bar(
                    city_count,
                    x="City",
                    y="Count",
                    title="Number of Listings by City",
                    color="Count"
                )
                fig_bar.update_xaxes(tickangle=45)
                st.plotly_chart(fig_bar, width='stretch')
        
        with col2:
            st.subheader("Distribution of Property Types")
            if "property_type" in filtered_data.columns:
                type_dist = filtered_data["property_type"].value_counts().reset_index()
                type_dist.columns = ["Property Type", "Count"]
                
                fig_pie = px.pie(
                    type_dist,
                    names="Property Type",
                    values="Count",
                    title="Property Type Distribution"
                )
                st.plotly_chart(fig_pie, width='stretch')
    
    with viz_tab3:
        st.subheader("Monthly Sales and Listings Trend")
        
        if "date_listed" in filtered_data.columns:
            # Monthly listings trend
            monthly_listings = filtered_data.copy()
            monthly_listings['month'] = monthly_listings['date_listed'].dt.to_period('M')
            listing_trend = monthly_listings.groupby('month').size().reset_index(name='Listings Count')
            listing_trend['month'] = listing_trend['month'].astype(str)
            
            # Listings trend
            fig_listings = px.line(
                listing_trend,
                x='month',
                y='Listings Count',
                title='Monthly Listings Trend',
                markers=True
            )
            st.plotly_chart(fig_listings, width='stretch')
            
            # Sales trend if available
            if "date_sold" in filtered_data.columns:
                monthly_sales = filtered_data.dropna(subset=["date_sold"])
                if not monthly_sales.empty:
                    monthly_sales['month'] = monthly_sales['date_sold'].dt.to_period('M')
                    sales_trend = monthly_sales.groupby('month').size().reset_index(name='Sales Count')
                    sales_trend['month'] = sales_trend['month'].astype(str)
                    
                    fig_sales = px.line(
                        sales_trend,
                        x='month',
                        y='Sales Count',
                        title='Monthly Sales Trend',
                        markers=True
                    )
                    st.plotly_chart(fig_sales, width='stretch')
        else:
            st.info("No date data available for trend analysis")
    
    with viz_tab4:
        st.subheader("Table View with Sorting")
        
        # Prepare display columns
        display_cols = [
            'listing_id', 'city', 'property_type', 'price', 
            'sqft', 'bedrooms', 'bathrooms'
        ]
        
        if 'sale_price' in filtered_data.columns:
            display_cols.append('sale_price')
        if 'days_on_market' in filtered_data.columns:
            display_cols.append('days_on_market')
        
        # Filter available columns
        available_cols = [col for col in display_cols if col in filtered_data.columns]
        display_df = filtered_data[available_cols].copy()
        
        # Format for display
        if 'price' in display_df.columns:
            display_df['price'] = display_df['price'].apply(lambda x: f"${x:,.0f}")
        
        if 'sale_price' in display_df.columns:
            display_df['sale_price'] = display_df['sale_price'].apply(
                lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
            )
        
        if 'sqft' in display_df.columns:
            display_df['sqft'] = display_df['sqft'].apply(
                lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
            )
        
        # Rename columns
        display_df = display_df.rename(columns={
            'listing_id': 'ID',
            'city': 'City',
            'property_type': 'Type',
            'price': 'Price',
            'sqft': 'Sq Ft',
            'bedrooms': 'Beds',
            'bathrooms': 'Baths',
            'sale_price': 'Sale Price',
            'days_on_market': 'Days on Market'
        })
        
        # Display table with sorting and pagination
        st.dataframe(display_df, width='stretch', hide_index=True)
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            "Download Data",
            csv,
            "properties.csv",
            "text/csv"
        )
    
    # Quick Insights
    st.markdown("## Quick Insights")
    
    if not filtered_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Market Overview")
            
            if "price" in filtered_data.columns:
                avg_price = filtered_data["price"].mean()
                median_price = filtered_data["price"].median()
                
                st.write(f"• **Average Price:** ${avg_price:,.0f}")
                st.write(f"• **Median Price:** ${median_price:,.0f}")
            
            # City insights
            if len(selected_cities) > 1:
                city_stats = filtered_data.groupby('city')['price'].agg(['count', 'mean'])
                most_expensive = city_stats['mean'].idxmax()
                most_active = city_stats['count'].idxmax()
                st.write(f"• **Most Expensive City:** {most_expensive}")
                st.write(f"• **Most Active City:** {most_active}")
            
            # Property type insights
            if "property_type" in filtered_data.columns:
                type_stats = filtered_data.groupby('property_type')['price'].mean()
                highest_priced_type = type_stats.idxmax()
                st.write(f"• **Highest Priced Type:** {highest_priced_type}")
        
        with col2:
            st.subheader("Performance Metrics")
            
            # Sales performance
            if 'sale_price' in filtered_data.columns:
                sold_data = filtered_data[filtered_data['sale_price'].notna()]
                if not sold_data.empty:
                    sale_to_list_ratio = (sold_data['sale_price'] / sold_data['price']).mean()
                    st.write(f"• **Sale-to-List Ratio:** {sale_to_list_ratio:.2f}")
                    
                    if 'days_on_market' in sold_data.columns:
                        avg_days = sold_data['days_on_market'].mean()
                        st.write(f"• **Avg Days on Market:** {avg_days:.0f}")
                    
                    # Above listing percentage
                    above_listing = (sold_data['sale_price'] > sold_data['price']).sum()
                    above_pct = (above_listing / len(sold_data)) * 100
                    st.write(f"• **Sold Above Listing:** {above_pct:.1f}%")
            
            # Market activity
            total_listings = len(filtered_data)
            if 'sale_price' in filtered_data.columns:
                sold_count = filtered_data['sale_price'].notna().sum()
                sell_through_rate = (sold_count / total_listings) * 100
                st.write(f"• **Sell-Through Rate:** {sell_through_rate:.1f}%")

if __name__ == "__main__":
    main()