# Real Estate Analytics Dashboard

## Project Overview

This is a real estate analytics dashboard built with Python, SQL, and Streamlit. It provides insights into property listings, agent performance, market trends, and buyer behavior through interactive visualizations and SQL analytics.

## Features

### Dashboard Capabilities
- Interactive property location maps
- Bar charts for city comparisons
- Pie charts for property type distribution
- Line charts for monthly trends
- Sortable data tables with export functionality

### Filtering System
- Multi-city selection
- Property type filtering
- Price range slider
- Agent selection
- Date range filtering

### SQL Analytics
- 30+ pre-built queries for property analysis
- Agent performance tracking
- Market trend analysis
- Buyer behavior analysis

## Technology Stack

- **Frontend**: Streamlit
- **Database**: MySQL
- **Data Processing**: Pandas
- **Visualization**: Plotly Express
- **Web Framework**: Python

## Installation

1. Clone the repository
2. Install required packages:
   ```
   pip install streamlit pandas plotly sqlalchemy pymysql
   ```
3. Set up MySQL database
4. Run the application:
   ```
   streamlit run app.py
   ```

## Database Setup

Create a MySQL database named `real_estate` and import the provided data files:
- listings_final_expanded.json
- property_attributes_final_expanded.json
- agents_cleaned.json
- sales_cleaned.csv
- buyers_cleaned.json

## Project Structure

```
real-estate-dashboard/
├── app.py                 # Main application
├── apps.ipynb            # SQL queries
├── data/                   # Data files
├── LICENSE                 # MIT license
└── README.md              # This file
```

## Usage

1. Start the application with `streamlit run app.py`
2. The dashboard will open in your browser at http://localhost:8501
3. Use the sidebar filters to explore the data
4. Switch between tabs to view different visualizations
5. Export filtered data using the download button

## SQL Queries

The application includes 30+ SQL queries organized by category:

- Property Analysis: Average prices, comparisons, and distributions
- Market Performance: Sales trends, days on market, and ratios
- Agent Analytics: Performance metrics, rankings, and correlations
- Buyer Behavior: Financing patterns, payment methods, and segmentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.