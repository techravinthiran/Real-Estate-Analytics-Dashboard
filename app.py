import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Page config
st.set_page_config(
    page_title="BrickView Real Estate Analytics", 
    layout="wide",
    initial_sidebar_state="collapsed"
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
        buyers = pd.read_sql("SELECT * FROM buyers", engine)
        
        # Convert to lowercase
        for df in [listings, sales, agents, property_attr, buyers]:
            df.columns = df.columns.str.lower()
        
        # Merge data
        merged = pd.merge(listings, property_attr, on="listing_id", how="left")
        merged = pd.merge(merged, sales, on="listing_id", how="left")
        merged = pd.merge(merged, agents, left_on="agent_id", right_on="agent_id", how="left")
        
        return merged, engine
    except Exception as e:
        st.error(f"Data loading error: {e}")
        return None, None

# Execute Query
def run_query(query, engine):
    """Execute SQL query and return DataFrame"""
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Query execution error: {e}")
        return pd.DataFrame()

# 30 SQL Queries with their visualizations
QUERIES = {
    "Q1: Average Listing Price by City": {
        "query": """
        SELECT city,
               ROUND(AVG(price), 2) AS avg_listing_price,
               COUNT(*) AS total_listings
        FROM listings
        GROUP BY city
        ORDER BY avg_listing_price DESC
        """,
        "chart_type": "bar",
        "x": "city",
        "y": "avg_listing_price",
        "title": "Average Listing Price by City"
    },
    
    "Q2: Average Price per Sq Ft by Property Type": {
        "query": """
        SELECT property_type,
               ROUND(AVG(price / NULLIF(sqft, 0)), 2) AS avg_price_per_sqft
        FROM listings
        GROUP BY property_type
        ORDER BY avg_price_per_sqft DESC
        """,
        "chart_type": "bar",
        "x": "property_type", 
        "y": "avg_price_per_sqft",
        "title": "Average Price per Square Foot by Property Type"
    },
    
    "Q3: Furnishing Status Impact on Price": {
        "query": """
        SELECT pa.furnishing_status,
               ROUND(AVG(l.price), 2) AS avg_price,
               COUNT(*) AS property_count
        FROM listings l
        JOIN property_attributes pa ON l.listing_id = pa.listing_id
        GROUP BY pa.furnishing_status
        ORDER BY avg_price DESC
        """,
        "chart_type": "bar",
        "x": "furnishing_status",
        "y": "avg_price", 
        "title": "Furnishing Status Impact on Price"
    },
    
    "Q4: Metro Distance vs Average Price": {
        "query": """
        SELECT
            CASE
                WHEN pa.metro_distance_km <= 2  THEN '0-2 km'
                WHEN pa.metro_distance_km <= 5  THEN '2-5 km'
                WHEN pa.metro_distance_km <= 10 THEN '5-10 km'
                ELSE '10+ km'
            END AS metro_distance_range,
            ROUND(AVG(l.price), 2) AS avg_price,
            COUNT(*) AS count
        FROM listings l
        JOIN property_attributes pa ON l.listing_id = pa.listing_id
        GROUP BY metro_distance_range
        ORDER BY avg_price DESC
        """,
        "chart_type": "bar",
        "x": "metro_distance_range",
        "y": "avg_price",
        "title": "Metro Distance vs Average Price"
    },
    
    "Q5: Rented vs Non-Rented Property Prices": {
        "query": """
        SELECT
            CASE WHEN pa.is_rented = 1 THEN 'Rented' ELSE 'Not Rented' END AS rental_status,
            ROUND(AVG(l.price), 2) AS avg_price,
            COUNT(*) AS count
        FROM listings l
        JOIN property_attributes pa ON l.listing_id = pa.listing_id
        GROUP BY rental_status
        """,
        "chart_type": "bar",
        "x": "rental_status",
        "y": "avg_price",
        "title": "Rented vs Non-Rented Property Prices"
    },
    
    "Q6: Bedrooms & Bathrooms Effect on Pricing": {
        "query": """
        SELECT pa.bedrooms,
               pa.bathrooms,
               ROUND(AVG(l.price), 2) AS avg_price,
               COUNT(*) AS count
        FROM listings l
        JOIN property_attributes pa ON l.listing_id = pa.listing_id
        WHERE pa.bedrooms IS NOT NULL AND pa.bathrooms IS NOT NULL
        GROUP BY pa.bedrooms, pa.bathrooms
        ORDER BY pa.bedrooms, pa.bathrooms
        LIMIT 15
        """,
        "chart_type": "bar",
        "x": "bedrooms",
        "y": "avg_price",
        "color": "bathrooms",
        "title": "Bedrooms & Bathrooms Effect on Pricing"
    },
    
    "Q7: Parking & Power Backup Impact on Price": {
        "query": """
        SELECT
            CASE WHEN pa.parking_available = 1 THEN 'Has Parking' ELSE 'No Parking' END AS parking,
            CASE WHEN pa.power_backup = 1 THEN 'Has Power Backup' ELSE 'No Power Backup' END AS power,
            ROUND(AVG(l.price), 2) AS avg_price,
            COUNT(*) AS count
        FROM listings l
        JOIN property_attributes pa ON l.listing_id = pa.listing_id
        GROUP BY parking, power
        ORDER BY avg_price DESC
        """,
        "chart_type": "bar",
        "x": "parking",
        "y": "avg_price",
        "color": "power",
        "title": "Parking & Power Backup Impact on Price"
    },
    
    "Q8: Year Built vs Average Listing Price": {
        "query": """
        SELECT pa.year_built,
               ROUND(AVG(l.price), 2) AS avg_price,
               COUNT(*) AS count
        FROM listings l
        JOIN property_attributes pa ON l.listing_id = pa.listing_id
        WHERE pa.year_built IS NOT NULL
        GROUP BY pa.year_built
        ORDER BY pa.year_built DESC
        LIMIT 20
        """,
        "chart_type": "line",
        "x": "year_built",
        "y": "avg_price",
        "title": "Year Built vs Average Listing Price"
    },
    
    "Q9: Cities with Highest Median Property Prices": {
        "query": """
        SELECT city,
               ROUND(AVG(price), 2) AS approx_median_price
        FROM (
            SELECT city, price,
                   ROW_NUMBER() OVER (PARTITION BY city ORDER BY price) AS rn,
                   COUNT(*) OVER (PARTITION BY city) AS cnt
            FROM listings
        )
        WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
        GROUP BY city
        ORDER BY approx_median_price DESC
        """,
        "chart_type": "bar",
        "x": "city",
        "y": "approx_median_price",
        "title": "Cities with Highest Median Property Prices"
    },
    
    "Q10: Properties Distributed Across Price Buckets": {
        "query": """
        SELECT
            CASE
                WHEN price < 500000   THEN 'Under $500K'
                WHEN price < 1000000  THEN '$500K - $1M'
                WHEN price < 2000000  THEN '$1M - $2M'
                WHEN price < 3000000  THEN '$2M - $3M'
                WHEN price < 4000000  THEN '$3M - $4M'
                ELSE 'Over $4M'
            END AS price_bucket,
            COUNT(*) AS count,
            ROUND(AVG(price), 0) AS avg_price_in_bucket
        FROM listings
        GROUP BY price_bucket
        ORDER BY MIN(price)
        """,
        "chart_type": "pie",
        "names": "price_bucket",
        "values": "count",
        "title": "Properties Distributed Across Price Buckets"
    },
    
    "Q11: Average Days on Market by City": {
        "query": """
        SELECT l.city,
               ROUND(AVG(s.days_on_market), 1) AS avg_days_on_market,
               COUNT(*) AS sales_count
        FROM sales s
        JOIN listings l ON s.listing_id = l.listing_id
        GROUP BY l.city
        ORDER BY avg_days_on_market ASC
        """,
        "chart_type": "bar",
        "x": "city",
        "y": "avg_days_on_market",
        "title": "Average Days on Market by City"
    },
    
    "Q12: Fastest Selling Property Types": {
        "query": """
        SELECT l.property_type,
               ROUND(AVG(s.days_on_market), 1) AS avg_days_on_market,
               COUNT(*) AS sales_count
        FROM sales s
        JOIN listings l ON s.listing_id = l.listing_id
        GROUP BY l.property_type
        ORDER BY avg_days_on_market ASC
        """,
        "chart_type": "bar",
        "x": "property_type",
        "y": "avg_days_on_market",
        "title": "Fastest Selling Property Types"
    },
    
    "Q13: % Properties Sold Above Listing Price": {
        "query": """
        SELECT
            COUNT(*) AS total_sales,
            SUM(CASE WHEN s.sale_price > l.price THEN 1 ELSE 0 END) AS sold_above_listing,
            ROUND(100.0 * SUM(CASE WHEN s.sale_price > l.price THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_above_listing
        FROM sales s
        JOIN listings l ON s.listing_id = l.listing_id
        """,
        "chart_type": "indicator",
        "value": "pct_above_listing",
        "title": "Properties Sold Above Listing Price (%)"
    },
    
    "Q14: Sale-to-List Price Ratio by City": {
        "query": """
        SELECT l.city,
               ROUND(AVG(s.sale_price / NULLIF(l.price, 0)), 4) AS sale_to_list_ratio
        FROM sales s
        JOIN listings l ON s.listing_id = l.listing_id
        GROUP BY l.city
        ORDER BY sale_to_list_ratio DESC
        """,
        "chart_type": "bar",
        "x": "city",
        "y": "sale_to_list_ratio",
        "title": "Sale-to-List Price Ratio by City"
    },
    
    "Q15: Listings That Took 90+ Days to Sell": {
        "query": """
        SELECT s.listing_id, l.city, l.property_type,
               l.price, s.sale_price, s.days_on_market, s.date_sold
        FROM sales s
        JOIN listings l ON s.listing_id = l.listing_id
        WHERE s.days_on_market > 90
        ORDER BY s.days_on_market DESC
        LIMIT 10
        """,
        "chart_type": "table",
        "title": "Listings That Took 90+ Days to Sell"
    },
    
    "Q16: Metro Distance vs Time on Market": {
        "query": """
        SELECT
            CASE
                WHEN pa.metro_distance_km <= 2  THEN '0-2 km'
                WHEN pa.metro_distance_km <= 5  THEN '2-5 km'
                WHEN pa.metro_distance_km <= 10 THEN '5-10 km'
                ELSE '10+ km'
            END AS metro_range,
            ROUND(AVG(s.days_on_market), 1) AS avg_days_on_market,
            COUNT(*) AS count
        FROM sales s
        JOIN listings l ON s.listing_id = l.listing_id
        JOIN property_attributes pa ON l.listing_id = pa.listing_id
        GROUP BY metro_range
        ORDER BY avg_days_on_market ASC
        """,
        "chart_type": "bar",
        "x": "metro_range",
        "y": "avg_days_on_market",
        "title": "Metro Distance vs Time on Market"
    },
    
    "Q17: Monthly Sales Trend": {
        "query": """
        SELECT DATE_FORMAT(date_sold, '%Y-%m') AS month,
               COUNT(*) AS total_sales,
               ROUND(SUM(sale_price), 2) AS total_revenue
        FROM sales
        WHERE date_sold IS NOT NULL
        GROUP BY month
        ORDER BY month
        """,
        "chart_type": "line",
        "x": "month",
        "y": "total_sales",
        "title": "Monthly Sales Trend"
    },
    
    "Q18: Currently Unsold Properties": {
        "query": """
        SELECT l.listing_id, l.city, l.property_type,
               l.price, l.sqft, l.date_listed, a.name AS agent_name
        FROM listings l
        LEFT JOIN sales s ON l.listing_id = s.listing_id
        LEFT JOIN agents a ON l.agent_id = a.agent_id
        WHERE s.listing_id IS NULL
        ORDER BY l.date_listed ASC
        LIMIT 20
        """,
        "chart_type": "table",
        "title": "Currently Unsold Properties (First 20)"
    },
    
    "Q19: Top Agents by Sales Closed": {
        "query": """
        SELECT a.agent_id, a.name,
               COUNT(s.listing_id) AS total_sales_closed
        FROM agents a
        JOIN listings l ON a.agent_id = l.agent_id
        JOIN sales s ON l.listing_id = s.listing_id
        GROUP BY a.agent_id, a.name
        ORDER BY total_sales_closed DESC
        LIMIT 10
        """,
        "chart_type": "bar",
        "x": "name",
        "y": "total_sales_closed",
        "title": "Top Agents by Sales Closed"
    },
    
    "Q20: Top Agents by Total Sales Revenue": {
        "query": """
        SELECT a.name,
               COUNT(s.listing_id) AS deals,
               ROUND(SUM(s.sale_price), 2) AS total_revenue
        FROM agents a
        JOIN listings l ON a.agent_id = l.agent_id
        JOIN sales s ON l.listing_id = s.listing_id
        GROUP BY a.name
        ORDER BY total_revenue DESC
        LIMIT 10
        """,
        "chart_type": "bar",
        "x": "name",
        "y": "total_revenue",
        "title": "Top Agents by Total Sales Revenue"
    },
    
    "Q21: Agents Who Close Deals Fastest": {
        "query": """
        SELECT a.name,
               ROUND(AVG(s.days_on_market), 1) AS avg_days_to_close,
               COUNT(*) AS deals_count
        FROM agents a
        JOIN listings l ON a.agent_id = l.agent_id
        JOIN sales s ON l.listing_id = s.listing_id
        GROUP BY a.name
        ORDER BY avg_days_to_close ASC
        LIMIT 10
        """,
        "chart_type": "bar",
        "x": "name",
        "y": "avg_days_to_close",
        "title": "Agents Who Close Deals Fastest"
    },
    
    "Q22: Experience vs Deals Closed": {
        "query": """
        SELECT name, experience_years, deals_closed, rating, avg_closing_days
        FROM agents
        ORDER BY experience_years DESC
        """,
        "chart_type": "scatter",
        "x": "experience_years",
        "y": "deals_closed",
        "title": "Experience vs Deals Closed"
    },
    
    "Q23: Rating Band vs Deal Closing Speed": {
        "query": """
        SELECT
            CASE
                WHEN a.rating >= 4.5 THEN 'Top Rated (4.5+)'
                WHEN a.rating >= 3.5 THEN 'Good (3.5-4.5)'
                ELSE 'Average (< 3.5)'
            END AS rating_band,
            ROUND(AVG(s.days_on_market), 1) AS avg_days_to_close,
            COUNT(*) AS deals
        FROM agents a
        JOIN listings l ON a.agent_id = l.agent_id
        JOIN sales s ON l.listing_id = s.listing_id
        GROUP BY rating_band
        ORDER BY avg_days_to_close ASC
        """,
        "chart_type": "bar",
        "x": "rating_band",
        "y": "avg_days_to_close",
        "title": "Rating Band vs Deal Closing Speed"
    },
    
    "Q24: Commission Earned by Agent": {
        "query": """
        SELECT a.name,
               a.commission_rate,
               COUNT(s.listing_id) AS deals,
               ROUND(SUM(s.sale_price * a.commission_rate / 100.0), 2) AS total_commission_earned
        FROM agents a
        JOIN listings l ON a.agent_id = l.agent_id
        JOIN sales s ON l.listing_id = s.listing_id
        GROUP BY a.name, a.commission_rate
        ORDER BY total_commission_earned DESC
        LIMIT 10
        """,
        "chart_type": "bar",
        "x": "name",
        "y": "total_commission_earned",
        "title": "Commission Earned by Agent"
    },
    
    "Q25: Investor vs End User Split": {
        "query": """
        SELECT buyer_type,
               COUNT(*) AS count,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
        FROM buyers
        GROUP BY buyer_type
        """,
        "chart_type": "pie",
        "names": "buyer_type",
        "values": "percentage",
        "title": "Investor vs End User Split (%)"
    },
    
    "Q26: Cities with Highest Loan Uptake Rate": {
        "query": """
        SELECT l.city,
               COUNT(b.buyer_id) AS total_buyers,
               SUM(b.loan_taken) AS loan_buyers,
               ROUND(100.0 * SUM(b.loan_taken) / COUNT(b.buyer_id), 2) AS loan_rate_pct
        FROM buyers b
        JOIN sales s ON b.sale_id = s.listing_id
        JOIN listings l ON s.listing_id = l.listing_id
        GROUP BY l.city
        ORDER BY loan_rate_pct DESC
        """,
        "chart_type": "bar",
        "x": "city",
        "y": "loan_rate_pct",
        "title": "Cities with Highest Loan Uptake Rate"
    },
    
    "Q27: Average Loan Amount by Buyer Type": {
        "query": """
        SELECT buyer_type,
               ROUND(AVG(loan_amount), 2) AS avg_loan_amount,
               COUNT(*) AS loan_count
        FROM buyers
        WHERE loan_taken = 1
        GROUP BY buyer_type
        """,
        "chart_type": "bar",
        "x": "buyer_type",
        "y": "avg_loan_amount",
        "title": "Average Loan Amount by Buyer Type"
    },
    
    "Q28: Most Common Payment Modes": {
        "query": """
        SELECT payment_mode,
               COUNT(*) AS count,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
        FROM buyers
        GROUP BY payment_mode
        ORDER BY count DESC
        """,
        "chart_type": "pie",
        "names": "payment_mode",
        "values": "percentage",
        "title": "Most Common Payment Modes (%)"
    },
    
    "Q29: Loan vs No-Loan Closing Speed": {
        "query": """
        SELECT
            CASE WHEN b.loan_taken = 1 THEN 'Loan Backed' ELSE 'No Loan' END AS purchase_type,
            ROUND(AVG(s.days_on_market), 1) AS avg_days_on_market,
            COUNT(*) AS count
        FROM buyers b
        JOIN sales s ON b.sale_id = s.listing_id
        GROUP BY purchase_type
        """,
        "chart_type": "bar",
        "x": "purchase_type",
        "y": "avg_days_on_market",
        "title": "Loan vs No-Loan Closing Speed"
    },
    
    "Q30: Top Loan Providers by Volume": {
        "query": """
        SELECT loan_provider,
               COUNT(*) AS num_loans,
               ROUND(AVG(loan_amount), 2) AS avg_loan_amount,
               ROUND(SUM(loan_amount), 2) AS total_loans_disbursed
        FROM buyers
        WHERE loan_taken = 1
          AND loan_provider IS NOT NULL
          AND loan_provider != ''
        GROUP BY loan_provider
        ORDER BY num_loans DESC
        """,
        "chart_type": "bar",
        "x": "loan_provider",
        "y": "num_loans",
        "title": "Top Loan Providers by Volume"
    }
}

# Create Chart Function
def create_chart(df, chart_config):
    """Create appropriate chart based on configuration"""
    if df.empty:
        st.warning("No data available for visualization")
        return
    
    chart_type = chart_config.get("chart_type", "bar")
    title = chart_config.get("title", "Chart")
    
    if chart_type == "bar":
        x_col = chart_config.get("x")
        y_col = chart_config.get("y")
        color_col = chart_config.get("color")
        
        if color_col and color_col in df.columns:
            fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
        else:
            fig = px.bar(df, x=x_col, y=y_col, title=title)
    
    elif chart_type == "line":
        x_col = chart_config.get("x")
        y_col = chart_config.get("y")
        fig = px.line(df, x=x_col, y=y_col, title=title)
    
    elif chart_type == "pie":
        names_col = chart_config.get("names")
        values_col = chart_config.get("values")
        fig = px.pie(df, names=names_col, values=values_col, title=title)
    
    elif chart_type == "scatter":
        x_col = chart_config.get("x")
        y_col = chart_config.get("y")
        fig = px.scatter(df, x=x_col, y=y_col, title=title)
    
    elif chart_type == "indicator":
        value_col = chart_config.get("value")
        value = df[value_col].iloc[0] if not df.empty and value_col in df.columns else 0
        fig = go.Figure(go.Indicator(
            mode = "number+gauge+delta",
            value = value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 25], 'color': "lightgray"},
                    {'range': [25, 50], 'color': "gray"},
                    {'range': [50, 75], 'color': "lightblue"},
                    {'range': [75, 100], 'color': "blue"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
    
    elif chart_type == "table":
        st.subheader(title)
        st.dataframe(df, use_container_width=True)
        return
    
    else:
        st.warning(f"Unsupported chart type: {chart_type}")
        return
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# Main Dashboard
def main():
    # Header
    st.title("🏠 BrickView Real Estate Analytics Dashboard")
    st.markdown("---")
    
    # Load data
    data, engine = load_data()
    if data is None or engine is None:
        st.error("Failed to load data. Please check database connection.")
        return
    
    # Initial Dashboard Charts
    st.header("📊 Dashboard Overview")
    
    # Create columns for initial charts
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Total Properties
        total_properties = len(data)
        st.metric("Total Properties", f"{total_properties:,}")
    
    with col2:
        # Average Price
        avg_price = data['price'].mean()
        st.metric("Average Price", f"${avg_price:,.0f}")
    
    with col3:
        # Total Sales
        total_sales = data['sale_price'].notna().sum()
        st.metric("Total Sales", f"{total_sales:,}")
    
    with col4:
        # Average Days on Market
        avg_days = data['days_on_market'].mean()
        st.metric("Avg Days on Market", f"{avg_days:.1f}")
    
    # Initial Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        # Property Type Distribution
        prop_type_counts = data['property_type'].value_counts()
        fig1 = px.pie(values=prop_type_counts.values, names=prop_type_counts.index, 
                     title="Property Type Distribution")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Price Distribution by City
        city_price = data.groupby('city')['price'].mean().sort_values(ascending=False)
        fig2 = px.bar(x=city_price.index, y=city_price.values, 
                     title="Average Price by City")
        fig2.update_xaxes(tickangle=45)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Initial Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales Trend
        if 'date_sold' in data.columns:
            sales_trend = data[data['sale_price'].notna()]
            if not sales_trend.empty:
                sales_trend['month'] = pd.to_datetime(sales_trend['date_sold']).dt.to_period('M')
                monthly_sales = sales_trend.groupby('month').size()
                fig3 = px.line(x=monthly_sales.index.astype(str), y=monthly_sales.values, 
                             title="Monthly Sales Trend")
                st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Top Agents
        agent_sales = data[data['sale_price'].notna()].groupby('name').size().sort_values(ascending=False).head(10)
        fig4 = px.bar(x=agent_sales.values, y=agent_sales.index, orientation='h',
                     title="Top 10 Agents by Sales")
        st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("---")
    
    # Query Selection Section
    st.header("🔍 Business Intelligence Queries")
    st.markdown("Select any of the 30 predefined queries to analyze specific aspects of the real estate data:")
    
    # Query selection
    selected_query = st.selectbox(
        "Choose a query to execute:",
        options=list(QUERIES.keys()),
        index=0
    )
    
    if selected_query:
        query_config = QUERIES[selected_query]
        
        # Execute query button
        if st.button(f"Execute"):
            with st.spinner("Executing query..."):
                result_df = run_query(query_config["query"], engine)
                
                if not result_df.empty:
                    st.success(f"Query executed successfully! Found {len(result_df)} records.")
                    
                    # Show query results
                    with st.expander("View Query Results"):
                        st.dataframe(result_df, use_container_width=True)
                    
                    # Create visualization
                    create_chart(result_df, query_config)
                else:
                    st.warning("No results returned from query.")

if __name__ == "__main__":
    main()
