#!/usr/bin/env bash
# Run the visa_scraper and update the bulletin cache
mkdir -p site/bulletins
python3 visa_scraper.py --start-month 12 --start-year 2001 --end-month $(date +%m) --end-year $(date +%Y) --output site/bulletins/ 