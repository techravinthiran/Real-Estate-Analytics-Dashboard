# 🏠 BrickView Real Estate Analytics Platform

## Project Overview

A comprehensive real estate analytics platform built with Python, MySQL, and Streamlit. This project provides deep insights into property listings, agent performance, market trends, and buyer behavior through interactive visualizations and 30+ SQL analytics queries.

## 🚀 Features

### Dashboard Capabilities
- **Interactive Overview**: Key metrics and KPIs at a glance
- **Property Analytics**: Price distributions, city comparisons, property type analysis
- **Market Trends**: Monthly sales trends, days on market analysis
- **Agent Performance**: Top performers, commission tracking, closing speed analysis
- **Buyer Insights**: Financing patterns, payment methods, investor vs end-user analysis

### Business Intelligence Queries
- **30 Pre-built SQL Queries** covering:
  - Property & Pricing Analysis (Q1-Q10)
  - Sales & Market Performance (Q11-Q18)
  - Agent Performance Analytics (Q19-Q24)
  - Buyer & Financing Behavior (Q25-Q30)

### Visualizations
- Bar charts for comparisons and rankings
- Line charts for trend analysis
- Pie charts for distribution analysis
- Scatter plots for correlations
- Indicator gauges for key metrics
- Interactive data tables with export functionality

## 🛠️ Technology Stack

- **Frontend**: Streamlit 1.28.1
- **Database**: MySQL with PyMySQL connector
- **Data Processing**: Pandas 1.5.3, NumPy 1.24.3
- **Visualization**: Plotly 5.17.0, Matplotlib 3.7.1, Seaborn 0.12.2
- **SQL Engine**: SQLAlchemy 1.4.53
- **Web Framework**: Python 3.11+

## 📋 Prerequisites

- Python 3.11+
- MySQL Server 8.0+
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Mini Project 1"
```

### 2. Create Virtual Environment
```bash
python -m venv env
env\Scripts\activate  # On Windows
source env/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Connect to MySQL and create database
mysql -u root -p
CREATE DATABASE real_estate;

# Run the setup script
python setup_database.py
```

### 5. Run the Application
```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## 📁 Project Structure

```
Mini Project 1/
├── app.py                    # Main Streamlit dashboard
├── apps.ipynb                # Jupyter notebook with 30 SQL queries
├── brickview_complete.ipynb  # Complete structured notebook
├── setup_database.py        # Database setup script
├── requirements.txt          # Python dependencies
├── dataset/                  # Raw data files
│   ├── listings_final_expanded.json
│   ├── property_attributes_final_expanded.json
│   ├── agents_cleaned.json
│   ├── buyers_cleaned.json
│   └── sales_cleaned.csv
├── .gitignore               # Git ignore rules
├── README.md               # This file
└── LICENSE                 # MIT license
```

## 📊 Database Schema

### Tables Overview
- **listings**: Property listings (21,200 records)
- **property_attributes**: Property features and amenities
- **agents**: Real estate agent information (50 agents)
- **sales**: Transaction data (720 sales)
- **buyers**: Buyer information and financing details (20,000 buyers)

### Key Relationships
- `listings.agent_id` → `agents.agent_id`
- `listings.listing_id` → `property_attributes.listing_id`
- `listings.listing_id` → `sales.listing_id`
- `sales.listing_id` → `buyers.sale_id`

## 🎯 Usage Guide

### Dashboard Navigation
1. **Overview Section**: View key metrics and initial charts
2. **Query Explorer**: Select from 30 pre-defined business questions
3. **Interactive Visualizations**: Click on any query to see results and charts
4. **Data Export**: Download query results as CSV

### Jupyter Notebook Analysis
- Open `apps.ipynb` for detailed step-by-step analysis
- Run cells sequentially for complete data processing pipeline
- Contains all 30 SQL queries with detailed explanations

## 📈 Business Questions Answered

### Property & Pricing Analysis
- Q1: Average listing price by city
- Q2: Average price per square foot by property type
- Q3: Furnishing status impact on price
- Q4: Metro distance vs average price
- Q5: Rented vs non-rented property prices
- Q6: Bedrooms & bathrooms effect on pricing
- Q7: Parking & power backup impact on price
- Q8: Year built vs average listing price
- Q9: Cities with highest median property prices
- Q10: Properties distributed across price buckets

### Sales & Market Performance
- Q11: Average days on market by city
- Q12: Fastest selling property types
- Q13: % Properties sold above listing price
- Q14: Sale-to-list price ratio by city
- Q15: Listings that took 90+ days to sell
- Q16: Metro distance vs time on market
- Q17: Monthly sales trend
- Q18: Currently unsold properties

### Agent Performance Analytics
- Q19: Top agents by sales closed
- Q20: Top agents by total sales revenue
- Q21: Agents who close deals fastest
- Q22: Experience vs deals closed
- Q23: Rating band vs deal closing speed
- Q24: Commission earned by agent

### Buyer & Financing Behavior
- Q25: Investor vs end user split
- Q26: Cities with highest loan uptake rate
- Q27: Average loan amount by buyer type
- Q28: Most common payment modes
- Q29: Loan vs no-loan closing speed
- Q30: Top loan providers by volume

## 🔧 Configuration

### Database Connection
Update the connection details in `app.py` if needed:
```python
username = "root"
password = "your_password"  # Update this
host = "localhost"
database = "real_estate"
```

### Custom Queries
Add new SQL queries to the `QUERIES` dictionary in `app.py` following the existing format.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Development Notes

- The project uses SQLAlchemy 1.4.53 for compatibility with pandas
- All column names are normalized to lowercase for consistency
- Data preprocessing includes type conversion and duplicate removal
- Visualizations automatically adapt to query results

## 🐛 Troubleshooting

### Common Issues
1. **Database Connection Error**: Check MySQL server status and credentials
2. **ModuleNotFoundError**: Run `pip install -r requirements.txt`
3. **SQLAlchemy Version Issues**: Ensure version 1.4.53 is installed
4. **Port Already in Use**: Change Streamlit port with `streamlit run app.py --server.port 8502`

### Performance Tips
- Use indexes on frequently queried columns
- Limit query results for large datasets
- Cache expensive computations in production

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

For questions or support, please open an issue in the repository.

---

**Built with ❤️ for Guvi Mini Project**