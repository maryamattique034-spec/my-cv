# My CVs

Two CVs from one small Python script. Edit the JSON, rebuild, print to PDF.

| File | CV |
|---|---|
| `data/django-developer.json` | Professional Python/Django developer CV |
| `data/general.json` | General CV for any job |

## Update
1. Edit the JSON file (add job, skill, project...).
2. `python build.py` (no packages needed, Python 3 only)
3. Open `dist/<name>.html` in Chrome, then Ctrl+P, Save as PDF, Paper A4, Margins None, untick Headers and footers.

## Tips
- `section_order` in each JSON controls section order. Remove a name from it to hide that section.
- Keep bullets short, use numbers (40%, 10,000+ users).