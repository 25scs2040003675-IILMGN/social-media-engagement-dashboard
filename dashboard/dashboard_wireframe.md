# Dashboard Wireframe
## Social Media Engagement Analytics Dashboard

Text-based wireframes for all four Power BI dashboard pages.
Use these as a layout reference when building in Power BI Desktop.

---

## Page 1 — Executive Overview

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║  📊 SOCIAL MEDIA ENGAGEMENT ANALYTICS DASHBOARD         [Channel ▼] [Year ▼]  ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                  ║
║  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ ║
║  │ TOTAL    │  │ TOTAL    │  │ TOTAL    │  │ TOTAL    │  │ AVG ENGAGEMENT   │ ║
║  │ VIEWS    │  │ LIKES    │  │ COMMENTS │  │ VIDEOS   │  │     RATE         │ ║
║  │ 12.5M    │  │ 620K     │  │ 63K      │  │ 200      │  │      3.42%       │ ║
║  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ ║
║                                                                                  ║
║  ┌────────────────────────────────────────┐  ┌─────────────────────────────┐   ║
║  │ MONTHLY VIEWS TREND (Line Chart)       │  │ TOP 10 VIDEOS BY VIEWS     │   ║
║  │                                        │  │ (Horizontal Bar Chart)      │   ║
║  │    ▁▃▅▇█▇▅▃▂▁▂▃▄▅▆▇█▇▆▅▄             │  │                             │   ║
║  │  Jan Feb Mar Apr May Jun ...           │  │ Video Title A  ████████ 2M │   ║
║  │                                        │  │ Video Title B  ██████ 1.5M │   ║
║  └────────────────────────────────────────┘  │ Video Title C  █████ 1.2M  │   ║
║                                              │ ...                         │   ║
║  ┌────────────────────────────────────────┐  └─────────────────────────────┘   ║
║  │ CHANNEL PERFORMANCE (Bar Chart)        │                                     ║
║  │                                        │  ┌─────────────────────────────┐   ║
║  │  TechInsights  ████████████ 4.5M       │  │ SLICERS                     │   ║
║  │  DataDriven    ████████ 2.8M           │  │ ■ Category  [All ▼]         │   ║
║  │  CodeMaster    ██████ 2.1M             │  │ ■ Duration  [All ▼]         │   ║
║  │  ...                                   │  │ ■ Perf Cat  [All ▼]         │   ║
║  └────────────────────────────────────────┘  └─────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

### Visual specifications

| Visual | Type | Axis/Field | Values | Sort | Tooltip |
|--------|------|-----------|--------|------|---------|
| Total Views | Card | — | Total Views | — | — |
| Total Likes | Card | — | Total Likes | — | — |
| Total Comments | Card | — | Total Comments | — | — |
| Total Videos | Card | — | Total Videos | — | — |
| Avg Engagement Rate | Card | — | Average Engagement Rate | — | — |
| Monthly Views Trend | Line Chart | X: publication_month_name | Y: Total Views | Month asc | channel_title |
| Top 10 by Views | Bar Chart | Y: title (top 10 filter) | X: Total Views | Desc | engagement_rate |
| Channel Performance | Bar Chart | Y: channel_title | X: Total Views | Desc | video_count |

---

## Page 2 — Engagement Analysis

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║  💡 ENGAGEMENT ANALYSIS                                 [Channel ▼] [Year ▼]  ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                  ║
║  ┌─────────────────────────────────────┐  ┌──────────────────────────────────┐ ║
║  │ TOP VIDEOS BY ENGAGEMENT RATE       │  │ VIEWS vs LIKES (Scatter)         │ ║
║  │ (Bar Chart — min 1000 views filter) │  │                                  │ ║
║  │                                     │  │  Likes         ●●               │ ║
║  │  Video A ████████████ 8.2%          │  │    ●●●  ●                        │ ║
║  │  Video B ███████████ 7.8%           │  │      ●●   ●                      │ ║
║  │  Video C ████████ 6.1%              │  │                      Views       │ ║
║  └─────────────────────────────────────┘  └──────────────────────────────────┘ ║
║                                                                                  ║
║  ┌─────────────────────────────────────┐  ┌──────────────────────────────────┐ ║
║  │ ENGAGEMENT BY CHANNEL               │  │ VIEWS vs COMMENTS (Scatter)      │ ║
║  │ (Bar Chart — sorted desc)           │  │                                  │ ║
║  │                                     │  │  Comments   ●●                   │ ║
║  │  Channel A ██████████ 4.8%          │  │       ●●  ●   ●                  │ ║
║  │  Channel B █████████ 4.1%           │  │                      Views       │ ║
║  └─────────────────────────────────────┘  └──────────────────────────────────┘ ║
║                                                                                  ║
║  ┌─────────────────────────────────────┐  ┌──────────────────────────────────┐ ║
║  │ ENGAGEMENT BY DURATION CATEGORY     │  │ PERFORMANCE CATEGORY BREAKDOWN   │ ║
║  │ (Bar Chart)                         │  │ (Donut Chart)                    │ ║
║  │                                     │  │                                  │ ║
║  │  Medium   ████████████ 4.2%         │  │      ╭──────╮                    │ ║
║  │  Short    ████████ 3.8%             │  │    ╭─┤  Avg ├─╮                  │ ║
║  │  Long     ██████ 2.9%               │  │    │ ╰──────╯ │                  │ ║
║  └─────────────────────────────────────┘  └──────────────────────────────────┘ ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

### Visual specifications

| Visual | Type | Axis | Values | Filter |
|--------|------|------|--------|--------|
| Top by Engagement | Bar | Y: title | X: Avg Engagement Rate | view_count >= 1000 |
| Views vs Likes | Scatter | X: view_count, Y: like_count | Legend: performance_category | — |
| Views vs Comments | Scatter | X: view_count, Y: comment_count | Legend: performance_category | — |
| Engagement by Channel | Bar | Y: channel_title | X: Avg Engagement Rate | Sort desc |
| Engagement by Duration | Bar | Y: duration_category | X: Avg Engagement Rate | — |
| Performance Breakdown | Donut | Legend: performance_category | Values: Total Videos | — |

---

## Page 3 — Posting-Time Analysis

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║  ⏰ POSTING-TIME ANALYSIS           [Channel ▼] [Year ▼] [Duration Cat ▼]    ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                  ║
║  ┌────────────────┐  ┌────────────────┐  ┌─────────────────────────────────┐  ║
║  │ BEST DAY KPI   │  │ BEST HOUR KPI  │  │ BEST TIME GROUP KPI             │  ║
║  │   Wednesday    │  │   18:00 IST    │  │       Evening                   │  ║
║  │   Eng: 4.8%    │  │   Eng: 5.1%    │  │       Eng: 4.9%                 │  ║
║  └────────────────┘  └────────────────┘  └─────────────────────────────────┘  ║
║                                                                                  ║
║  ┌──────────────────────────────────────┐  ┌───────────────────────────────┐  ║
║  │ ENGAGEMENT BY PUBLICATION DAY        │  │ ENGAGEMENT BY HOUR (0–23)     │  ║
║  │ (Bar Chart)                          │  │ (Line Chart)                  │  ║
║  │                                      │  │                               │  ║
║  │  Monday     ████████ 3.9%            │  │  5% ╮                   ╭─╮   │  ║
║  │  Tuesday    █████████ 4.1%           │  │     │  ╭──╮        ╭────╯ │   │  ║
║  │  Wednesday  ████████████ 4.8%        │  │  3% ╯──╯  ╰────────╯     ╰   │  ║
║  │  Thursday   ████████ 3.7%            │  │   0  6  12  18  23  Hour     │  ║
║  │  Friday     ██████████ 4.5%          │  └───────────────────────────────┘  ║
║  │  Saturday   ███████ 3.2%             │                                     ║
║  │  Sunday     ██████ 2.9%              │  ┌───────────────────────────────┐  ║
║  └──────────────────────────────────────┘  │ POSTS BY TIME GROUP (Bar)     │  ║
║                                            │                               │  ║
║  ┌──────────────────────────────────────┐  │  Morning   ████████ 45        │  ║
║  │ DAY × HOUR HEATMAP (Matrix)          │  │  Evening   ██████ 38          │  ║
║  │                                      │  │  Afternoon █████ 32           │  ║
║  │ Day\Hour  |06|12|18|                 │  │  Night     ███ 22             │  ║
║  │ Monday    |░░|▓▓|██|                 │  │  Late Night█ 8               │  ║
║  │ Wednesday |░░|██|██|                 │  └───────────────────────────────┘  ║
║  └──────────────────────────────────────┘                                     ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

### Visual specifications

| Visual | Type | Rows/Axis | Columns/Values | Notes |
|--------|------|-----------|----------------|-------|
| Best Day KPI | Card | — | Best Posting Day | DAX measure |
| Best Hour KPI | Card | — | Best Posting Hour | DAX measure |
| Best Group KPI | Card | — | Best Time Group | DAX measure |
| Engagement by Day | Bar | Y: publication_day_name | X: Avg Engagement Rate | Sort by value desc |
| Engagement by Hour | Line | X: publication_hour | Y: Avg Engagement Rate | Sort hour asc |
| Day×Hour Heatmap | Matrix | Rows: day_name, Cols: publication_hour | Avg Engagement Rate | Conditional formatting |
| Posts by Group | Bar | Y: posting_time_group | X: Total Videos | Sort desc |

---

## Page 4 — Content Strategy

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║  🎯 CONTENT STRATEGY                                    [Channel ▼] [Year ▼]  ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                  ║
║  ┌────────────────────────────────────┐  ┌─────────────────────────────────┐   ║
║  │ PERFORMANCE BY CATEGORY (Bar)      │  │ DURATION PERFORMANCE (Bar)      │   ║
║  │                                    │  │                                 │   ║
║  │  Education   ████████████ 5.2%     │  │  Medium   ████████████ 4.2%     │   ║
║  │  Science     ██████████ 4.8%       │  │  Short    ████████ 3.8%         │   ║
║  │  Tech        █████████ 4.1%        │  │  Long     ██████ 2.9%           │   ║
║  └────────────────────────────────────┘  └─────────────────────────────────┘   ║
║                                                                                  ║
║  ┌────────────────────────────────────┐  ┌─────────────────────────────────┐   ║
║  │ HIGH VIEWS, LOW ENGAGEMENT (Table) │  │ LOW VIEWS, HIGH ENGAGEMENT     │   ║
║  │ (CTA Improvement Opportunities)    │  │ (Hidden Gems — Table)           │   ║
║  │                                    │  │                                 │   ║
║  │ Title | Views | Eng Rate           │  │ Title | Views | Eng Rate        │   ║
║  │ ───── | ───── | ────────           │  │ ───── | ───── | ────────        │   ║
║  │ ...   | 2.1M  | 0.8%              │  │ ...   | 45K   | 9.2%            │   ║
║  │ ...   | 1.8M  | 0.6%              │  │ ...   | 38K   | 8.7%            │   ║
║  └────────────────────────────────────┘  └─────────────────────────────────┘   ║
║                                                                                  ║
║  ┌─────────────────────────────────────────────────────────────────────────┐   ║
║  │ KEY RECOMMENDATIONS (Text Box — populate from business_insights.md)     │   ║
║  │                                                                         │   ║
║  │ ✅ Post on [Best Day] at [Best Hour] for highest engagement             │   ║
║  │ ✅ Focus on [Best Duration] videos — highest median engagement          │   ║
║  │ ✅ [Best Category] content drives the most interaction                  │   ║
║  │ ⚠️  [N] high-view videos have low engagement — add stronger CTAs        │   ║
║  │ 💡 Hidden gems: promote low-view, high-engagement content               │   ║
║  └─────────────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

### Visual specifications

| Visual | Type | Axis | Values | Filter |
|--------|------|------|--------|--------|
| Category Performance | Bar | Y: category_id | X: Avg Engagement Rate | Sort desc |
| Duration Performance | Bar | Y: duration_category | X: Avg Engagement Rate | Sort desc |
| High View Low Engagement | Table | title, channel_title, view_count, engagement_rate | view_count > avg AND engagement_rate < avg | Top 15 |
| Hidden Gems | Table | title, channel_title, view_count, engagement_rate | view_count < avg AND engagement_rate > avg | Top 15 |
| Recommendations | Text Box | — | Static text from insights report | — |

---

## Colour Palette Recommendations

| Purpose | Hex | Description |
|---------|-----|-------------|
| Primary | #2E86AB | Professional blue — headers, main KPIs |
| Accent | #F6AE2D | Warm amber — highlights, best values |
| Positive | #4CAF50 | Green — high/viral performance |
| Warning | #FF6B35 | Orange — low engagement / caution |
| Neutral | #8E9AAF | Grey — secondary text |
| Background | #1A1A2E | Dark navy — modern dark theme |
| Card BG | #16213E | Slightly lighter dark |
| Text | #EAEAEA | Near-white — readable on dark bg |

> Ensure colour contrast meets WCAG AA standard (4.5:1 for normal text).
> Use Power BI's built-in accessibility checker under View → Check accessibility.
