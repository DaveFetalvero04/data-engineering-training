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

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
