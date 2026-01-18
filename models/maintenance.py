"""Maintenance log data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from .water_params import WaterParameters


@dataclass
class MaintenanceLog:
    """Represents a maintenance activity for a tank."""

    tank_id: UUID
    activity_type: str
    description: str
    id: UUID = field(default_factory=uuid4)
    date: datetime = field(default_factory=datetime.now)
    water_params: Optional[WaterParameters] = None

    VALID_ACTIVITY_TYPES = (
        "water_change",
        "filter_clean",
        "feeding",
        "water_test",
        "equipment_check",
        "medication",
    )

    def __post_init__(self):
        """Validate fields after initialization."""
        if self.activity_type not in self.VALID_ACTIVITY_TYPES:
            raise ValueError(
                f"Invalid activity type: {self.activity_type}. "
                f"Must be one of {self.VALID_ACTIVITY_TYPES}"
            )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "tank_id": str(self.tank_id),
            "date": self.date.isoformat(),
            "activity_type": self.activity_type,
            "description": self.description,
            "water_params": self.water_params.to_dict() if self.water_params else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MaintenanceLog":
        """Create instance from dictionary."""
        return cls(
            id=UUID(data["id"]),
            tank_id=UUID(data["tank_id"]),
            date=datetime.fromisoformat(data["date"]),
            activity_type=data["activity_type"],
            description=data["description"],
            water_params=(
                WaterParameters.from_dict(data["water_params"])
                if data.get("water_params")
                else None
            ),
        )

    @property
    def activity_display_name(self) -> str:
        """Get human-readable activity type name."""
        return {
            "water_change": "Water Change",
            "filter_clean": "Filter Cleaning",
            "feeding": "Feeding",
            "water_test": "Water Test",
            "equipment_check": "Equipment Check",
            "medication": "Medication",
        }.get(self.activity_type, self.activity_type)

    def __str__(self) -> str:
        """Human-readable string representation."""
        date_str = self.date.strftime("%Y-%m-%d %H:%M")
        return f"[{date_str}] {self.activity_display_name}: {self.description}"
