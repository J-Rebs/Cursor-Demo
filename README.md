# 10-K Risk Analysis Tool

A tool for analyzing risk factors from 10-K filings using AI. This tool processes PDF files of 10-K filings to extract, categorize, and analyze risk factors over time. This was made using Cursor. 

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your 10-K PDF files in the `data_to_use` directory.

2. Run the analysis:
```bash
python src/main.py --input data_to_use --output data
```

See [output.md](data/output.md) for what this application produces.

## Notes

This is primarily to demonstrate the capacity of Cursor to help generated a useful data processing application with some use of AI. It shows the speed and ease of using Cursor while also highlighting a few other learnings:
- Try to break the desired output into smaller logical parts Cursor can work with. 
- During development, it can be useful to produce interemediate outputs that are easier to check. 

It does not consider things like proper python packaging, testing, or extensibility beyond the sourced 10Ks. In a real world scenario, it may be useful to use SEC APIs to access 10k data. 

## License

MIT License 