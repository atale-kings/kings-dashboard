"""
Fetches GA4 data using the Google Analytics Data API.

You need your GA4 "Property ID" (a number, NOT the measurement ID like G-XXXX).
Find it in GA4: Admin -> Property details -> Property ID.
"""

import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest,
)


def _client(creds):
    return BetaAnalyticsDataClient(credentials=creds)


def _run_report(creds, property_id, dimensions, metrics, start_date, end_date, limit=10):
    client = _client(creds)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )
    response = client.run_report(request)

    rows = []
    for row in response.rows:
        record = {}
        for i, dim in enumerate(dimensions):
            record[dim] = row.dimension_values[i].value
        for i, met in enumerate(metrics):
            record[met] = row.metric_values[i].value
        rows.append(record)
    return pd.DataFrame(rows)


def get_summary(creds, property_id, start_date, end_date):
    """Top-line scorecard numbers: views, sessions, new user %, etc."""
    df = _run_report(
        creds, property_id,
        dimensions=[],
        metrics=["screenPageViews", "sessions", "newUserRate",
                 "active1DayUsers", "screenPageViewsPerUser", "averageSessionDuration"],
        start_date=start_date, end_date=end_date, limit=1,
    )
    if df.empty:
        return {}
    row = df.iloc[0]
    return {
        "Views": int(float(row["screenPageViews"])),
        "Sessions": int(float(row["sessions"])),
        "New User %": round(float(row["newUserRate"]) * 100, 1),
        "One-day active users": int(float(row["active1DayUsers"])),
        "Pageviews per User": round(float(row["screenPageViewsPerUser"]), 1),
        "Engagement Time (s)": round(float(row["averageSessionDuration"]), 1),
    }


def get_trend(creds, property_id, start_date, end_date):
    """Daily views for the trend line chart."""
    df = _run_report(
        creds, property_id,
        dimensions=["date"],
        metrics=["screenPageViews"],
        start_date=start_date, end_date=end_date, limit=1000,
    )
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df["screenPageViews"] = df["screenPageViews"].astype(int)
    return df.sort_values("date")


def get_device_category(creds, property_id, start_date, end_date):
    return _run_report(
        creds, property_id,
        dimensions=["deviceCategory"],
        metrics=["activeUsers"],
        start_date=start_date, end_date=end_date,
    )


def get_top_countries(creds, property_id, start_date, end_date):
    return _run_report(
        creds, property_id,
        dimensions=["country"],
        metrics=["activeUsers"],
        start_date=start_date, end_date=end_date, limit=8,
    )


def get_operating_system(creds, property_id, start_date, end_date):
    return _run_report(
        creds, property_id,
        dimensions=["operatingSystem"],
        metrics=["activeUsers"],
        start_date=start_date, end_date=end_date, limit=8,
    )


def get_browser(creds, property_id, start_date, end_date):
    return _run_report(
        creds, property_id,
        dimensions=["browser"],
        metrics=["activeUsers"],
        start_date=start_date, end_date=end_date, limit=8,
    )


def get_top_traffic_sources(creds, property_id, start_date, end_date):
    return _run_report(
        creds, property_id,
        dimensions=["sessionSource", "sessionMedium"],
        metrics=["sessions"],
        start_date=start_date, end_date=end_date, limit=10,
    )


def get_top_events(creds, property_id, start_date, end_date):
    return _run_report(
        creds, property_id,
        dimensions=["eventName"],
        metrics=["eventCount", "activeUsers"],
        start_date=start_date, end_date=end_date, limit=10,
    )


def get_landing_pages(creds, property_id, start_date, end_date):
    return _run_report(
        creds, property_id,
        dimensions=["landingPagePlusQueryString"],
        metrics=["sessions", "bounceRate"],
        start_date=start_date, end_date=end_date, limit=10,
    )


def get_top_pages(creds, property_id, start_date, end_date):
    return _run_report(
        creds, property_id,
        dimensions=["pagePath"],
        metrics=["screenPageViews", "activeUsers"],
        start_date=start_date, end_date=end_date, limit=10,
    )
