#!/usr/bin/env python3
"""Run the CLI scraper."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from webscraper.cli import main
if __name__ == "__main__":
    main()
