#!/usr/bin/env python3
"""Parser module for reading event data from various formats."""

import csv
import json
from typing import List, Dict


class EventParser:
    """Parser for event data in various formats."""

    def parse_csv(self, filepath: str) -> List[Dict]:
        """Parse events from CSV file.

        Args:
            filepath: Path to CSV file

        Returns:
            List of event dictionaries
        """
        events = []
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                events.append(
                    {
                        "date": row.get("date", ""),
                        "event": row.get("event", ""),
                        "description": row.get("description", ""),
                    }
                )
        return events

    def parse_json(self, filepath: str) -> List[Dict]:
        """Parse events from JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            List of event dictionaries
        """
        with open(filepath, "r") as f:
            data = json.load(f)
            return data.get("events", [])

    def parse_yaml(self, filepath: str) -> List[Dict]:
        """Parse events from YAML file.

        Args:
            filepath: Path to YAML file

        Returns:
            List of event dictionaries
        """
        try:
            import yaml

            with open(filepath, "r") as f:
                data = yaml.safe_load(f)
                return data.get("events", [])
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML parsing. Install with: pip install pyyaml"
            )
