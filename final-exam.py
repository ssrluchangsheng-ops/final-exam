import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from functools import reduce

# -----------------------------
# Page configuration
st.set_page_config(page_title="ShopEasy Sales & Inventory Dashboard", layout="wide")
st.title("ShopEasy Sales & Inventory Management Dashboard")

# -----------------------------
# 1. Generate sales dataset (same as before)
@st.cache_data
def generate_sales_data():
    np.random.seed(42)
    products = [
        ("Laptop", "Electronics"), ("Mouse", "Electronics"), ("Keyboard", "Electronics"),
        ("Monitor", "Electronics"), ("Phone", "Electronics"), ("Headphones", "Electronics"),
        ("T-shirt", "Fashion"), ("Jeans", "Fashion"), ("Sneakers", "Fashion"),
        ("Novel", "Books"), ("Notebook", "Stationery"), ("Pen", "Stationery"),
        ("Desk Lamp", "Home"), ("Water Bottle", "Home"), ("Backpack", "Fashion")
    ]
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    data = []
    for _ in range(80):
        product_name, category = products[np.random.randint(0, len(products))]
        quantity_sold = np.random.randint(1, 10)
        unit_price = np.random.choice([25, 50, 80, 120, 200, 350, 500])
        random_date = np.random.choice(dates)
        data.append({
            "product_name": product_name,
            "category": category,
            "quantity_sold": quantity_sold,
            "unit_price": unit_price,
            "date": random_date
        })
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['revenue'] = df['quantity_sold'] * df['unit_price']
    return df

# -----------------------------
# 2. Generate inventory dataset (separate)
@st.cache_data
def generate_inventory_data():
    # Use the same product list as sales, but ensure all products are unique
    product_list = [
        ("Laptop", "Electronics"), ("Mouse", "Electronics"), ("Keyboard", "Electronics"),
        ("Monitor", "Electronics"), ("Phone", "Electronics"), ("Headphones", "Electronics"),
        ("T-shirt", "Fashion"), ("Jeans", "Fashion"), ("Sneakers", "Fashion"),
        ("Novel", "Books"), ("Notebook", "Stationery"), ("Pen", "Stationery"),
        ("Desk Lamp", "Home"), ("Water Bottle", "Home"), ("Backpack", "Fashion")
    ]
    np.random.seed(123)  # different seed for variety
    stocks = []
    for product_name, category in product_list:
        stock_qty = np.random.randint(0, 150)  # random stock between 0 and 150
        stocks.append({
            "product_name": product_name,
            "category": category,
            "stock_quantity": stock_qty
        })
    df_inv = pd.DataFrame(stocks)
    return df_inv

sales_df = generate_sales_data()
inventory_df = generate_inventory_data()

st.success(f"Sales data: {len(sales_df)} rows | Inventory data: {len(inventory_df)} products")

# -----------------------------
# 3. Sidebar filters for sales data (as before)
st.sidebar.header("🔍 Sales Data Filters")

all_categories = sorted(sales_df["category"].unique())
selected_category = st.sidebar.selectbox("Product Category (Sales)", ["All"] + all_categories)

min_date = sales_df["date"].min().date()
max_date = sales_df["date"].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Apply filters to sales data
filtered_sales = sales_df.copy()
if selected_category != "All":
    filtered_sales = filtered_sales[filtered_sales["category"] == selected_category]
if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    filtered_sales = filtered_sales[(filtered_sales["date"] >= start_date) & (filtered_sales["date"] <= end_date)]
elif len(date_range) == 1:
    selected_date = pd.to_datetime(date_range[0])
    filtered_sales = filtered_sales[filtered_sales["date"] == selected_date]

# -----------------------------
# 4. Sales KPI cards (same as Part A)
total_revenue = filtered_sales["revenue"].sum()
total_units_sold = filtered_sales["quantity_sold"].sum()
avg_selling_price = filtered_sales["unit_price"].mean() if len(filtered_sales) > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Revenue (RM)", f"{total_revenue:,.2f}")
col2.metric("📦 Total Units Sold", f"{total_units_sold:,}")
col3.metric("🏷️ Average Selling Price (RM)", f"{avg_selling_price:.2f}")

st.markdown("---")

# -----------------------------
# 5. Visualizations (Part B)
st.subheader("📊 Sales Visualizations")

if filtered_sales.empty:
    st.warning("No sales data for the selected filters. Adjust filters.")
else:
    # Bar chart: revenue by category
    col_bar, col_pie = st.columns(2)
    with col_bar:
        st.markdown("#### Total Revenue by Category")
        cat_revenue = filtered_sales.groupby("category")["revenue"].sum().sort_values(ascending=False)
        fig_bar, ax_bar = plt.subplots(figsize=(6,4))
        sns.barplot(x=cat_revenue.values, y=cat_revenue.index, palette="viridis", ax=ax_bar)
        ax_bar.set_xlabel("Revenue (RM)")
        ax_bar.set_ylabel("Category")
        for i, v in enumerate(cat_revenue.values):
            ax_bar.text(v+50, i, f"{v:,.0f}", va='center')
        st.pyplot(fig_bar)
    with col_pie:
        st.markdown("#### Revenue Share by Category")
        cat_pct = cat_revenue[cat_revenue > cat_revenue.sum() * 0.01]
        fig_pie, ax_pie = plt.subplots(figsize=(6,4))
        ax_pie.pie(cat_pct, labels=cat_pct.index, autopct='%1.1f%%', startangle=90)
        ax_pie.axis('equal')
        st.pyplot(fig_pie)

    # Line chart: weekly trend
    st.markdown("#### Weekly Sales Trend")
    df_trend = filtered_sales.set_index('date')
    weekly_revenue = df_trend['revenue'].resample('W-MON').sum().reset_index()
    if not weekly_revenue.empty:
        fig_line, ax_line = plt.subplots(figsize=(12,5))
        ax_line.plot(weekly_revenue['date'], weekly_revenue['revenue'], marker='o', linestyle='-')
        ax_line.set_title("Weekly Total Revenue")
        ax_line.set_xlabel("Date (Week starting Monday)")
        ax_line.set_ylabel("Revenue (RM)")
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        st.pyplot(fig_line)
    else:
        st.info("Insufficient data for weekly trend.")

st.markdown("---")

# -----------------------------
# 6. INVENTORY MANAGEMENT SECTION (Part C)
st.subheader("📦 Inventory Management")

# 6.1 User-defined threshold slider
threshold = st.slider(
    "Low stock threshold (units)",
    min_value=0, max_value=100, value=20, step=5,
    help="Products with stock below this value will be flagged as low stock."
)

# 6.2 Inventory category filter (optional, separate from sales)
inv_categories = ["All"] + sorted(inventory_df["category"].unique())
selected_inv_category = st.selectbox("Filter inventory by category", inv_categories, key="inv_cat")

filtered_inv = inventory_df.copy()
if selected_inv_category != "All":
    filtered_inv = filtered_inv[filtered_inv["category"] == selected_inv_category]

# 6.3 Functional programming to identify low-stock products
# Using filter + map + reduce
# Step 1: Convert filtered_inv to list of dicts for functional operations
inv_dicts = filtered_inv.to_dict('records')

# Step 2: filter products with stock < threshold
low_stock_items = list(filter(lambda item: item["stock_quantity"] < threshold, inv_dicts))

# Step 3: map to get stock quantities
low_stock_qtys = list(map(lambda item: item["stock_quantity"], low_stock_items))

# Step 4: reduce to calculate total units at risk (sum)
total_risk_units = reduce(lambda x, y: x + y, low_stock_qtys, 0)

# Step 5: Also using list comprehension (alternative functional style) to extract product names
low_stock_names = [item["product_name"] for item in low_stock_items]  # list comp is also functional

# Display warning if any low-stock products exist
if low_stock_items:
    st.warning(f"⚠️ {len(low_stock_items)} product(s) have stock below {threshold} units! Total risk units: {total_risk_units}")
    st.markdown("**Low stock products:**")
    for item in low_stock_items:
        st.write(f"- {item['product_name']} ({item['category']}): {item['stock_quantity']} units")
else:
    st.success(f"✅ All products have stock ≥ {threshold} units. No alert needed.")

# 6.4 Display full inventory table with highlighting (using pandas Styler)
st.markdown("### Complete Inventory List (with low stock highlighted)")

# Create a function to highlight rows where stock < threshold
def highlight_low_stock(row):
    if row['stock_quantity'] < threshold:
        return ['background-color: #ffcccc'] * len(row)  # light red
    else:
        return [''] * len(row)

# Apply style to the filtered_inv DataFrame (or full inventory? We show filtered_inv as per category filter)
styled_inv = filtered_inv.style.apply(highlight_low_stock, axis=1)
# Format numbers
styled_inv = styled_inv.format({'stock_quantity': '{:.0f}'})

# Display the styled DataFrame
st.dataframe(styled_inv, use_container_width=True, hide_index=True)

# Optionally show a note about functional programming used
with st.expander("ℹ️ Functional programming used in this section"):
    st.code("""
# Filter low stock items
low_stock_items = list(filter(lambda item: item['stock_quantity'] < threshold, inv_dicts))

# Map to get quantities
low_stock_qtys = list(map(lambda item: item['stock_quantity'], low_stock_items))

# Reduce to sum risk units
total_risk_units = reduce(lambda x, y: x + y, low_stock_qtys, 0)

# List comprehension (functional) to get names
low_stock_names = [item['product_name'] for item in low_stock_items]
    """, language='python')

st.markdown("---")

# -----------------------------
# 7. Sales details table (as before)
st.subheader("📋 Filtered Sales Details")
if not filtered_sales.empty:
    display_sales = filtered_sales.copy()
    display_sales['date'] = display_sales['date'].dt.date
    st.dataframe(
        display_sales,
        use_container_width=True,
        hide_index=True,
        column_config={
            "product_name": "Product Name",
            "category": "Category",
            "quantity_sold": "Quantity Sold",
            "unit_price": st.column_config.NumberColumn("Unit Price (RM)", format="RM %.2f"),
            "revenue": st.column_config.NumberColumn("Revenue (RM)", format="RM %.2f"),
            "date": "Sale Date"
        }
    )
    st.caption(f"Showing {len(filtered_sales)} sales records (out of {len(sales_df)} total)")
else:
    st.info("No sales records match the selected filters.")
