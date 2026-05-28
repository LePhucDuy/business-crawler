# Business Crawler

A robust, compliance-first business information crawler serving internal eKYB systems.

## Legal and Ethical Considerations
This system is designed with strict adherence to crawling ethics:
- Does **not** bypass captchas. Captcha challenges are escalated for manual review.
- Respects `robots.txt` rules.
- Implements strict rate limiting and retries.
- Performs on-demand lookups only. No bulk scraping, no brute-forcing.
- Maintains full audit logs of what was crawled, when, and from where.

## Features
- Extensible Plugin Architecture for new providers.
- Normalization and Data Quality scoring.
- Conflict detection and merging from multiple sources using `rapidfuzz`.
- REST API via FastAPI.
- Internal DB Caching to minimize redundant requests.

## Setup
1. Copy `.env.example` to `.env`.
2. Start the database: `make docker-up`
3. Generate and run migrations: 
   ```bash
   make install
   make revision name="init"
   make migrate
   ```
4. Run the app: `make dev`

## Adding a New Provider
1. Create a new folder in `app/crawlers/providers/`
2. Implement `BaseBusinessCrawler` and register it in `app/crawlers/providers/__init__.py`.

## Running the CLI
```bash
python -m app.cli.lookup --tax-code 0101234567
```
# business-crawler
