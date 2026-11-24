# Exercise 1 — Q3 2026 Store Performance & Reorder Report

| Item | Detail |
|---|---|
| **Phase** | 1 — SQL and Python Integration |
| **Difficulty** | Intermediate |
| **Date assigned** | 2026-11-24 |
| **Database** | `RetailOps` (Microsoft SQL Server) |
| **Setup script** | `RetailOps_Setup.sql` (in this folder) |
| **Status** | Assigned — awaiting submission |

---

## 1. Company Onboarding — Kalinaw Retail Group

**Who we are:** Kalinaw Retail Group is a mid-sized Philippine grocery and convenience chain with 9 stores across Metro Manila, the Visayas and Mindanao. It sells about 40 core SKUs across beverages, snacks, groceries, personal care, household goods, baby products and fresh/frozen.

**Your role:** You joined this week as a **Junior Data Engineer / Analyst** on the Data & Analytics team. The business currently produces its reports by hand from Excel exports. Your team is replacing that with repeatable Python + SQL Server workflows.

**Your environment:** a SQL Server database named `RetailOps`. Run `RetailOps_Setup.sql` to build it. The script can be re-run safely and ends with a row-count check you can use to confirm the load.

---

## 2. Business Scenario

It's Monday morning. You get this email from **Ms. Liza Ramos, Head of Retail Operations**:

> "I need the Q3 store performance numbers for Thursday's leadership review. Last quarter's manual Excel report caused problems. Finance said our revenue figures didn't match theirs, and nobody could explain why. This time I want something we can trust and re-run every quarter without someone copy-pasting.
>
> I also need to know which stores are about to run out of our best-selling products. We had empty shelves in September and I don't want a repeat."

---

## 3. Business Requirements

**Reporting period:** Q3 2026, i.e. **July 1 to September 30, 2026**.

**Finance's revenue definitions:**

- **Gross Sales** = Quantity × UnitPrice
- **Discount Amount** = Gross Sales × discount rate
- **Net Revenue** = Gross Sales − Discount Amount
- **COGS** = Quantity × the product's UnitCost
- **Gross Profit** = Net Revenue − COGS. **Gross Margin %** = Gross Profit ÷ Net Revenue
- **Average Order Value (AOV)** = Net Revenue ÷ number of distinct orders
- Only **completed** orders count as revenue. Cancelled and returned orders are excluded.

**Leadership wants three things:**

1. **Monthly store performance:** for every store and every month in Q3: order count, units sold, Gross Sales, Discount Amount, Net Revenue, Gross Profit, Gross Margin %, AOV, and month-over-month Net Revenue growth %.
2. **Regional summary:** Q3 totals by region (Net Revenue, Gross Profit, Margin %, share of company Net Revenue %), ranked from highest to lowest Net Revenue.
3. **Reorder alert:**
   - Find the **top 10 products by Q3 units sold**, company-wide.
   - For each store, list any of those products where stock in the **October 1 inventory snapshot** is at or below its ReorderPoint.
   - For each row, add **Days of Cover** = QtyOnHand ÷ that store's average daily units sold of that product in **September**.
   - Sort with the most urgent items first.

---

## 4. Database Schema and Available Data

### 4.1 Table overview

| Table | Columns (type) | Notes |
|---|---|---|
| `dbo.Stores` | StoreID (INT, PK), StoreCode (VARCHAR), StoreName (NVARCHAR), Region (NVARCHAR), City (NVARCHAR), OpenDate (DATE), IsActive (BIT) | 10 rows |
| `dbo.Products` | ProductID (INT, PK), SKU, ProductName, Category, Brand, UnitCost (DECIMAL 10,2), ListPrice (DECIMAL 10,2), IsActive (BIT) | 40 rows |
| `dbo.Customers` | CustomerID (INT, PK), FirstName, LastName, Email, City, LoyaltyTier, CreatedAt (DATETIME2) | 360 rows |
| `dbo.SalesOrders` | OrderID (INT, PK), OrderNumber (VARCHAR), StoreID (FK), CustomerID (FK, NULL = walk-in), OrderDate (DATETIME2), Status (VARCHAR), PaymentMethod | ~2,900 rows, June to mid-October 2026 |
| `dbo.SalesOrderLines` | OrderLineID (INT, PK), OrderID (FK), ProductID (FK), Quantity (INT), UnitPrice (DECIMAL 10,2), DiscountPct (DECIMAL 5,2), LoadBatchID (INT), LoadedAt (DATETIME2) | ~9,000 rows. Loaded nightly by the POS integration job |
| `dbo.Inventory` | InventoryID (INT, PK), StoreID (FK), ProductID (FK), QtyOnHand (INT), ReorderPoint (INT), SnapshotDate (DATE) | Snapshot dated 2026-10-01 |

### 4.2 Relationships

```
Stores 1 ──< SalesOrders 1 ──< SalesOrderLines >── 1 Products
Stores 1 ──< Inventory   >── 1 Products
Customers 1 ──< SalesOrders   (CustomerID NULL = walk-in)
```

### 4.3 Table definitions (DDL from `RetailOps_Setup.sql`)

```sql
CREATE TABLE dbo.Stores (
    StoreID      INT IDENTITY(1,1) PRIMARY KEY,
    StoreCode    VARCHAR(10)   NOT NULL UNIQUE,
    StoreName    NVARCHAR(100) NOT NULL,
    Region       NVARCHAR(50)  NULL,
    City         NVARCHAR(50)  NULL,
    OpenDate     DATE          NULL,
    IsActive     BIT           NOT NULL DEFAULT 1
);
CREATE TABLE dbo.Products (
    ProductID    INT IDENTITY(1,1) PRIMARY KEY,
    SKU          VARCHAR(20)   NOT NULL UNIQUE,
    ProductName  NVARCHAR(150) NOT NULL,
    Category     NVARCHAR(50)  NOT NULL,
    Brand        NVARCHAR(50)  NULL,
    UnitCost     DECIMAL(10,2) NULL,
    ListPrice    DECIMAL(10,2) NOT NULL,
    IsActive     BIT           NOT NULL DEFAULT 1
);
CREATE TABLE dbo.Customers (
    CustomerID   INT IDENTITY(1,1) PRIMARY KEY,
    FirstName    NVARCHAR(50)  NOT NULL,
    LastName     NVARCHAR(50)  NOT NULL,
    Email        NVARCHAR(120) NULL,
    City         NVARCHAR(50)  NULL,
    LoyaltyTier  VARCHAR(10)   NULL,
    CreatedAt    DATETIME2(0)  NOT NULL
);
CREATE TABLE dbo.SalesOrders (
    OrderID       INT IDENTITY(1,1) PRIMARY KEY,
    OrderNumber   VARCHAR(20)  NOT NULL UNIQUE,
    StoreID       INT          NOT NULL REFERENCES dbo.Stores(StoreID),
    CustomerID    INT          NULL REFERENCES dbo.Customers(CustomerID),  -- NULL = walk-in
    OrderDate     DATETIME2(0) NOT NULL,
    Status        VARCHAR(20)  NOT NULL,
    PaymentMethod VARCHAR(20)  NULL
);
CREATE TABLE dbo.SalesOrderLines (
    OrderLineID  INT IDENTITY(1,1) PRIMARY KEY,
    OrderID      INT           NOT NULL REFERENCES dbo.SalesOrders(OrderID),
    ProductID    INT           NOT NULL REFERENCES dbo.Products(ProductID),
    Quantity     INT           NOT NULL,
    UnitPrice    DECIMAL(10,2) NULL,
    DiscountPct  DECIMAL(5,2)  NOT NULL DEFAULT 0,
    LoadBatchID  INT           NOT NULL,
    LoadedAt     DATETIME2(0)  NOT NULL
);
CREATE TABLE dbo.Inventory (
    InventoryID   INT IDENTITY(1,1) PRIMARY KEY,
    StoreID       INT          NOT NULL REFERENCES dbo.Stores(StoreID),
    ProductID     INT          NOT NULL REFERENCES dbo.Products(ProductID),
    QtyOnHand     INT          NOT NULL,
    ReorderPoint  INT          NOT NULL,
    SnapshotDate  DATE         NOT NULL
);
```

### 4.4 Sample records

**`dbo.SalesOrderLines`** (sample shown in the original assignment)

```
OrderLineID OrderID ProductID Quantity UnitPrice DiscountPct LoadBatchID LoadedAt
1           1       4         3        88.20     0.20        20260601    2026-06-02 02:15:00
2           1       18        2        99.00     0.20        20260601    2026-06-02 02:15:00
```

**Other tables** (the first rows of each table in `RetailOps_Setup.sql`)

`dbo.Products`

| ProductID | SKU | ProductName | Category | Brand | UnitCost | ListPrice | IsActive |
|---|---|---|---|---|---|---|---|
| 1 | BEV-1001 | Kopiko 3-in-1 Coffee 30s | Beverages | Kopiko | 143.14 | 215.00 | 1 |
| 2 | BEV-1002 | Nestea Iced Tea 450g | Beverages | Nestea | 133.13 | 189.00 | 1 |
| 3 | BEV-1003 | Bottled Water 6x500ml | Beverages | Wilkins | 105.49 | 120.00 | 1 |

`dbo.Customers`

| CustomerID | FirstName | LastName | Email | City | LoyaltyTier | CreatedAt |
|---|---|---|---|---|---|---|
| 1 | Patricia | Lim | patricia.lim802@yahoo.com | Davao City | Gold | 2025-05-30 18:45:54 |
| 2 | Gabriel | Dela Cruz | gabriel.delacruz886@gmail.com | Pasig | Bronze | 2023-02-13 17:53:26 |

`dbo.SalesOrders`

| OrderID | OrderNumber | StoreID | CustomerID | OrderDate | Status | PaymentMethod |
|---|---|---|---|---|---|---|
| 1 | SO-2026000001 | 1 | NULL | 2026-06-01 08:43:29 | Completed | GCash |
| 2 | SO-2026000002 | 1 | 241 | 2026-06-01 22:03:30 | Completed | Card |
| 3 | SO-2026000003 | 1 | NULL | 2026-06-01 15:07:18 | Completed | GCash |

`dbo.Inventory`

| InventoryID | StoreID | ProductID | QtyOnHand | ReorderPoint | SnapshotDate |
|---|---|---|---|---|---|
| 1 | 1 | 1 | 43 | 10 | 2026-10-01 |
| 2 | 1 | 2 | 178 | 24 | 2026-10-01 |
| 3 | 1 | 3 | 116 | 15 | 2026-10-01 |

### 4.5 Database initialization script

The full dataset (about 870 KB, ~12,700 rows across six tables) is in **`RetailOps_Setup.sql`**. Keep that file in this folder next to this document. It:

1. Drops and recreates the `RetailOps` database, so it can be re-run safely.
2. Creates the six tables above.
3. Loads all sample data with `SET IDENTITY_INSERT` batches.
4. Ends with this row-count check:

```sql
SELECT 'Stores' AS TableName, COUNT(*) AS RowCnt FROM dbo.Stores
UNION ALL SELECT 'Products', COUNT(*) FROM dbo.Products
UNION ALL SELECT 'Customers', COUNT(*) FROM dbo.Customers
UNION ALL SELECT 'SalesOrders', COUNT(*) FROM dbo.SalesOrders
UNION ALL SELECT 'SalesOrderLines', COUNT(*) FROM dbo.SalesOrderLines
UNION ALL SELECT 'Inventory', COUNT(*) FROM dbo.Inventory;
```

Run it in SSMS or Azure Data Studio (SQL Server 2017+ or Azure SQL Edge).

> ⚠️ This is production data and it has **not** been cleaned. Profile it before you trust it.

---

## 5. Tasks

1. **Connect:** write Python that connects to `RetailOps` on SQL Server. Credentials and server names must not be hard-coded in the script.
2. **Extract:** pull the data you need with SQL. Deciding what to do in SQL and what to do in Pandas is part of the job, so be ready to justify your choices.
3. **Profile and clean:** look for data quality problems that would distort the report. Fix each one or exclude it, and document every decision.
4. **Transform:** build the three outputs with Pandas, using Finance's definitions above.
5. **Deliver:** write everything to one Excel workbook.
6. **Interpret:** write a short findings note for Ms. Ramos.

---

## 6. Expected Deliverables

1. **`q3_store_report.py`**: one runnable script, organised into functions (connect, extract, clean, transform, export).
2. **`sql/` folder or embedded queries**: every SQL query you run, readable and commented.
3. **`Q3_2026_Store_Performance.xlsx`**, with four sheets:
   - `Monthly_Store_Summary`
   - `Region_Summary`
   - `Reorder_Alert`
   - `Data_Quality_Log`: every issue you found, how many rows it affected, what you did about it, and the revenue impact where you can measure it
4. **`findings.md`**: 3 to 5 business insights written for a non-technical manager, including at least one anomaly or risk.
5. **Reconciliation evidence:** proof that your total Q3 Net Revenue in Python matches an independent SQL-only calculation that applies the same rules.

**How to submit:** paste your code, the query results or a screenshot of each Excel sheet, your Data Quality Log and your findings. If you use GitHub, a repository link works too.

**Suggested folder layout:**

```
Exercise_01/
├── exercise_instructions.md
├── RetailOps_Setup.sql
├── q3_store_report.py
├── sql/
├── output/Q3_2026_Store_Performance.xlsx
└── findings.md
```

---

## 7. Acceptance Criteria

| Criterion | What will be checked |
|---|---|
| **Correctness (30%)** | Figures match the answer key to the centavo. The date range is exactly Q3. Status logic is correct. Every planted data issue is found and handled sensibly. |
| **SQL/Python implementation (25%)** | Correct use of pyodbc and/or SQLAlchemy. Parameterised queries. Good Pandas usage, not row-by-row loops. |
| **Efficiency (15%)** | No pulling whole tables when filtering in SQL makes more sense. No repeated round-trips to the database. |
| **Readability (15%)** | Functions, clear names, docstrings or comments, no dead code. |
| **Data quality & validation (10%)** | A complete Data Quality Log, the reconciliation check, and row counts checked at each step. |
| **Professional practices (5%)** | Credentials handled through config or environment variables, logging or clear console output, error handling on the connection, a re-runnable script. |

**Workplace bar:** a submission passes at **75+**, meaning Ms. Ramos could present it on Thursday. Below that, you revise and resubmit.

> The requirements are deliberately not airtight, the same as in a real job. If something is ambiguous, either ask the manager or make a documented assumption. Both are legitimate; silent guesses are not.

---

## 8. Evaluation Rubric

| Evaluation Criteria | Weight |
|---|---:|
| Correctness and accuracy | 30% |
| SQL/Python implementation | 25% |
| Efficiency and performance | 15% |
| Code readability and organization | 15% |
| Data quality and validation | 10% |
| Professional practices | 5% |
| **TOTAL** | **100%** |

The evaluation (`evaluation.md`) will include:

- Final score
- What was done correctly
- Errors and weaknesses
- How a professional Data Analyst or Data Engineer would approach the problem
- Whether the solution is acceptable in a real workplace
- Skills to improve

---

## 9. Training Rules for This Exercise

- No hints or solutions unless explicitly requested.
- The submission is evaluated before Exercise 2 is assigned.
- Scores below 75 require revision and resubmission.
