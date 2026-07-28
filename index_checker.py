"""
Standalone script to check indexing status for a large list of URLs
(e.g. your ~3,000 reports) using the Search Console URL Inspection API.

WHY THIS IS SEPARATE FROM THE DASHBOARD:
Checking 3,000 URLs takes a long time (Google allows roughly 1-2 requests per
second per site), so this can't run every time you open the dashboard -- it
would take 30-50+ minutes and time out. Instead:

  1. Run this script whenever you want fresh indexing numbers
     (e.g. once a week): python index_checker.py
  2. It saves progress to indexing_status.csv as it goes, and can be safely
     stopped (Ctrl+C) and re-run later -- it skips URLs already checked
     within the last 7 days.
  3. The dashboard (app.py) reads indexing_status.csv and shows:
     Reports Published, Reports Indexed, Reports Not Indexed.

HOW TO USE:
  1. Put your list of URLs in urls.txt, one URL per line.
  2. Edit SITE_URL below to match your exact Search Console property.
  3. Run: python index_checker.py
"""

import csv
import os
import time
from datetime import datetime, timedelta

from googleapiclient.discovery import build
from auth import get_credentials

SITE_URL = "https://www.kingsresearch.com/"   # <-- change to your exact GSC property
URLS_FILE = "urls.txt"
OUTPUT_FILE = "indexing_status.csv"
RECHECK_AFTER_DAYS = 7
SECONDS_BETWEEN_REQUESTS = 1.0  # stay under Google's rate limit


def load_existing_results():
    results = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                results[row["url"]] = row
    return results


def save_results(results):
    fieldnames = ["url", "coverage_state", "verdict", "last_checked"]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results.values():
            writer.writerow(row)


def needs_check(row):
    if row is None:
        return True
    last_checked = datetime.fromisoformat(row["last_checked"])
    return datetime.now() - last_checked > timedelta(days=RECHECK_AFTER_DAYS)


def main():
    if not os.path.exists(URLS_FILE):
        print(f"Could not find {URLS_FILE}. Create it with one URL per line.")
        return

    with open(URLS_FILE, encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    creds = get_credentials()
    service = build("searchconsole", "v1", credentials=creds)

    results = load_existing_results()
    total = len(urls)

    for i, url in enumerate(urls, start=1):
        existing = results.get(url)
        if not needs_check(existing):
            continue

        try:
            response = service.urlInspection().index().inspect(
                body={"inspectionUrl": url, "siteUrl": SITE_URL}
            ).execute()
            index_result = response.get("inspectionResult", {}).get("indexStatusResult", {})
            coverage_state = index_result.get("coverageState", "Unknown")
            verdict = index_result.get("verdict", "Unknown")
        except Exception as e:
            coverage_state = f"ERROR: {e}"
            verdict = "ERROR"

        results[url] = {
            "url": url,
            "coverage_state": coverage_state,
            "verdict": verdict,
            "last_checked": datetime.now().isoformat(),
        }

        print(f"[{i}/{total}] {url} -> {coverage_state}")

        # Save progress every 25 URLs so a crash/stop doesn't lose everything
        if i % 25 == 0:
            save_results(results)

        time.sleep(SECONDS_BETWEEN_REQUESTS)

    save_results(results)
    print("Done. Results saved to", OUTPUT_FILE)


if __name__ == "__main__":
    main()
