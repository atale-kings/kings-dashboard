"""
Fetches Search Console data using the Search Console API (searchanalytics.query).

This is the piece that Looker Studio couldn't do correctly: here, we pull every
row ourselves, group by query in plain Python/pandas, and THEN compute the true
average position per keyword across the whole date range. That's why Top 3 /
Top 10 counts come out right here.
"""

import pandas as pd
from googleapiclient.discovery import build


def _service(creds):
    return build("searchconsole", "v1", credentials=creds)


def _query(creds, site_url, start_date, end_date, dimensions, row_limit=25000):
    service = _service(creds)
    all_rows = []
    start_row = 0
    while True:
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dimensions,
            "rowLimit": row_limit,
            "startRow": start_row,
        }
        response = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
        rows = response.get("rows", [])
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < row_limit:
            break
        start_row += row_limit

    records = []
    for r in all_rows:
        record = {}
        for i, dim in enumerate(dimensions):
            record[dim] = r["keys"][i]
        record["clicks"] = r.get("clicks", 0)
        record["impressions"] = r.get("impressions", 0)
        record["ctr"] = r.get("ctr", 0)
        record["position"] = r.get("position", 0)
        records.append(record)
    return pd.DataFrame(records)


def get_query_summary(creds, site_url, start_date, end_date):
    """
    Pulls per-query data across the whole date range, then computes the TRUE
    average position per keyword (weighted by impressions), and returns:
    avg_position, ranking_keywords, top3_count, top10_count, plus the full
    per-keyword table (useful for debugging).
    """
    df = _query(creds, site_url, start_date, end_date, dimensions=["query"])

    if df.empty:
        return {
            "avg_position": 0, "ranking_keywords": 0,
            "top3_count": 0, "top10_count": 0,
        }, df

    # Search Console already returns one row per query for this date range,
    # with 'position' already averaged across the range (weighted internally
    # by Google). No further grouping needed -- but we compute overall avg
    # position ourselves, weighted by impressions, for the top scorecard.
    total_impressions = df["impressions"].sum()
    if total_impressions > 0:
        avg_position = (df["position"] * df["impressions"]).sum() / total_impressions
    else:
        avg_position = df["position"].mean()

    top3_count = int((df["position"] <= 3).sum())
    top10_count = int((df["position"] <= 10).sum())

    summary = {
        "avg_position": round(avg_position, 2),
        "ranking_keywords": len(df),
        "top3_count": top3_count,
        "top10_count": top10_count,
    }
    return summary, df


def get_traffic_trend(creds, site_url, start_date, end_date):
    """Daily clicks + impressions for the trend line chart."""
    df = _query(creds, site_url, start_date, end_date, dimensions=["date"])
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date")


def get_top_pages(creds, site_url, start_date, end_date, limit=10):
    """Top performing reports/pages by clicks."""
    df = _query(creds, site_url, start_date, end_date, dimensions=["page"])
    if df.empty:
        return df
    return df.sort_values("clicks", ascending=False).head(limit)
