"""
Kings Research Weekly Report -- live dashboard.

Run with:  streamlit run app.py

First run will open a browser tab asking you to log in with Google and click
Allow -- that's normal, it's how the dashboard gets permission to read your
GA4 and Search Console data as you.
"""

import os
import csv
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from auth import get_credentials
import ga4_data
import gsc_data

st.set_page_config(page_title="Kings Research Weekly Report", layout="wide")

# ---------------------------------------------------------------------------
# SETTINGS -- edit these two values for your site
# ---------------------------------------------------------------------------
GA4_PROPERTY_ID = "REPLACE_WITH_YOUR_GA4_PROPERTY_ID"   # e.g. "123456789"
GSC_SITE_URL = "https://www.kingsresearch.com/"          # exact GSC property URL
INDEXING_FILE = "indexing_status.csv"
# ---------------------------------------------------------------------------

st.title("Kings Research Weekly Report")

col_a, col_b = st.columns(2)
with col_a:
    start = st.date_input("Start date", value=date.today() - timedelta(days=7))
with col_b:
    end = st.date_input("End date", value=date.today())

start_str = start.strftime("%Y-%m-%d")
end_str = end.strftime("%Y-%m-%d")

with st.spinner("Signing in to Google..."):
    creds = get_credentials()

# ===========================================================================
# GA4 SECTION
# ===========================================================================
st.header("Google Analytics 4 Report")

if GA4_PROPERTY_ID.startswith("REPLACE"):
    st.warning("Set GA4_PROPERTY_ID in app.py to your GA4 property ID to see this section.")
else:
    with st.spinner("Loading GA4 summary..."):
        summary = ga4_data.get_summary(creds, GA4_PROPERTY_ID, start_str, end_str)

    cols = st.columns(len(summary) or 1)
    for col, (label, value) in zip(cols, summary.items()):
        col.metric(label, value)

    with st.spinner("Loading trend..."):
        trend_df = ga4_data.get_trend(creds, GA4_PROPERTY_ID, start_str, end_str)
    if not trend_df.empty:
        fig = px.line(trend_df, x="date", y="screenPageViews", title="Trends (Views)")
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Device Category")
        df = ga4_data.get_device_category(creds, GA4_PROPERTY_ID, start_str, end_str)
        if not df.empty:
            st.plotly_chart(px.pie(df, names="deviceCategory", values="activeUsers"),
                             use_container_width=True)

        st.subheader("Operating System")
        df = ga4_data.get_operating_system(creds, GA4_PROPERTY_ID, start_str, end_str)
        if not df.empty:
            st.bar_chart(df.set_index("operatingSystem")["activeUsers"].astype(int))

    with c2:
        st.subheader("Top Countries")
        df = ga4_data.get_top_countries(creds, GA4_PROPERTY_ID, start_str, end_str)
        if not df.empty:
            st.bar_chart(df.set_index("country")["activeUsers"].astype(int))

        st.subheader("Browser")
        df = ga4_data.get_browser(creds, GA4_PROPERTY_ID, start_str, end_str)
        if not df.empty:
            st.bar_chart(df.set_index("browser")["activeUsers"].astype(int))

    st.subheader("Top Traffic Sources")
    st.dataframe(ga4_data.get_top_traffic_sources(creds, GA4_PROPERTY_ID, start_str, end_str),
                 use_container_width=True)

    st.subheader("Top Events")
    st.dataframe(ga4_data.get_top_events(creds, GA4_PROPERTY_ID, start_str, end_str),
                 use_container_width=True)

    st.subheader("Landing Pages")
    st.dataframe(ga4_data.get_landing_pages(creds, GA4_PROPERTY_ID, start_str, end_str),
                 use_container_width=True)

    st.subheader("Top Pages")
    st.dataframe(ga4_data.get_top_pages(creds, GA4_PROPERTY_ID, start_str, end_str),
                 use_container_width=True)

st.divider()

# ===========================================================================
# GSC SECTION
# ===========================================================================
st.header("Google Search Console Report")

with st.spinner("Loading Search Console data (this groups every keyword correctly)..."):
    gsc_summary, gsc_query_df = gsc_data.get_query_summary(creds, GSC_SITE_URL, start_str, end_str)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg Position", gsc_summary["avg_position"])
c2.metric("Ranking Keywords", gsc_summary["ranking_keywords"])
c3.metric("Top 3 Reports", gsc_summary["top3_count"])
c4.metric("Top 10 Reports", gsc_summary["top10_count"])

with st.spinner("Loading traffic trend..."):
    gsc_trend_df = gsc_data.get_traffic_trend(creds, GSC_SITE_URL, start_str, end_str)
if not gsc_trend_df.empty:
    fig = px.line(gsc_trend_df, x="date", y=["clicks", "impressions"],
                  title="Traffic Trend (Clicks & Impressions)")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Top Performing Reports")
top_pages_df = gsc_data.get_top_pages(creds, GSC_SITE_URL, start_str, end_str)
st.dataframe(top_pages_df, use_container_width=True)

st.divider()

# ===========================================================================
# INDEXING SECTION (reads from the file produced by index_checker.py)
# ===========================================================================
st.header("Indexing Status")

if os.path.exists(INDEXING_FILE):
    idx_df = pd.read_csv(INDEXING_FILE)
    total_published = len(idx_df)
    indexed = int((idx_df["coverage_state"].str.contains("Submitted and indexed", na=False)).sum())
    not_indexed = total_published - indexed

    c1, c2, c3 = st.columns(3)
    c1.metric("Reports Published", total_published)
    c2.metric("Reports Indexed", indexed)
    c3.metric("Reports Not Indexed", not_indexed)

    with st.expander("See full indexing breakdown"):
        st.dataframe(idx_df, use_container_width=True)
else:
    st.info(
        "No indexing data yet. Run `python index_checker.py` in this folder "
        "once (see README) to check indexing status for your reports. "
        "It writes results to indexing_status.csv, which this page reads automatically."
    )
