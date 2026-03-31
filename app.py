import streamlit as st
import pandas as pd
import json
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="BrickView – Real Estate Analytics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS
st.markdown("""
<style>
    .main-title {font-size:2.2rem;font-weight:700;color:#1f3c88;margin-bottom:0}
    .sub-title  {font-size:1rem;color:#6c757d;margin-bottom:1.5rem}
    .metric-card{background:#f8f9fa;border-radius:10px;padding:1rem;border-left:4px solid #1f3c88;margin-bottom:0.5rem}
    .section-header{font-size:1.2rem;font-weight:600;color:#1f3c88;border-bottom:2px solid #e9ecef;padding-bottom:4px;margin:1rem 0 0.5rem}
    .stDataFrame{font-size:0.85rem}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_db():
    listings   = pd.DataFrame(json.load(open("listings_final_expanded.json")))
    attrs      = pd.DataFrame(json.load(open("property_attributes_final_expanded.json")))
    agents     = pd.DataFrame(json.load(open("agents_cleaned.json")))
    buyers     = pd.DataFrame(json.load(open("buyers_cleaned.json")))
    sales      = pd.read_csv("sales_cleaned.csv")

    # Normalise column names
    attrs.columns   = [c.lower() for c in attrs.columns]
    agents.columns  = [c.lower() for c in agents.columns]
    buyers.columns  = [c.lower() for c in buyers.columns]
    sales.columns   = [c.lower() for c in sales.columns]
    listings.columns= [c.lower() for c in listings.columns]

    con = sqlite3.connect(":memory:", check_same_thread=False)
    listings.to_sql("listings",   con, index=False, if_exists="replace")
    attrs.to_sql("property_attributes", con, index=False, if_exists="replace")
    agents.to_sql("agents",       con, index=False, if_exists="replace")
    buyers.to_sql("buyers",       con, index=False, if_exists="replace")
    sales.to_sql("sales",         con, index=False, if_exists="replace")
    return con, listings, attrs, agents, buyers, sales

con, listings, attrs, agents, buyers, sales = init_db()

def q(sql):
    return pd.read_sql_query(sql, con)


# Sidebar
st.sidebar.markdown("## 🏠 BrickView")
st.sidebar.markdown("Real Estate Analytics Platform")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "🔍 Filters & Listings", "📈 SQL Insights (30 Queries)", "✏️ CRUD Operations"],
)

# Global sidebar filters (used by Dashboard & Filters pages)
st.sidebar.markdown("### Global Filters")
cities = ["All"] + sorted(listings["city"].dropna().unique().tolist())
sel_city = st.sidebar.selectbox("City", cities)

prop_types = ["All"] + sorted(listings["property_type"].dropna().unique().tolist())
sel_type = st.sidebar.selectbox("Property Type", prop_types)

price_min = int(listings["price"].min())
price_max = int(listings["price"].max())
sel_price = st.sidebar.slider("Price Range ($)", price_min, price_max, (price_min, price_max), step=10000)

def apply_filters(df):
    if sel_city != "All":
        df = df[df["city"] == sel_city]
    if sel_type != "All":
        df = df[df["property_type"] == sel_type]
    df = df[(df["price"] >= sel_price[0]) & (df["price"] <= sel_price[1])]
    return df

filtered_listings = apply_filters(listings.copy())

# Dashboard
if page == "📊 Dashboard":
    st.markdown('<p class="main-title">🏠 BrickView – Real Estate Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Interactive dashboard for property listings, sales & agent performance</p>', unsafe_allow_html=True)

    # KPI Row
    k1, k2, k3, k4, k5 = st.columns(5)
    merged = filtered_listings.merge(sales, on="listing_id", how="left")
    sold   = merged[merged["sale_price"].notna()]

    k1.metric("Total Listings",    f"{len(filtered_listings):,}")
    k2.metric("Sold Properties",   f"{len(sold):,}")
    k3.metric("Avg List Price",    f"${filtered_listings['price'].mean():,.0f}" if len(filtered_listings) else "N/A")
    k4.metric("Avg Sale Price",    f"${sold['sale_price'].mean():,.0f}" if len(sold) else "N/A")
    k5.metric("Avg Days on Market",f"{sold['days_on_market'].mean():.1f}" if len(sold) else "N/A")

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<p class="section-header">Average Price by City</p>', unsafe_allow_html=True)
        city_price = filtered_listings.groupby("city")["price"].mean().reset_index()
        fig = px.bar(city_price, x="city", y="price", color="city",
                     labels={"price":"Avg Price ($)","city":"City"},
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(showlegend=False, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<p class="section-header">Property Type Distribution</p>', unsafe_allow_html=True)
        type_dist = filtered_listings["property_type"].value_counts().reset_index()
        type_dist.columns = ["property_type","count"]
        fig2 = px.pie(type_dist, names="property_type", values="count",
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig2.update_layout(margin=dict(t=10))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<p class="section-header">Monthly Sales Trend</p>', unsafe_allow_html=True)
        s = sales.copy()
        s["date_sold"] = pd.to_datetime(s["date_sold"])
        s["month"] = s["date_sold"].dt.to_period("M").astype(str)
        monthly = s.groupby("month").agg(count=("sale_price","count"), revenue=("sale_price","sum")).reset_index()
        fig3 = px.line(monthly, x="month", y="count", markers=True,
                       labels={"count":"Sales","month":"Month"},
                       color_discrete_sequence=["#1f3c88"])
        fig3.update_layout(margin=dict(t=10))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.markdown('<p class="section-header">Map of Listings</p>', unsafe_allow_html=True)
        map_df = filtered_listings[["city","latitude","longitude","price","property_type"]].dropna()
        fig4 = px.scatter_mapbox(map_df, lat="latitude", lon="longitude",
                                 color="property_type", size="price",
                                 hover_name="city", hover_data={"price":True},
                                 mapbox_style="open-street-map", zoom=3, height=350,
                                 size_max=12)
        fig4.update_layout(margin=dict(t=0,b=0))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<p class="section-header">Top 10 Agents by Deals Closed</p>', unsafe_allow_html=True)
    top_agents = agents.nlargest(10,"deals_closed")[["name","deals_closed","rating","experience_years","avg_closing_days"]]
    top_agents.columns = ["Agent","Deals Closed","Rating","Exp (yrs)","Avg Closing Days"]
    fig5 = px.bar(top_agents, x="Agent", y="Deals Closed", color="Rating",
                  color_continuous_scale="Blues")
    fig5.update_layout(margin=dict(t=10))
    st.plotly_chart(fig5, use_container_width=True)

# Filters & Listings
elif page == "🔍 Filters & Listings":
    st.markdown('<p class="main-title">🔍 Property Listings Explorer</p>', unsafe_allow_html=True)

    # extra filters
    col1, col2 = st.columns(2)
    with col1:
        agent_list = ["All"] + sorted(agents["name"].tolist())
        sel_agent = st.selectbox("Agent", agent_list)
    with col2:
        date_from = st.date_input("Listed From", value=pd.to_datetime("2020-01-01"))
        date_to   = st.date_input("Listed To",   value=pd.to_datetime("2024-12-31"))

    df_view = filtered_listings.copy()
    df_view["date_listed"] = pd.to_datetime(df_view["date_listed"])
    df_view = df_view[(df_view["date_listed"] >= pd.Timestamp(date_from)) &
                      (df_view["date_listed"] <= pd.Timestamp(date_to))]

    if sel_agent != "All":
        agent_id = agents[agents["name"] == sel_agent]["agent_id"].values
        if len(agent_id):
            df_view = df_view[df_view["agent_id"] == agent_id[0]]

    st.markdown(f"**{len(df_view):,} listings** match your filters")

    # Merge with attrs for richer display
    display_cols = ["listing_id","city","property_type","price","sqft","date_listed","agent_id"]
    st.dataframe(df_view[display_cols].reset_index(drop=True), use_container_width=True, height=400)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<p class="section-header">Price Distribution</p>', unsafe_allow_html=True)
        fig = px.histogram(df_view, x="price", nbins=30, color_discrete_sequence=["#1f3c88"])
        fig.update_layout(margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown('<p class="section-header">Listings by City</p>', unsafe_allow_html=True)
        city_cnt = df_view["city"].value_counts().reset_index()
        city_cnt.columns = ["city","count"]
        fig2 = px.bar(city_cnt, x="city", y="count", color="city",
                      color_discrete_sequence=px.colors.qualitative.Set3)
        fig2.update_layout(showlegend=False, margin=dict(t=10))
        st.plotly_chart(fig2, use_container_width=True)

# 30 SQL Insights
elif page == "📈 SQL Insights (30 Queries)":
    st.markdown('<p class="main-title">📈 SQL Insights – 30 Analytical Queries</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Select a question to view the SQL query and its output</p>', unsafe_allow_html=True)

    QUERIES = {
        # Property & Pricing (10) 
        "Q01 · Avg listing price by city": (
            """
SELECT city,
       ROUND(AVG(price),2) AS avg_price,
       COUNT(*)            AS total_listings
FROM listings
GROUP BY city
ORDER BY avg_price DESC;
""",
            "bar", "city", "avg_price",
        ),
        "Q02 · Avg price per sqft by property type": (
            """
SELECT property_type,
       ROUND(AVG(price / sqft), 2) AS price_per_sqft
FROM listings
WHERE sqft > 0
GROUP BY property_type
ORDER BY price_per_sqft DESC;
""",
            "bar", "property_type", "price_per_sqft",
        ),
        "Q03 · Furnishing status vs avg price": (
            """
SELECT pa.furnishing_status,
       ROUND(AVG(l.price),2) AS avg_price,
       COUNT(*)               AS count
FROM listings l
JOIN property_attributes pa ON l.listing_id = pa.listing_id
GROUP BY pa.furnishing_status
ORDER BY avg_price DESC;
""",
            "bar", "furnishing_status", "avg_price",
        ),
        "Q04 · Metro distance impact on price": (
            """
SELECT CASE
         WHEN pa.metro_distance_km < 2  THEN '< 2 km'
         WHEN pa.metro_distance_km < 5  THEN '2-5 km'
         WHEN pa.metro_distance_km < 10 THEN '5-10 km'
         ELSE '> 10 km'
       END AS metro_bucket,
       ROUND(AVG(l.price),2) AS avg_price,
       COUNT(*) AS count
FROM listings l
JOIN property_attributes pa ON l.listing_id = pa.listing_id
GROUP BY metro_bucket
ORDER BY avg_price DESC;
""",
            "bar", "metro_bucket", "avg_price",
        ),
        "Q05 · Rented vs non-rented property prices": (
            """
SELECT pa.is_rented,
       ROUND(AVG(l.price),2) AS avg_price,
       COUNT(*) AS count
FROM listings l
JOIN property_attributes pa ON l.listing_id = pa.listing_id
GROUP BY pa.is_rented;
""",
            "bar", "is_rented", "avg_price",
        ),
        "Q06 · Bedrooms & bathrooms vs avg price": (
            """
SELECT pa.bedrooms, pa.bathrooms,
       ROUND(AVG(l.price),2) AS avg_price,
       COUNT(*) AS count
FROM listings l
JOIN property_attributes pa ON l.listing_id = pa.listing_id
GROUP BY pa.bedrooms, pa.bathrooms
ORDER BY pa.bedrooms, pa.bathrooms;
""",
            "table", None, None,
        ),
        "Q07 · Parking & power backup vs avg price": (
            """
SELECT pa.parking_available, pa.power_backup,
       ROUND(AVG(l.price),2) AS avg_price,
       COUNT(*) AS count
FROM listings l
JOIN property_attributes pa ON l.listing_id = pa.listing_id
GROUP BY pa.parking_available, pa.power_backup
ORDER BY avg_price DESC;
""",
            "bar", "parking_available", "avg_price",
        ),
        "Q08 · Year built vs avg listing price": (
            """
SELECT pa.year_built,
       ROUND(AVG(l.price),2) AS avg_price,
       COUNT(*) AS count
FROM listings l
JOIN property_attributes pa ON l.listing_id = pa.listing_id
GROUP BY pa.year_built
ORDER BY pa.year_built;
""",
            "line", "year_built", "avg_price",
        ),
        "Q09 · Median property prices by city": (
            """
SELECT city,
       ROUND(AVG(price),2)     AS mean_price,
       COUNT(*)                AS total
FROM listings
GROUP BY city
ORDER BY mean_price DESC;
""",
            "bar", "city", "mean_price",
        ),
        "Q10 · Properties by price bucket": (
            """
SELECT CASE
         WHEN price < 500000    THEN '< $500K'
         WHEN price < 1000000   THEN '$500K–$1M'
         WHEN price < 2000000   THEN '$1M–$2M'
         WHEN price < 3000000   THEN '$2M–$3M'
         ELSE '> $3M'
       END AS price_bucket,
       COUNT(*) AS count
FROM listings
GROUP BY price_bucket
ORDER BY count DESC;
""",
            "pie", "price_bucket", "count",
        ),
        # ── Sales & Market (8) ───────────────────────────────────────────────
        "Q11 · Avg days on market by city": (
            """
SELECT l.city,
       ROUND(AVG(s.days_on_market),1) AS avg_days
FROM sales s
JOIN listings l ON s.listing_id = l.listing_id
GROUP BY l.city
ORDER BY avg_days;
""",
            "bar", "city", "avg_days",
        ),
        "Q12 · Property types that sell fastest": (
            """
SELECT l.property_type,
       ROUND(AVG(s.days_on_market),1) AS avg_days
FROM sales s
JOIN listings l ON s.listing_id = l.listing_id
GROUP BY l.property_type
ORDER BY avg_days;
""",
            "bar", "property_type", "avg_days",
        ),
        "Q13 · % properties sold above listing price": (
            """
SELECT
  COUNT(*) AS total_sold,
  SUM(CASE WHEN s.sale_price > l.price THEN 1 ELSE 0 END) AS sold_above,
  ROUND(100.0 * SUM(CASE WHEN s.sale_price > l.price THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_above_list
FROM sales s
JOIN listings l ON s.listing_id = l.listing_id;
""",
            "table", None, None,
        ),
        "Q14 · Sale-to-list price ratio by city": (
            """
SELECT l.city,
       ROUND(AVG(s.sale_price / l.price), 4) AS sale_to_list_ratio
FROM sales s
JOIN listings l ON s.listing_id = l.listing_id
GROUP BY l.city
ORDER BY sale_to_list_ratio DESC;
""",
            "bar", "city", "sale_to_list_ratio",
        ),
        "Q15 · Listings that took > 90 days to sell": (
            """
SELECT l.listing_id, l.city, l.property_type, l.price,
       ROUND(s.days_on_market,1) AS days_on_market
FROM sales s
JOIN listings l ON s.listing_id = l.listing_id
WHERE s.days_on_market > 90
ORDER BY s.days_on_market DESC
LIMIT 50;
""",
            "table", None, None,
        ),
        "Q16 · Metro distance vs time on market": (
            """
SELECT CASE
         WHEN pa.metro_distance_km < 2  THEN '< 2 km'
         WHEN pa.metro_distance_km < 5  THEN '2-5 km'
         WHEN pa.metro_distance_km < 10 THEN '5-10 km'
         ELSE '> 10 km'
       END AS metro_bucket,
       ROUND(AVG(s.days_on_market),1) AS avg_days
FROM sales s
JOIN listings l ON s.listing_id = l.listing_id
JOIN property_attributes pa ON l.listing_id = pa.listing_id
GROUP BY metro_bucket
ORDER BY avg_days;
""",
            "bar", "metro_bucket", "avg_days",
        ),
        "Q17 · Monthly sales trend": (
            """
SELECT STRFTIME('%Y-%m', date_sold) AS month,
       COUNT(*) AS sales_count,
       ROUND(SUM(sale_price),0) AS total_revenue
FROM sales
GROUP BY month
ORDER BY month;
""",
            "line", "month", "sales_count",
        ),
        "Q18 · Unsold properties": (
            """
SELECT l.listing_id, l.city, l.property_type, l.price, l.date_listed
FROM listings l
LEFT JOIN sales s ON l.listing_id = s.listing_id
WHERE s.listing_id IS NULL
ORDER BY l.price DESC
LIMIT 50;
""",
            "table", None, None,
        ),
        # ── Agent Performance (6) ────────────────────────────────────────────
        "Q19 · Agents with most sales": (
            """
SELECT a.name, COUNT(s.listing_id) AS total_sales
FROM sales s
JOIN listings l ON s.listing_id = l.listing_id
JOIN agents   a ON l.agent_id    = a.agent_id
GROUP BY a.name
ORDER BY total_sales DESC
LIMIT 15;
""",
            "bar", "name", "total_sales",
        ),
        "Q20 · Top agents by total sales revenue": (
            """
SELECT a.name,
       ROUND(SUM(s.sale_price),0) AS total_revenue
FROM sales s
JOIN listings l ON s.listing_id = l.listing_id
JOIN agents   a ON l.agent_id    = a.agent_id
GROUP BY a.name
ORDER BY total_revenue DESC
LIMIT 15;
""",
            "bar", "name", "total_revenue",
        ),
        "Q21 · Agents who close deals fastest (avg_closing_days)": (
            """
SELECT name, avg_closing_days, rating, experience_years
FROM agents
ORDER BY avg_closing_days
LIMIT 15;
""",
            "bar", "name", "avg_closing_days",
        ),
        "Q22 · Experience vs deals closed": (
            """
SELECT experience_years,
       ROUND(AVG(deals_closed),1) AS avg_deals
FROM agents
GROUP BY experience_years
ORDER BY experience_years;
""",
            "line", "experience_years", "avg_deals",
        ),
        "Q23 · Rating vs avg closing days": (
            """
SELECT ROUND(rating,0) AS rating_bucket,
       ROUND(AVG(avg_closing_days),1) AS avg_days
FROM agents
GROUP BY rating_bucket
ORDER BY rating_bucket;
""",
            "bar", "rating_bucket", "avg_days",
        ),
        "Q24 · Avg commission earned per agent": (
            """
SELECT a.name,
       ROUND(SUM(s.sale_price * a.commission_rate / 100.0),0) AS commission_earned
FROM sales s
JOIN listings l ON s.listing_id = l.listing_id
JOIN agents   a ON l.agent_id    = a.agent_id
GROUP BY a.name
ORDER BY commission_earned DESC
LIMIT 15;
""",
            "bar", "name", "commission_earned",
        ),
        # ── Buyer & Financing (6) ────────────────────────────────────────────
        "Q25 · Investor vs End User split": (
            """
SELECT buyer_type,
       COUNT(*) AS count,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM buyers), 2) AS pct
FROM buyers
GROUP BY buyer_type;
""",
            "pie", "buyer_type", "count",
        ),
        "Q26 · Loan uptake by city": (
            """
SELECT l.city,
       SUM(CASE WHEN b.loan_taken = 1 THEN 1 ELSE 0 END) AS loan_count,
       COUNT(*) AS total,
       ROUND(100.0 * SUM(CASE WHEN b.loan_taken = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS loan_pct
FROM buyers b
JOIN sales s ON b.sale_id = s.listing_id
JOIN listings l ON s.listing_id = l.listing_id
GROUP BY l.city
ORDER BY loan_pct DESC;
""",
            "bar", "city", "loan_pct",
        ),
        "Q27 · Avg loan amount by buyer type": (
            """
SELECT buyer_type,
       ROUND(AVG(loan_amount),0) AS avg_loan_amount,
       COUNT(*) AS count
FROM buyers
WHERE loan_taken = 1
GROUP BY buyer_type;
""",
            "bar", "buyer_type", "avg_loan_amount",
        ),
        "Q28 · Most common payment mode": (
            """
SELECT payment_mode,
       COUNT(*) AS count,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM buyers), 2) AS pct
FROM buyers
GROUP BY payment_mode
ORDER BY count DESC;
""",
            "pie", "payment_mode", "count",
        ),
        "Q29 · Loan vs non-loan avg days on market": (
            """
SELECT CASE WHEN b.loan_taken = 1 THEN 'Loan' ELSE 'No Loan' END AS finance_type,
       ROUND(AVG(s.days_on_market),1) AS avg_days
FROM buyers b
JOIN sales s ON b.sale_id = s.listing_id
GROUP BY finance_type;
""",
            "bar", "finance_type", "avg_days",
        ),
        "Q30 · Top loan providers by volume": (
            """
SELECT loan_provider,
       COUNT(*) AS count,
       ROUND(AVG(loan_amount),0) AS avg_loan
FROM buyers
WHERE loan_taken = 1 AND loan_provider IS NOT NULL
GROUP BY loan_provider
ORDER BY count DESC
LIMIT 10;
""",
            "bar", "loan_provider", "count",
        ),
    }

    query_names = list(QUERIES.keys())
    selected_q  = st.selectbox("Choose a Question", query_names)
    sql, chart_type, x_col, y_col = QUERIES[selected_q]

    with st.expander("📋 View SQL Query", expanded=True):
        st.code(sql.strip(), language="sql")

    try:
        result = q(sql)
        st.markdown(f"**Result: {len(result):,} rows**")
        st.dataframe(result, use_container_width=True)

        if chart_type == "bar" and x_col and y_col:
            fig = px.bar(result, x=x_col, y=y_col,
                         color_discrete_sequence=["#1f3c88"],
                         labels={x_col: x_col.replace("_"," ").title(),
                                 y_col: y_col.replace("_"," ").title()})
            fig.update_layout(margin=dict(t=20))
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "pie" and x_col and y_col:
            fig = px.pie(result, names=x_col, values=y_col,
                         color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "line" and x_col and y_col:
            fig = px.line(result, x=x_col, y=y_col, markers=True,
                          color_discrete_sequence=["#1f3c88"])
            fig.update_layout(margin=dict(t=20))
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Query error: {e}")

# CRUD Operations
elif page == "✏️ CRUD Operations":
    st.markdown('<p class="main-title">✏️ CRUD Operations</p>', unsafe_allow_html=True)

    table_choice = st.selectbox("Select Table", ["listings","agents","sales","buyers","property_attributes"])

    # Read
    st.markdown('<p class="section-header">📖 View Records</p>', unsafe_allow_html=True)
    limit = st.slider("Rows to display", 5, 100, 20)
    df_table = q(f"SELECT * FROM {table_choice} LIMIT {limit}")
    st.dataframe(df_table, use_container_width=True)

    st.markdown("---")

    tab_add, tab_upd, tab_del = st.tabs(["➕ Add Record", "✏️ Update Record", "🗑️ Delete Record"])

    # Add
    with tab_add:
        st.markdown(f"**Add a new row to `{table_choice}`**")
        cols = q(f"SELECT * FROM {table_choice} LIMIT 0").columns.tolist()
        new_vals = {}
        col_pairs = st.columns(2)
        for i, col in enumerate(cols):
            new_vals[col] = col_pairs[i % 2].text_input(col, key=f"add_{col}")

        if st.button("Insert Row"):
            placeholders = ", ".join(["?" for _ in cols])
            col_str = ", ".join(cols)
            vals = [new_vals[c] for c in cols]
            try:
                con.execute(f"INSERT INTO {table_choice} ({col_str}) VALUES ({placeholders})", vals)
                con.commit()
                st.success("✅ Row inserted successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

    # Update
    with tab_upd:
        st.markdown(f"**Update a row in `{table_choice}`**")
        pk_col = st.text_input("Primary Key Column (e.g. listing_id)", key="upd_pk")
        pk_val = st.text_input("Primary Key Value", key="upd_pk_val")
        upd_col = st.text_input("Column to Update", key="upd_col")
        upd_val = st.text_input("New Value", key="upd_val")

        if st.button("Update Row"):
            try:
                con.execute(f"UPDATE {table_choice} SET {upd_col} = ? WHERE {pk_col} = ?",
                            [upd_val, pk_val])
                con.commit()
                st.success("✅ Row updated successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

    # Delete
    with tab_del:
        st.markdown(f"**Delete a row from `{table_choice}`**")
        del_pk_col = st.text_input("Primary Key Column", key="del_pk_col")
        del_pk_val = st.text_input("Primary Key Value to Delete", key="del_pk_val")

        if st.button("🗑️ Delete Row", type="primary"):
            try:
                con.execute(f"DELETE FROM {table_choice} WHERE {del_pk_col} = ?", [del_pk_val])
                con.commit()
                st.success("✅ Row deleted!")
            except Exception as e:
                st.error(f"Error: {e}")

