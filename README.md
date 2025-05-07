# Job Offer Comparison Tool

A comprehensive Python tool to help you compare multiple job offers based on a wide range of factors including compensation, benefits, taxes, and work-life considerations.

## Overview

Making career decisions can be complex, especially when comparing multiple job offers with different compensation structures, benefits packages, and employment types. This tool provides a structured approach to evaluate job offers by considering:

- Base salary and bonuses
- Benefits valuation (401k matching, healthcare, PTO, etc.)
- Tax implications for different employment types (W2, 1099, S-Corp)
- Work-life balance factors (commute time, work hours)
- Cost of living adjustments between locations

## Installation

### Requirements
- Python 3.6+
- Additional packages for spreadsheet support:
  - pandas
  - openpyxl

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/job-compare.git
cd job-compare

# Install dependencies for spreadsheet support
pip install pandas openpyxl
```

## Usage

The tool can be run from the command line with various options:

```bash
cd src/
python main.py [OPTIONS]
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--interactive` | Run in interactive mode to manually enter job offer details |
| `--load FILE` | Load previously saved job offers from a JSON file |
| `--save FILE` | Save entered job offers to a JSON file for future use |
| `--spreadsheet FILE` | Import job offers from a spreadsheet (CSV or Excel) |
| `--create-template FILE` | Create a template spreadsheet with all required fields |

### Interactive Mode

Run the tool in interactive mode to manually enter job offer details:

```bash
python main.py --interactive
```

The tool will guide you through entering all relevant information for each job offer. You'll need at least two job offers to generate a comparison.

### Using Spreadsheets

#### Creating a Template

Generate a template spreadsheet with all required fields:

```bash
python main.py --create-template job_offers_template.xlsx
```

#### Importing Job Offers

After filling in the template with your job offer details:

```bash
python main.py --spreadsheet path/to/your/job_offers.xlsx
```

### Combining Methods

You can combine multiple input methods:

```bash
# Load from a spreadsheet and add more offers interactively
python main.py --spreadsheet existing_offers.xlsx --interactive

# Load offers from JSON, add more interactively, and save the combined result
python main.py --load saved_offers.json --interactive --save updated_offers.json
```

## Example Usage Scenarios

### Basic Comparison
```bash
# Enter job offers interactively and see comparison results
python main.py --interactive
```

### Create and Use a Template
```bash
# First create a template
python main.py --create-template my_offers.xlsx

# Fill in the template with offer details, then run:
python main.py --spreadsheet my_offers.xlsx
```

### Save and Reuse Offers
```bash
# Enter offers and save them for later
python main.py --interactive --save my_offers.json

# Later, load the saved offers
python main.py --load my_offers.json
```

### Combine Multiple Sources
```bash
# Load offers from multiple sources
python main.py --load previous_offers.json --spreadsheet new_offers.xlsx --interactive
```

## Comparison Factors

The tool considers these factors when comparing job offers:

1. **Compensation**
   - Base salary/hourly rate
   - Signing bonuses
   - Performance bonuses
   - Equity/stock options

2. **Benefits**
   - Health insurance (medical, dental, vision)
   - Retirement benefits (401k/403b matching)
   - Paid time off (vacation, sick days, holidays)
   - Other perks (education stipends, gym memberships, etc.)

3. **Tax Considerations**
   - Employment type (W2, 1099, Corp-to-Corp)
   - Tax implications of different structures
   - Self-employment taxes for contractors

4. **Work-Life Balance**
   - Commute time and costs
   - Remote work options
   - Work schedule flexibility
   - Expected work hours

5. **Geographic Adjustments**
   - Cost of living differences
   - State tax variations

## Notes

- Tax calculations are estimates and should not be considered tax advice
- Benefit valuations are based on approximate market values
- For important financial decisions, consult with a financial advisor or tax professional

## Project Structure

```
job-compare/
├── README.md                # This documentation
├── src/                     # Source code
│   ├── benefits_calculator.py  # Benefits valuation logic
│   ├── commute_calculator.py   # Commute cost/time calculations
│   ├── comparison_engine.py    # Core comparison logic
│   ├── job_offer.py            # Job offer data model
│   ├── main.py                 # Entry point and CLI handling
│   ├── spreadsheet_parser.py   # Import/export functionality
│   ├── tax_calculator.py       # Tax estimation logic
│   └── ui_handler.py           # User interface
└── tests/                   # Test suite
    ├── test_job_comparison.py  # Unit tests
    └── data/                   # Test data files
        ├── test_job_offers.csv
        └── test_job_offers.xlsx
```