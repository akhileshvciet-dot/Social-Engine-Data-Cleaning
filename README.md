# DataVortex — Social Engine Data Cleaning & EDA

**Team:** TEAM NEXUS | **Team ID:** 10698
**Event:** DataVortex Hackathon — Round 1

Clean and explore the *Social Engine* posts/users dataset, and prepare analysis-ready
outputs for downstream modeling.

## Deliverables in this repo

| File | Description |
|---|---|
| `data_cleaning_eda.ipynb` | Jupyter notebook: full cleaning pipeline + EDA with visualizations |
| `clean_data.py` | Standalone script that reproduces the cleaned CSVs |
| `eda_report.py` | Generates the `EDA_Report.pdf` (charts + summary tables) |

> The cleaned datasets (`Social_Engine_Posts_Cleaned.csv`, `Social_Engine_Users_Cleaned.csv`)
> and `EDA_Report.pdf` are submitted as separate deliverable files.

## Cleaning rules

| Issue | Treatment |
|---|---|
| `NULL` / empty `platform` | Replaced with `Unknown` |
| `NULL` / empty `text_content` | Replaced with `[No text]` placeholder |
| Missing `likes` | Imputed with dataset median (2500) |
| Negative like counts | Converted to absolute value |
| Mixed timestamp formats | Normalized to ISO 8601 (`YYYY-MM-DDTHH:MM:SS`) |
| HTML entities / tags (`&amp;`, `<div>`, `<br>`) | Decoded / stripped |
| Encoding artifacts (`Ã©`) | Corrected to unicode (`é`) |
| Multi-line quoted records | Merged into single logical rows |

## How to run

```bash
pip install pandas matplotlib seaborn numpy reportlab nbformat

# Reproduce the cleaned datasets
python clean_data.py

# Regenerate the EDA report
python eda_report.py

# Or explore interactively
jupyter notebook data_cleaning_eda.ipynb
```

## Results snapshot

- **Posts:** 12,360 rows — no missing values after cleaning
- **Users:** 1,500 rows
- Average engagement per post: ~2,494 likes, ~1,006 shares, ~504 comments
- Most active platform: `YouTube`
- Top hashtag: `#Reviews`