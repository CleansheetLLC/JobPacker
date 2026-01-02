# JobPacker

A beautiful, menu-driven CLI tool for harvesting job listings from multiple job boards. Exports to Cleansheet-compatible JSON format.

## Features

- Search multiple job boards: Indeed, LinkedIn, Glassdoor, ZipRecruiter, Google
- Interactive menu-driven interface with rich formatting
- Persistent configuration (remembers your preferences)
- Cross-platform: Windows, Mac, Linux
- Export directly to Cleansheet JSON format

## Installation

### Requirements

- **Python 3.12** (required - numpy/jobspy compatibility issues with 3.13+)

### Setup

```bash
# Clone the repository
git clone https://github.com/CleansheetLLC/JobPacker.git
cd JobPacker

# Create virtual environment with Python 3.12
# Windows:
py -3.12 -m venv venv
venv\Scripts\activate

# Mac/Linux:
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python jobpacker.py
```

The interactive menu will guide you through:

1. **Search** - Enter job title, location, and select job boards
2. **Settings** - Configure defaults (location, results per site, job boards)
3. **Export** - Save results to Cleansheet-compatible JSON
4. **Exit** - Quit the application

### Quick Start

1. Run `python jobpacker.py`
2. Select **[1] Search for Jobs**
3. Enter your search terms (or press Enter for defaults)
4. Review results in the table
5. Select **[3] Export Results** to save JSON

## Configuration

JobPacker saves your preferences to `config.json`:

- Default job title/keywords
- Default location
- Preferred job boards
- Results per site
- Remote-only filter
- Job type filter

Settings persist between sessions.

## Output Format

Exports JSON compatible with Cleansheet Job Opportunities import:

```json
{
  "exportType": "jobspy_harvest",
  "jobs": [
    {
      "id": "uuid",
      "company": "Company Name",
      "title": "Job Title",
      "location": "City, State",
      "url": "https://...",
      "description": "Job description...",
      "salary": "$100,000 - $120,000",
      "datePosted": "2025-01-02",
      "source": "indeed",
      "status": "Saved",
      "tags": []
    }
  ]
}
```

## Troubleshooting

### No results found

- Try broader search terms
- Try a larger location (e.g., "USA" instead of a specific city)
- Some job boards may have anti-bot measures; try Indeed alone

### Rate limiting

- Wait a few minutes between searches
- Reduce results per site
- Use fewer job boards simultaneously

### LinkedIn errors

- LinkedIn has strict anti-scraping measures
- Rate limits around 10 pages without proxies
- Use Indeed for most reliable results

### ZipRecruiter not returning results

- Only works for US/Canada locations
- Uses location parameter only (search terms may be ignored)
- Try "USA" or a specific US city

### Google Jobs not returning results

- Requires exact Google Jobs search syntax
- Very finicky with search terms
- Recommended: Use Indeed/LinkedIn instead

## Dependencies

- [python-jobspy](https://github.com/Bunsly/JobSpy) - Job board scraping
- [rich](https://github.com/Textualize/rich) - Beautiful terminal formatting

## License

MIT License - See LICENSE file for details.

## Related

- [Cleansheet](https://cleansheet.info) - Career development platform
