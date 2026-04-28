#  Dynamic Web Scraper — Jobs / Products / News

A Python-based web scraping tool with both a **CLI** and **Tkinter GUI** interface. Extracts real-time data from multiple websites across three categories: **Jobs**, **Products**, and **News**.

---

##  Project Structure

```
dynamic-web-scraper/
├── webscraper/
│   ├── __init__.py
│   ├── cli.py              # CLI menu interface
│   ├── gui.py              # Tkinter GUI application
│   ├── storage.py          # JSON / CSV / Excel export
│   └── scrapers/
│       ├── __init__.py
│       ├── base.py         # Shared utilities (headers, retry, fetch)
│       ├── jobs.py         # Jobs: RemoteOK + Jobicy
│       ├── products.py     # Products: Books to Scrape + FakeStore
│       └── news.py         # News: HackerNews + Dev.to
├── data/                   # Saved scraped data (auto-created)
├── run_cli.py              # Launch CLI
├── run_gui.py              # Launch GUI
├── requirements.txt
└── README.md
```

---

##  Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/dynamic-web-scraper.git
cd dynamic-web-scraper
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

##  How to Run

### CLI Mode
```bash
python run_cli.py
```
Follow the interactive menu to select category, scrape, search, and save.

### GUI Mode
```bash
python run_gui.py
```
A dark-themed Tkinter window will open with:
- Category selector (Jobs / Products / News)
- Page count slider
- Real-time scraping progress bar
- Searchable / filterable results table
- One-click save to JSON / CSV / Excel

---

##  Websites Used

| Category | Source | Type | URL |
|----------|--------|------|-----|
| Jobs | RemoteOK | JSON API | https://remoteok.com/api |
| Jobs | Jobicy | JSON API | https://jobicy.com/api/v2/remote-jobs |
| Products | Books to Scrape | HTML (BeautifulSoup) | https://books.toscrape.com |
| Products | FakeStore | JSON API | https://fakestoreapi.com/products |
| News | HackerNews (Algolia) | JSON API | https://hn.algolia.com/api/v1/search |
| News | Dev.to | JSON API | https://dev.to/api/articles |

---

##  Features

###  Core Features
- Multi-source scraping (Jobs, Products, News)
- Keyword search and in-memory filtering
- Export to **JSON**, **CSV**, and **Excel** (.xlsx)
- Polite scraping with random User-Agent rotation
- Retry logic with exponential backoff
- Pagination support (configurable max pages)
- Clean text extraction and normalisation

### 🔹 CLI Features
- Interactive numbered menu
- Category selection with scraping options
- Search/filter with option to replace results
- Timestamped file output

###  GUI Features
- Dark-themed Tkinter interface
- Live progress bar during scraping
- Scrollable results table with zebra striping
- Stats panel (total, filtered, sources, last run)
- Log panel showing scraping activity
- Format selector for export

---

##  Data Fields

**Jobs:** title, company, location, tags, apply_link, date, source

**Products:** name, price, rating, category, product_link, source

**News:** title, description, source, published_date, url, author

---

##  Error Handling

- HTTP errors (4xx, 5xx) with automatic retry
- Connection timeouts (15s) with backoff
- Missing fields handled with `"N/A"` fallback
- Graceful degradation: if one source fails, others continue

---

##  Requirements

```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=5.1.0
openpyxl>=3.1.2
```

Python 3.9+ required.

---

##  Sample Output

Sample data files are included in the `data/` directory:
- `jobs_TIMESTAMP.json` / `.csv`
- `products_TIMESTAMP.json` / `.csv`  
- `news_TIMESTAMP.json` / `.csv`

---

##  Ethical Scraping

- Randomised User-Agent headers on every request
- Polite delays between requests (1.5s + random jitter)
- Targets only public APIs and openly-scrapable sites
- Robots.txt respected by targeting API endpoints where available

---

##  License

MIT License — free to use, modify, and distribute.

## Developed By 

Muhammad Junaid
