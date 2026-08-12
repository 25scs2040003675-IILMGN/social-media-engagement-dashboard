# DAX Measures Reference
## Social Media Engagement Analytics Dashboard

All measures assume the main table is named **youtube_cleaned_data**.
Adjust the table name if you renamed it in Power BI.

> **Division-by-zero protection:** All division uses the DAX `DIVIDE()` function.
> `DIVIDE(numerator, denominator, 0)` returns 0 (not an error) when
> the denominator is 0 or blank.

---

## Basic Count Measures

```dax
Total Videos =
COUNTROWS(youtube_cleaned_data)
```

```dax
Total Views =
SUM(youtube_cleaned_data[view_count])
```

```dax
Total Likes =
SUM(youtube_cleaned_data[like_count])
```

```dax
Total Comments =
SUM(youtube_cleaned_data[comment_count])
```

```dax
Total Interactions =
SUM(youtube_cleaned_data[total_interactions])
```

---

## Average Measures

```dax
Average Views =
AVERAGE(youtube_cleaned_data[view_count])
```

```dax
Average Likes =
AVERAGE(youtube_cleaned_data[like_count])
```

```dax
Average Comments =
AVERAGE(youtube_cleaned_data[comment_count])
```

```dax
Average Engagement Rate =
AVERAGE(youtube_cleaned_data[engagement_rate])
```

```dax
Median Engagement Rate =
MEDIAN(youtube_cleaned_data[engagement_rate])
```

---

## Rate Measures

```dax
Like Rate =
DIVIDE(
    SUM(youtube_cleaned_data[like_count]),
    SUM(youtube_cleaned_data[view_count]),
    0
) * 100
```

```dax
Comment Rate =
DIVIDE(
    SUM(youtube_cleaned_data[comment_count]),
    SUM(youtube_cleaned_data[view_count]),
    0
) * 100
```

```dax
Views per Video =
DIVIDE(
    SUM(youtube_cleaned_data[view_count]),
    COUNTROWS(youtube_cleaned_data),
    0
)
```

```dax
Engagement per Video =
DIVIDE(
    SUM(youtube_cleaned_data[total_interactions]),
    COUNTROWS(youtube_cleaned_data),
    0
)
```

---

## Top Performer Measures

```dax
Highest Viewed Video =
CALCULATE(
    MAX(youtube_cleaned_data[title]),
    TOPN(
        1,
        youtube_cleaned_data,
        youtube_cleaned_data[view_count],
        DESC
    )
)
```

```dax
Best Performing Channel =
CALCULATE(
    FIRSTNONBLANK(youtube_cleaned_data[channel_title], 1),
    TOPN(
        1,
        SUMMARIZE(
            youtube_cleaned_data,
            youtube_cleaned_data[channel_title],
            "AvgEng", AVERAGE(youtube_cleaned_data[engagement_rate])
        ),
        [AvgEng],
        DESC
    )
)
```

```dax
Best Posting Day =
CALCULATE(
    FIRSTNONBLANK(youtube_cleaned_data[publication_day_name], 1),
    TOPN(
        1,
        SUMMARIZE(
            youtube_cleaned_data,
            youtube_cleaned_data[publication_day_name],
            "MedianEng", MEDIAN(youtube_cleaned_data[engagement_rate])
        ),
        [MedianEng],
        DESC
    )
)
```

```dax
Best Posting Hour =
CALCULATE(
    FIRSTNONBLANK(youtube_cleaned_data[publication_hour], 1),
    TOPN(
        1,
        SUMMARIZE(
            youtube_cleaned_data,
            youtube_cleaned_data[publication_hour],
            "MedianEng", MEDIAN(youtube_cleaned_data[engagement_rate])
        ),
        [MedianEng],
        DESC
    )
)
```

---

## Time Intelligence Measures

> These measures require a DimDate table connected to publication_date.
> If you have not created DimDate, use the simpler alternatives below.

```dax
Previous Month Views =
CALCULATE(
    [Total Views],
    PREVIOUSMONTH(DimDate[Date])
)
```

```dax
Month-over-Month Views Growth =
VAR CurrentViews  = [Total Views]
VAR PreviousViews = [Previous Month Views]
RETURN
DIVIDE(CurrentViews - PreviousViews, PreviousViews, 0) * 100
```

```dax
Previous Month Engagement =
CALCULATE(
    [Average Engagement Rate],
    PREVIOUSMONTH(DimDate[Date])
)
```

```dax
Month-over-Month Engagement Growth =
VAR CurrentEng  = [Average Engagement Rate]
VAR PreviousEng = [Previous Month Engagement]
RETURN
DIVIDE(CurrentEng - PreviousEng, PreviousEng, 0) * 100
```

**Alternative (without DimDate) — use publication_year + publication_month filters:**
```dax
Previous Month Views (No DimDate) =
CALCULATE(
    [Total Views],
    DATEADD(youtube_cleaned_data[published_at], -1, MONTH)
)
```

---

## Ranking Measures

```dax
Rank by Views =
RANKX(
    ALL(youtube_cleaned_data[title]),
    [Total Views],
    ,
    DESC,
    DENSE
)
```

```dax
Rank by Engagement =
RANKX(
    ALL(youtube_cleaned_data[title]),
    [Average Engagement Rate],
    ,
    DESC,
    DENSE
)
```

```dax
Percentage of Total Views =
DIVIDE(
    SUM(youtube_cleaned_data[view_count]),
    CALCULATE(SUM(youtube_cleaned_data[view_count]), ALL(youtube_cleaned_data)),
    0
) * 100
```

---

## Classification Measures

```dax
High Engagement Video Count =
CALCULATE(
    COUNTROWS(youtube_cleaned_data),
    youtube_cleaned_data[performance_category] = "High"
)
```

```dax
Viral Video Count =
CALCULATE(
    COUNTROWS(youtube_cleaned_data),
    youtube_cleaned_data[performance_category] = "Viral"
)
```

```dax
Low Engagement Video Count =
CALCULATE(
    COUNTROWS(youtube_cleaned_data),
    youtube_cleaned_data[performance_category] = "Low"
)
```

---

## How to Create a Measure in Power BI

1. In the **Fields** pane, right-click the table name
2. Click **New Measure**
3. Type or paste the DAX formula
4. Press **Enter** or click the checkmark
5. Format the measure: In the **Measure tools** ribbon, set:
   - **Format**: Decimal Number or Percentage
   - **Decimal places**: 2
