# Kings Research Weekly Report - Live Dashboard

A live version of your Looker Studio report, built in Python, that fixes the
Top 3 / Top 10 counting problem by computing them correctly in code.

## What you need before starting

- Python 3.9 or newer installed on your computer
- The OAuth "Desktop app" JSON file you downloaded from Google Cloud Console
- Your GA4 Property ID (a number). Find it in GA4: **Admin -> Property details -> Property ID**
- Your exact Search Console property URL (e.g. `https://www.kingsresearch.com/`)

## One-time setup

1. **Put your files in this folder:**
   - Rename your downloaded OAuth JSON file to `client_secret.json` and put it in this folder.

2. **Install the required packages.** Open a terminal in this folder and run:
   ```
   pip install -r requirements.txt
   ```

3. **Edit `app.py`:**
   - Find the line `GA4_PROPERTY_ID = "REPLACE_WITH_YOUR_GA4_PROPERTY_ID"`
     and replace it with your real GA4 property ID, e.g. `GA4_PROPERTY_ID = "123456789"`
   - Find the line `GSC_SITE_URL = "https://www.kingsresearch.com/"`
     and make sure it matches your site exactly as it appears in Search Console.

4. **Run the dashboard:**
   ```
   streamlit run app.py
   ```
   A browser tab will open. The first time, Google will ask you to log in and
   click "Allow" -- do that once. After that it remembers you.

   Since the app is in "Testing" mode, Google may show a warning screen
   ("Google hasn't verified this app"). This is expected and safe -- it's
   your own app. Click **Advanced -> Go to Kings Research Dashboard (unsafe)**
   to continue. This warning only appears because the app isn't published
   publicly; it's not actually unsafe.

## Checking indexing status (Reports Indexed / Not Indexed)

This part needs a separate one-time-per-week run because checking thousands
of URLs takes too long to do every time you open the dashboard.

1. Create a file called `urls.txt` in this folder, with one report URL per line, e.g.:
   ```
   https://www.kingsresearch.com/blog/report-1
   https://www.kingsresearch.com/blog/report-2
   ```
   (Export this list from your CMS, sitemap, or a crawl tool like Screaming Frog.)

2. Edit `index_checker.py` and set `SITE_URL` to your exact Search Console property.

3. Run:
   ```
   python index_checker.py
   ```
   This will take a while for ~3,000 URLs (roughly 1 URL per second). You can
   stop it anytime with Ctrl+C and re-run later -- it picks up where it left off.

4. Once it finishes, refresh the dashboard (`streamlit run app.py`) -- the
   "Indexing Status" section will now show real numbers automatically, read
   from `indexing_status.csv`.

## Files in this folder

| File                  | What it does                                             |
|-----------------------|-----------------------------------------------------------|
| `app.py`              | The dashboard itself (run this)                           |
| `auth.py`             | Handles Google login                                      |
| `ga4_data.py`         | Pulls GA4 metrics                                          |
| `gsc_data.py`         | Pulls Search Console metrics (correct Top 3/10 counting)   |
| `index_checker.py`    | One-time/weekly script to check indexing status in bulk    |
| `requirements.txt`    | List of Python packages needed                             |
| `client_secret.json`  | Your OAuth credentials (you add this - keep it private)    |
| `token.json`          | Auto-created after first login (keep it private)           |
| `urls.txt`            | Your list of report URLs (you create this)                 |
| `indexing_status.csv` | Auto-created by index_checker.py                            |

**Keep `client_secret.json` and `token.json` private** -- don't upload them to
GitHub or share them. They're the "keys" to your Google data.
