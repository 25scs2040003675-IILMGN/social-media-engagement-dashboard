# Power BI Dashboard Guide
## Social Media Engagement Analytics Dashboard

This guide walks you through importing the project data into Power BI Desktop
and building each dashboard page step by step.

---

## Prerequisites

- **Power BI Desktop** installed (free from https://powerbi.microsoft.com)
- The file `data/processed/youtube_cleaned_data.csv` exists
  (run `python main.py run-all` to generate it)

---

## Step 1 — Import the Processed CSV

1. Open **Power BI Desktop**
2. Click **Home → Get Data → Text/CSV**
3. Browse to `data/processed/youtube_cleaned_data.csv`
4. Click **Open → Load**

> 💡 The CSV has already been cleaned and enriched with all calculated columns
> (engagement_rate, performance_category, posting_time_group, etc.)
> so no complex Power Query transformations are needed.

---

## Step 2 — Optional: Connect to SQLite Database

Power BI Desktop cannot connect to SQLite natively without an ODBC driver.

**Option A — Use the CSV (recommended for beginners)**
Use the CSV as described above. It contains all the same data.

**Option B — SQLite via ODBC**
1. Download the SQLite ODBC driver from http://www.ch-werner.de/sqliteodbc/
2. Install and create a DSN pointing to `data/social_media.db`
3. In Power BI: **Home → Get Data → ODBC**
4. Select your SQLite DSN → select `youtube_engagement` table

**Option C — MySQL**
If you used MySQL as the database:
1. **Home → Get Data → MySQL Database**
2. Enter host, database name, and credentials

---

## Step 3 — Power Query Validation

After loading, open **Transform Data (Power Query Editor)**.

### Check data types
Ensure these columns have the correct type:

| Column | Expected Type |
|--------|--------------|
| video_id | Text |
| title | Text |
| channel_title | Text |
| published_at | Date/Time |
| publication_date | Date |
| publication_year | Whole Number |
| publication_month | Whole Number |
| publication_hour | Whole Number |
| view_count | Whole Number |
| like_count | Whole Number |
| comment_count | Whole Number |
| engagement_rate | Decimal Number |
| like_rate | Decimal Number |
| comment_rate | Decimal Number |
| video_duration_minutes | Decimal Number |
| performance_category | Text |
| posting_time_group | Text |
| duration_category | Text |
| publication_day_name | Text |

To change a type: **right-click the column header → Change Type → [type]**

### Handle null values
- In the `is_outlier` column: replace `null` with `0`
- In `duration_category`: replace `null` with `"Unknown"`

### Remove unnecessary columns (optional)
Consider removing: `description`, `tags`, `favorite_count`, `duration`
(the raw ISO string) to reduce file size.

Click **Close & Apply** when done.

---

## Step 4 — Create a Date Table (Recommended)

A separate date table enables time intelligence DAX functions
(e.g., month-over-month comparisons).

In Power BI, go to **Modeling → New Table** and paste:

```
DimDate =
ADDCOLUMNS(
    CALENDAR(DATE(2022, 1, 1), DATE(2025, 12, 31)),
    "Year",        YEAR([Date]),
    "Month",       MONTH([Date]),
    "MonthName",   FORMAT([Date], "MMMM"),
    "Quarter",     "Q" & FORMAT(QUARTER([Date]), "0"),
    "WeekDay",     WEEKDAY([Date], 2),
    "DayName",     FORMAT([Date], "dddd"),
    "IsWeekend",   IF(WEEKDAY([Date], 2) >= 6, TRUE, FALSE)
)
```

Then create a relationship:
- `DimDate[Date]` → `youtube_cleaned_data[publication_date]`
- Cardinality: Many-to-one
- Direction: Single (from fact to dimension)

---

## Step 5 — Data Model (Star Schema)

```
FactYouTubeEngagement (youtube_cleaned_data)
    │
    ├── DimDate          (on publication_date)
    ├── DimChannel       (on channel_title)  ← optional separate table
    ├── DimCategory      (on category_id)    ← optional
    └── DimPostingTime   (on posting_time_group) ← optional
```

For a beginner project, using the single flat CSV table is perfectly acceptable.

---

## Step 6 — Build Dashboard Pages

See `dashboard_wireframe.md` for the layout of each page.

### Page 1: Executive Overview
- Add **Card** visuals for: Total Views, Total Likes, Total Comments,
  Total Videos, Average Engagement Rate
- Add a **Line Chart**: X-axis = publication_month_name, Values = Total Views
- Add a **Bar Chart**: Y-axis = title (top 10 by view_count), X-axis = view_count
- Add **Slicers**: channel_title, publication_year, duration_category,
  performance_category

### Page 2: Engagement Analysis
- **Bar Chart**: channel_title vs. Average engagement_rate
- **Scatter Chart**: X = view_count, Y = like_count, Legend = performance_category
- **Bar Chart**: duration_category vs. Average engagement_rate
- **Donut Chart**: performance_category distribution

### Page 3: Posting-Time Analysis
- **Bar Chart**: publication_day_name vs. Average engagement_rate
- **Line Chart**: publication_hour vs. Average engagement_rate
- **Matrix (Heatmap)**: Rows = publication_day_name,
  Columns = posting_time_group, Values = Average engagement_rate
- **Card KPIs**: Best Day, Best Hour, Best Time Group

### Page 4: Content Strategy
- **Bar Chart**: duration_category vs. Average engagement_rate
- **Table**: High-view, low-engagement videos
  (filter: view_count above average AND engagement_rate below average)
- **Text boxes**: Key recommendations from business_insights.md

---

## Step 7 — Formatting Tips

- Set the **report theme**: View → Themes → choose a built-in dark or modern theme
- Use **consistent colours** per channel (apply colour to channel slicer)
- Add a **page title** text box to each page
- Add **tooltips** showing: view_count, like_count, engagement_rate, channel_title
- Enable **Cross-filter** between visuals for interactivity
- Sort bar charts by value (descending) for cleaner presentation

---

## Step 8 — Publish to Power BI Service (Optional)

1. Click **Home → Publish**
2. Sign in with your Microsoft/work account
3. Select workspace → click **Publish**
4. Access your report at https://app.powerbi.com

> ⚠️ The SQLite .db file must be replaced with a cloud database or CSV
> scheduled refresh for the published report to stay up to date.
