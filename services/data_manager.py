"""Data manager for JSON file I/O operations."""

import json
from pathlib import Path
from typing import TypeVar, Callable

T = TypeVar("T")


class DataManager:
    """Handles reading and writing data to JSON files."""

    def __init__(self, data_dir: str = "data"):
        """Initialize the data manager.

        Args:
            data_dir: Directory path for storing JSON files.
        """
        self.data_dir = Path(data_dir)
        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        """Create data directory if it doesn't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, filename: str) -> Path:
        """Get full path for a data file."""
        return self.data_dir / filename

    def load(self, filename: str) -> list[dict]:
        """Load data from a JSON file.

        Args:
            filename: Name of the JSON file (e.g., 'tanks.json').

        Returns:
            List of dictionaries from the JSON file, or empty list if file doesn't exist.
        """
        file_path = self._get_file_path(filename)
        if not file_path.exists():
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def save(self, filename: str, data: list[dict]) -> None:
        """Save data to a JSON file.

        Args:
            filename: Name of the JSON file.
            data: List of dictionaries to save.
        """
        file_path = self._get_file_path(filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_entities(
        self, filename: str, from_dict: Callable[[dict], T]
    ) -> list[T]:
        """Load entities from a JSON file using a converter function.

        Args:
            filename: Name of the JSON file.
            from_dict: Function to convert dict to entity.

        Returns:
            List of entities.
        """
        data = self.load(filename)
        entities = []
        for item in data:
            try:
                entities.append(from_dict(item))
            except (KeyError, ValueError, TypeError):
                # Skip invalid entries
                continue
        return entities

    def save_entities(
        self, filename: str, entities: list, to_dict: Callable = None
    ) -> None:
        """Save entities to a JSON file.

        Args:
            filename: Name of the JSON file.
            entities: List of entities to save.
            to_dict: Optional function to convert entity to dict.
                     If None, uses entity.to_dict() method.
        """
        if to_dict:
            data = [to_dict(e) for e in entities]
        else:
            data = [e.to_dict() for e in entities]
        self.save(filename, data)
