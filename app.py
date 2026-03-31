import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import json

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

# Extract queries from notebook
def get_queries_from_notebook():
    """Extract SQL queries from the notebook"""
    try:
        with open('apps.ipynb', 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        queries = {}
        
        # Define query cells with their titles and chart types
        query_configs = {
            "Q1: Average Listing Price by City": {
                "cell_index": 22,
                "chart_type": "bar",
                "x": "city",
                "y": "avg_price",
                "title": "Average Listing Price by City"
            },
            "Q2: Average Price per Sq Ft by Property Type": {
                "cell_index": 24,
                "chart_type": "bar",
                "x": "property_type",
                "y": "avg_price_per_sqft",
                "title": "Average Price per Square Foot by Property Type"
            },
            "Q3: Furnishing Status Impact on Price": {
                "cell_index": 26,
                "chart_type": "bar",
                "x": "furnishing_status",
                "y": "avg_price",
                "title": "Furnishing Status Impact on Price"
            },
            "Q4: Metro Distance vs Average Price": {
                "cell_index": 28,
                "chart_type": "bar",
                "x": "metro_category",
                "y": "avg_price",
                "title": "Metro Distance vs Average Price"
            },
            "Q5: Rented vs Non-Rented Property Prices": {
                "cell_index": 30,
                "chart_type": "bar",
                "x": "rental_status",
                "y": "avg_price",
                "title": "Rented vs Non-Rented Property Prices"
            },
            "Q6: Bedrooms & Bathrooms Effect on Pricing": {
                "cell_index": 32,
                "chart_type": "bar",
                "x": "bedrooms",
                "y": "avg_price",
                "color": "bathrooms",
                "title": "Bedrooms & Bathrooms Effect on Pricing"
            },
            "Q7: Parking & Power Backup Impact on Price": {
                "cell_index": 34,
                "chart_type": "bar",
                "x": "parking",
                "y": "avg_price",
                "color": "power_backup",
                "title": "Parking & Power Backup Impact on Price"
            },
            "Q8: Year Built vs Average Listing Price": {
                "cell_index": 36,
                "chart_type": "line",
                "x": "year_built",
                "y": "avg_price",
                "title": "Year Built vs Average Listing Price"
            },
            "Q9: Cities with Highest Median Property Prices": {
                "cell_index": 38,
                "chart_type": "bar",
                "x": "city",
                "y": "avg_price",
                "title": "Cities with Highest Median Property Prices"
            },
            "Q10: Properties Distributed Across Price Buckets": {
                "cell_index": 40,
                "chart_type": "pie",
                "names": "price_bucket",
                "values": "property_count",
                "title": "Properties Distributed Across Price Buckets"
            },
            "Q11: Average Days on Market by City": {
                "cell_index": 42,
                "chart_type": "bar",
                "x": "city",
                "y": "avg_days_on_market",
                "title": "Average Days on Market by City"
            },
            "Q12: Fastest Selling Property Types": {
                "cell_index": 44,
                "chart_type": "bar",
                "x": "property_type",
                "y": "avg_days_on_market",
                "title": "Fastest Selling Property Types"
            },
            "Q13: % Properties Sold Above Listing Price": {
                "cell_index": 46,
                "chart_type": "indicator",
                "value": "percent_above_listing",
                "title": "Properties Sold Above Listing Price (%)"
            },
            "Q14: Sale-to-List Price Ratio by City": {
                "cell_index": 48,
                "chart_type": "bar",
                "x": "city",
                "y": "sale_to_list_ratio",
                "title": "Sale-to-List Price Ratio by City"
            },
            "Q15: Listings That Took 90+ Days to Sell": {
                "cell_index": 50,
                "chart_type": "table",
                "title": "Listings That Took 90+ Days to Sell"
            },
            "Q16: Metro Distance vs Time on Market": {
                "cell_index": 52,
                "chart_type": "bar",
                "x": "metro_category",
                "y": "avg_days_on_market",
                "title": "Metro Distance vs Time on Market"
            },
            "Q17: Monthly Sales Trend": {
                "cell_index": 54,
                "chart_type": "line",
                "x": "month",
                "y": "total_sales",
                "title": "Monthly Sales Trend"
            },
            "Q18: Currently Unsold Properties": {
                "cell_index": 56,
                "chart_type": "table",
                "title": "Currently Unsold Properties (First 20)"
            },
            "Q19: Top Agents by Sales Closed": {
                "cell_index": 58,
                "chart_type": "bar",
                "x": "name",
                "y": "total_sales",
                "title": "Top Agents by Sales Closed"
            },
            "Q20: Top Agents by Total Sales Revenue": {
                "cell_index": 60,
                "chart_type": "bar",
                "x": "name",
                "y": "total_revenue",
                "title": "Top Agents by Total Sales Revenue"
            },
            "Q21: Agents Who Close Deals Fastest": {
                "cell_index": 62,
                "chart_type": "bar",
                "x": "name",
                "y": "avg_days_to_close",
                "title": "Agents Who Close Deals Fastest"
            },
            "Q22: Experience vs Deals Closed": {
                "cell_index": 64,
                "chart_type": "scatter",
                "x": "experience_years",
                "y": "total_sales",
                "title": "Experience vs Deals Closed"
            },
            "Q23: Rating Band vs Deal Closing Speed": {
                "cell_index": 66,
                "chart_type": "bar",
                "x": "rating",
                "y": "avg_days_to_close",
                "title": "Rating Band vs Deal Closing Speed"
            },
            "Q24: Commission Earned by Agent": {
                "cell_index": 68,
                "chart_type": "bar",
                "x": "name",
                "y": "avg_commission",
                "title": "Commission Earned by Agent"
            },
            "Q25: Investor vs End User Split": {
                "cell_index": 72,
                "chart_type": "pie",
                "names": "buyer_type",
                "values": "percentage",
                "title": "Investor vs End User Split (%)"
            },
            "Q26: Cities with Highest Loan Uptake Rate": {
                "cell_index": 74,
                "chart_type": "bar",
                "x": "city",
                "y": "loan_uptake_rate",
                "title": "Cities with Highest Loan Uptake Rate"
            },
            "Q27: Average Loan Amount by Buyer Type": {
                "cell_index": 76,
                "chart_type": "bar",
                "x": "buyer_type",
                "y": "avg_loan_amount",
                "title": "Average Loan Amount by Buyer Type"
            },
            "Q28: Most Common Payment Modes": {
                "cell_index": 78,
                "chart_type": "pie",
                "names": "payment_mode",
                "values": "percentage",
                "title": "Most Common Payment Modes (%)"
            },
            "Q29: Loan vs No-Loan Closing Speed": {
                "cell_index": 80,
                "chart_type": "bar",
                "x": "loan_status",
                "y": "avg_days_to_close",
                "title": "Loan vs No-Loan Closing Speed"
            }
        }
        
        for query_name, config in query_configs.items():
            cell = notebook['cells'][config['cell_index']]
            if cell['cell_type'] == 'code':
                # Extract the SQL query from the cell source
                source = ''.join(cell['source'])
                # Find the query between triple quotes
                start = source.find('"""')
                if start != -1:
                    end = source.find('"""', start + 3)
                    if end != -1:
                        query = source[start + 3:end]
                        queries[query_name] = {
                            "query": query.strip(),
                            "chart_type": config["chart_type"],
                            "title": config["title"]
                        }
                        # Add chart-specific parameters
                        for param in ["x", "y", "names", "values", "color", "value"]:
                            if param in config:
                                queries[query_name][param] = config[param]
        
        return queries
    except Exception as e:
        st.error(f"Error loading queries from notebook: {e}")
        return {}

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
    
    # Load queries from notebook
    queries = get_queries_from_notebook()
    
    if not queries:
        st.error("Could not load queries from notebook. Please ensure apps.ipynb is available.")
        return
    
    # Query selection
    selected_query = st.selectbox(
        "Choose a query to execute:",
        options=list(queries.keys()),
        index=0
    )
    
    if selected_query:
        query_config = queries[selected_query]
        
        # Execute query button
        if st.button(f"Execute: {selected_query}"):
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
