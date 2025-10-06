# chron
chronology and timeline creator

A lightweight Python tool for creating chronological timelines from event data.

## Quick Start

See [timeliner-lite.md](timeliner-lite.md) for detailed development setup and usage instructions.

### Installation

```bash
pip install -e .
```

### Basic Usage

```bash
# Create timeline from CSV
python -m chron.timeline --input examples/sample_events.csv --output timeline.html

# Create timeline from JSON
python -m chron.timeline --input examples/sample_events.json --output timeline.html
```

## Features

- Multiple input formats (CSV, JSON, YAML)
- HTML timeline generation
- Customizable themes and date ranges
- Easy-to-use CLI interface

## Documentation

For comprehensive documentation, development scripts, and API usage, see [timeliner-lite.md](timeliner-lite.md).

## License

MIT License
