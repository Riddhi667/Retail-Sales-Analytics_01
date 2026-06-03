# Import libraries

import pandas as pd
import numpy as np

print("Libraries loaded ✓")

# Load all sheets

file_path = "USECASE - Data Engineering.xlsx"  # put the Excel file in the same folder as your notebook

product_details = pd.read_excel(file_path, sheet_name="product_details")
retail_data1    = pd.read_excel(file_path, sheet_name="retail_data1")
retail_data2    = pd.read_excel(file_path, sheet_name="retail_data2")

print("product_details:", product_details.shape)
print("retail_data1   :", retail_data1.shape)
print("retail_data2   :", retail_data2.shape)

# Merge into one raw dataset

raw_df = pd.concat([retail_data1, retail_data2], ignore_index=True)

print("Combined dataset shape:", raw_df.shape)
print("\nColumns:", raw_df.columns.tolist())
print("\nFirst 3 rows:")
raw_df.head(3)

# Inspect data quality

print("=== Missing values ===")
print(raw_df.isnull().sum())

print("\n=== Data types ===")
print(raw_df.dtypes)

print("\n=== Sample of transaction_date column ===")
print(raw_df['transaction_date'].value_counts().head(10))

# Check duplicate records

duplicate_count = raw_df.duplicated().sum()# Check invalid quantity

invalid_qty = raw_df[raw_df['quantity'] <= 0]

print("Invalid Quantity Records:", len(invalid_qty))

print("Total Duplicate Records:", duplicate_count)

# Check invalid quantity

invalid_qty = raw_df[raw_df['quantity'] <= 0]

print("Invalid Quantity Records:", len(invalid_qty))

# Standardize Categories

category_map = {
    'ELEC': 'Electronics',
    'electronics': 'Electronics',

    'HOME': 'Home Appliances',
    'home appliances': 'Home Appliances',

    'FURN': 'Furniture',
    'furniture': 'Furniture',

    'CLOTH': 'Clothing',
    'clothing': 'Clothing'
}

raw_df['category'] = raw_df['category'].replace(category_map)

print(raw_df['category'].value_counts())

# Remove Invalid Quantities

raw_df = raw_df[raw_df['quantity'] > 0]

print(raw_df.shape)

# Fill Missing Prices

merged_df = raw_df.merge(
    product_details[['product_id','price']],
    on='product_id',
    how='left',
    suffixes=('','_master')
)
print(merged_df.shape)

# Fill missing prices from master table

merged_df['price'] = merged_df['price'].fillna(
    merged_df['price_master']
)

print("Remaining Missing Prices:",
      merged_df['price'].isnull().sum())

# Drop Extra Column

merged_df.drop(
    columns=['price_master'],
    inplace=True
)

print(merged_df.shape)

# Date Cleaning

merged_df['transaction_date'] = pd.to_datetime(
    merged_df['transaction_date'],
    errors='coerce'
)
print(merged_df['transaction_date'].isnull().sum())

print(
    merged_df['transaction_date'].isnull().sum()
)

# Create date features

merged_df['Year'] = merged_df['transaction_date'].dt.year

merged_df['Month'] = merged_df['transaction_date'].dt.month_name()

merged_df['Quarter'] = merged_df['transaction_date'].dt.quarter

merged_df['Day'] = merged_df['transaction_date'].dt.day

merged_df[['transaction_date',
           'Year',
           'Month',
           'Quarter',
           'Day']].head()

# PII Masking

#Email:

def mask_email(email):

    if pd.isna(email):
        return email

    name, domain = email.split('@')

    return name[:2] + '*****@' + domain

merged_df['masked_email'] = (
    merged_df['email']
    .apply(mask_email)
)

#Phone:

def mask_phone(phone):

    phone = str(phone)

    return phone[:2] + '******' + phone[-2:]

merged_df['masked_phone'] = (
    merged_df['phone']
    .apply(mask_phone)
)

#Revenue Calculation

merged_df['Revenue'] = (
    merged_df['price']
    * merged_df['quantity']
    * (1 - merged_df['discount'])
)

merged_df[['price',
           'quantity',
           'discount',
           'Revenue']].head()

#Total Revenue KPI

total_revenue = merged_df['Revenue'].sum()

print("Total Revenue =", total_revenue)

#Revenue by Category

category_kpi = (
    merged_df.groupby('category')['Revenue']
    .sum()
    .reset_index()
)
category_kpi

#Revenue by City

city_kpi = (
    merged_df
    .groupby('city')['Revenue']
    .sum()
    .reset_index()
    .sort_values(by='Revenue', ascending=False)
)
city_kpi

#Total Orders

total_orders = merged_df['transaction_id'].nunique()

print("Total Orders:", total_orders)

#Total Customers

total_customers = merged_df['customer_id'].nunique()

print("Total Customers:", total_customers)

#Average Order Value(AOV)

avg_order_value = (
    merged_df['Revenue'].sum()
    /
    merged_df['transaction_id'].nunique()
)

print("Average Order Value:", round(avg_order_value,2))

#Revenue by Month

monthly_revenue = (
    merged_df.groupby('Month')['Revenue']
    .sum()
    .reset_index()
)
monthly_revenue

#Revenue by Quarter

quarterly_revenue = (
    merged_df.groupby('Quarter')['Revenue']
    .sum()
    .reset_index()
)
quarterly_revenue

#Top 10 Products

top_products = (
    merged_df.groupby('product_name')['Revenue']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
top_products

#Best Selling Product

best_selling = (
    merged_df.groupby('product_name')['quantity']
    .sum()
    .sort_values(ascending=False)
    .head(1)
)
best_selling

#Online vs Offline Revenue

location_kpi = (
    merged_df.groupby('purchase_location')['Revenue']
    .sum()
    .reset_index()
)
location_kpi

#Payment Method Analysis

payment_kpi = (
    merged_df.groupby('payment_method')['Revenue']
    .sum()
    .reset_index()
)
payment_kpi

#Payment Status Analysis

payment_status_kpi = (
    merged_df['payment_status']
    .value_counts()
)
payment_status_kpi

#Failed Transaction Rate

failed_rate = (
    (merged_df['payment_status'] == 'failed').sum()
    /
    len(merged_df)
) * 100

print(
    "failed Transaction Rate:",
    round(failed_rate,2),
    "%"
)

#Average Discount %

avg_discount = (
    merged_df['discount'].mean()
    * 100
)

print(
    "Average Discount:",
    round(avg_discount,2),
    "%"
)

#Revenue Lost Due to Discount

merged_df['Discount_Loss'] = (
    merged_df['price']
    * merged_df['quantity']
    * merged_df['discount']
)

total_discount_loss = (
    merged_df['Discount_Loss']
    .sum()
)

print(
    "Revenue Lost Due To Discount:",
    round(total_discount_loss,2)
)

#Highest Revenue City

highest_city = (
    merged_df.groupby('city')['Revenue']
    .sum()
    .sort_values(ascending=False)
    .head(1)
)
highest_city

#Highest Revenue Category

highest_category = (
    merged_df.groupby('category')['Revenue']
    .sum()
    .sort_values(ascending=False)
    .head(1)
)
highest_category

#Export Final Curated Dataset

merged_df.to_csv(
    'retail_curated.csv',
    index=False
)

print("Curated Dataset Saved Successfully ✓")
