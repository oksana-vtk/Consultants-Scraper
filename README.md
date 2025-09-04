## Consultant Scraper - Dynamic web scraping using Selenium for paginated data
This project demonstrates how to dynamically scrape listing data from a paginated directory 
using Selenium, with filters, scroll interaction, and contact detail extraction 
from profile pages.

### Project Execution Steps
This project automates the extraction of consultant listings and their details from a website using Selenium, BeautifulSoup, and pandas.
It consists of two main scripts that run sequentially:

- `show_more.py` – collects all consultant names and profile links for selected countries.
- `consultants_details.py` – visits each profile and scrapes additional details such as About, Headquarters, Website, Email, and Phone.

The output is a clean dataset of consultants with structured information.

### 1. Run `show_more.py` - Scraping listings for Country_1
A Python script was developed to select certain country *Country_1* in the Country Location filter and 
perform dynamic, paginated scraping of listing cards. 
It automatically loads additional results by interacting with the **“Show more”** button. 

For each card, it collects: 
- ✅ Name
- ✅ Link to the listings’s profile
- ✅ Country (based on the selected filter)

Total listings found under Country_1: 2,016
Data saved: listings_country_1.csv   (separator: *)

### 2. Run `show_more.py` - Scraping listings for Country_2
A Python script was developed to select *Country_2* in the Country Location filter and perform dynamic, 
paginated scraping of listing cards. 
It automatically loads additional results by interacting with the **“Show more”** button. 

For each card, it collects: 

- ✅ Name
- ✅ Link to the listing’s profile
- ✅ Country (based on the selected filter)

Total listings found under Country_2: 762
Data saved to: listings_country_2.csv (separator: *)

### 3. Data Cleaning & Deduplication
Using Power Query, both datasets were analyzed and merged by matching listings profile Links 
to remove duplicates (some consultants appear in multiple countries).

- Country_1, but not Country_2 listings: 1,410
- Both Country_1 and Country_2 listings: 606
- Country_2, but not Country_1 listings: 156

Total unique Links across both countries: 2,172
Data saved to: listings_both_countries.csv (separator: *)

The merged dataset contains the following columns:
- ✅ Name
- ✅ Link to the listing’s profile
- ✅ Country_1 (listed under Country_1 filter)
- ✅ Country_2 (listed under Country_2 filter)
- ✅ Index (for internal merging and reference purposes)

### 4. Run consultants_details.py - Collecting consultant's details

Using the list of internal Links to the listing’s profile, a second Python script 
was developed to visit every profile page and extract the available details 
(HQ, Website, email, phone if listed).

**Total unique internal Links for scraping: 2,172**

The final output includes 2,172 rows with the following fields:
- ✅ Name
- ✅ Link to the listing’s profile
- ✅ Country_1 (listed under the Country_1 filter)
- ✅ Country_2 (listed under the Country_2 filter)
- ✅ Index (for internal merging and reference purposes)
- ✅ About (Short Name) (Short listing’s Name from section “About”)
- ✅ Headquarters (if listed) 
- ✅ Website (if listed)
- ✅ Email (if listed)
- ✅ Phone number (if listed)

Final dataset  saved to: listings_both_countries_details.csv (separator: *)

### Features

- Headless browsing with Selenium (Chrome).
- Support for multiple countries (configured via .env).
- Continuous "Show More" scrolling and clicking to load all results.
- Logging to both console and file (per country).
- Backup saves to prevent data loss during scraping.
- Auto-restart of browser sessions to avoid memory issues.
- CSV export with UTF-8 encoding and * delimiter for compatibility.
- Deduplication of multi-country results in Power Query.

### ⚙️ Technologies Used

- Python
- Selenium (with headless Chrome)
- BeautifulSoup
- pandas
- .env configuration
- Power Query (for merging and deduplication)

### Notes

- Run scripts sequentially: first show_more.py, then consultants_details.py.
- Logs are saved to .log files specified in .env.
- ChromeDriver must match your local Chrome version. Place it in your PATH.
- To avoid blocking, random delays are added between requests.
- For more countries, extend .env and duplicate function calls in show_more.py.
