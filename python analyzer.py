name: Ituran_Excel_Analyzer
on:
  push:
    paths:
      - '**.csv' # ירוץ בכל פעם שתעלה קובץ אקסל/csv חדש
  workflow_dispatch:

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install pandas
      - name: Run Analysis
        run: python analyzer.py
      - name: Commit Results
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add fleet_detailed.json
          git commit -m "Update analysis from Excel" || echo "No changes"
          git push
