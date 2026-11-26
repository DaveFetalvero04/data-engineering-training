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