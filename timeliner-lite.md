# Timeliner-Lite Development Script

A lightweight chronology and timeline creator for visualizing events over time.

## Overview

Timeliner-Lite is a Python-based tool for creating chronological timelines from event data. It supports various input formats and generates visual timelines for analysis and presentation.

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/xdrabbit/chron.git
cd chron

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linter
flake8 src/

# Format code
black src/
```

## Usage

### Basic Timeline Creation

```bash
# Create a timeline from CSV file
python -m chron.timeline --input events.csv --output timeline.html

# Create a timeline from JSON file
python -m chron.timeline --input events.json --output timeline.png

# Interactive mode
python -m chron.timeline --interactive
```

### Input Format

#### CSV Format
```csv
date,event,description
2024-01-01,Project Start,Initial project kickoff
2024-02-15,Milestone 1,First major milestone
2024-03-30,Release,Version 1.0 release
```

#### JSON Format
```json
{
  "events": [
    {
      "date": "2024-01-01",
      "event": "Project Start",
      "description": "Initial project kickoff"
    },
    {
      "date": "2024-02-15",
      "event": "Milestone 1",
      "description": "First major milestone"
    }
  ]
}
```

## Features

- **Multiple Input Formats**: CSV, JSON, and YAML support
- **Visual Outputs**: HTML, PNG, SVG timeline generation
- **Customization**: Color schemes, date ranges, and styling options
- **Interactive Mode**: CLI interface for quick timeline creation
- **Export Options**: Multiple output formats for presentations

## Development Scripts

### Running the Application

```bash
# Development mode with auto-reload
python -m chron.timeline --dev

# Production mode
python -m chron.timeline --input data/events.csv --output output/timeline.html
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=chron --cov-report=html

# Run specific test file
pytest tests/test_timeline.py
```

### Building

```bash
# Build package
python -m build

# Install locally
pip install -e .

# Create distribution
python setup.py sdist bdist_wheel
```

## Project Structure

```
chron/
├── src/
│   └── chron/
│       ├── __init__.py
│       ├── timeline.py      # Main timeline logic
│       ├── parser.py        # Input parsing
│       └── renderer.py      # Output rendering
├── tests/
│   ├── __init__.py
│   ├── test_timeline.py
│   └── test_parser.py
├── examples/
│   ├── sample_events.csv
│   └── sample_events.json
├── requirements.txt
├── requirements-dev.txt
├── setup.py
└── README.md
```

## Configuration

Create a `.chronrc` file in your home directory or project root:

```yaml
default_output: html
color_scheme: blue
date_format: "%Y-%m-%d"
timezone: UTC
```

## API Usage

```python
from chron.timeline import Timeline
from chron.parser import EventParser

# Parse events
parser = EventParser()
events = parser.parse_csv('events.csv')

# Create timeline
timeline = Timeline(events)
timeline.set_range('2024-01-01', '2024-12-31')
timeline.set_theme('modern')

# Generate output
timeline.render('output.html')
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Development Workflow

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install in development mode
pip install -e .

# 3. Run tests
pytest

# 4. Make changes and test
# ... edit files ...
pytest

# 5. Format and lint
black src/
flake8 src/

# 6. Commit changes
git add .
git commit -m "Description of changes"
git push
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure you've activated the virtual environment
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Test failures**: Check Python version compatibility (3.8+)

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/xdrabbit/chron/issues
- Documentation: https://github.com/xdrabbit/chron/wiki
