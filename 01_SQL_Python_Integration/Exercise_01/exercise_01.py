import pyodbc
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

server = os.getenv("DB_SERVER")
database = os.getenv("DB_DATABASE")
driver = os.getenv("DB_DRIVER")

print("Server:", server)
print("Database:", database)
print("Driver:", driver)

connection_string = (
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

connection = pyodbc.connect(connection_string)

print("Successfully connected to SQL Server!")

query = """
SELECT TOP 5 *
FROM dbo.SalesOrders;
"""

df = pd.read_sql_query(query, connection)

print(df)

print("\nDataFrame Information:")
print(df.info())

print("\nDataFrame Description:")
print(df.describe())

print(df.head())
print(df.shape)
print(df.columns)
print(df.dtypes)

order_summary = df[['OrderID','StoreID',"OrderDate",'PaymentMethod']]
print(order_summary)

gcash_orders = df[df['PaymentMethod'] == 'GCash']

print(gcash_orders)

print("Total GCash Orders:", len(gcash_orders))

completed_gcash = df[
    (df['PaymentMethod'] == 'GCash') &
    (df['Status'] == 'Completed')
]

print(completed_gcash)
print("Total Orders:", len(completed_gcash))


print(df.isnull().sum())

print(df.isnull().sum().sum())


missing_customers = df[df['CustomerID'].isnull()]

print(missing_customers)

print(df[['OrderID', 'CustomerID']])

df['CustomerID'].isnull()

df['CustomerID'].isnull().sum()

print(df)

print("Original DataFrame:", len(df))
print("Missing Customers:", len(missing_customers))

cleaned_df = df.dropna(subset=['CustomerID'])

print(cleaned_df)
print("Original records:", len(df))
print("Cleaned records:", len(cleaned_df))

filled_df = df.copy()

filled_df['CustomerID'] = filled_df['CustomerID'].fillna(-1)

print(filled_df[['OrderID', 'CustomerID']])

print(df.duplicated())
print("Total duplicates:", df.duplicated().sum())

deduplicated_df = df.drop_duplicates()

print(deduplicated_df)

print("Original records:", len(df))
print("After removing duplicates:", len(deduplicated_df))

df.duplicated(subset=['OrderID'])

df['StoreID'] = df['StoreID'].astype(str)

print(df.dtypes)

print(df['OrderDate'].dtype)

print(df['OrderDate'].dt.month)
print(df['OrderDate'].dt.year)
print(df['OrderDate'].dt.day)

df['Year'] = df['OrderDate'].dt.year
df['Month'] = df['OrderDate'].dt.month
df['Day'] = df['OrderDate'].dt.day

print(df)

print(df.shape)

sorted_df = df.sort_values(by='OrderDate', ascending=False)

print(sorted_df)

sorted_df = df.sort_values(
    by=['StoreID', 'OrderID'],
    ascending=[True, True]
)

print(sorted_df)

average_customer = df.groupby('StoreID')['CustomerID'].mean()

print(average_customer)

orders_per_store = df.groupby('StoreID').size()

print(orders_per_store)

store_summary = df.groupby('StoreID').agg(
    TotalOrders=('OrderID', 'count'),
    AverageCustomerID=('CustomerID', 'mean')
)

print(store_summary)


payment_summary = df.groupby(
    ['StoreID', 'PaymentMethod']
).size().reset_index(name='TotalOrders')

print(payment_summary)