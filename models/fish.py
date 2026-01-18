"""Fish data model."""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Fish:
    """Represents a fish in a tank."""

    name: str
    species: str
    tank_id: UUID
    id: UUID = field(default_factory=uuid4)
    date_added: date = field(default_factory=date.today)
    birth_date: Optional[date] = None
    health_status: str = "healthy"  # healthy, sick, recovering, deceased
    size: Optional[str] = None
    color: Optional[str] = None
    feeding_preferences: Optional[str] = None
    notes: Optional[str] = None

    VALID_HEALTH_STATUSES = ("healthy", "sick", "recovering", "deceased")

    def __post_init__(self):
        """Validate fields after initialization."""
        if self.health_status not in self.VALID_HEALTH_STATUSES:
            raise ValueError(
                f"Invalid health status: {self.health_status}. "
                f"Must be one of {self.VALID_HEALTH_STATUSES}"
            )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "species": self.species,
            "tank_id": str(self.tank_id),
            "date_added": self.date_added.isoformat(),
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "health_status": self.health_status,
            "size": self.size,
            "color": self.color,
            "feeding_preferences": self.feeding_preferences,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Fish":
        """Create instance from dictionary."""
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            species=data["species"],
            tank_id=UUID(data["tank_id"]),
            date_added=date.fromisoformat(data["date_added"]),
            birth_date=date.fromisoformat(data["birth_date"]) if data.get("birth_date") else None,
            health_status=data.get("health_status", "healthy"),
            size=data.get("size"),
            color=data.get("color"),
            feeding_preferences=data.get("feeding_preferences"),
            notes=data.get("notes"),
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        status_icon = {
            "healthy": "✓",
            "sick": "✗",
            "recovering": "↻",
            "deceased": "†",
        }.get(self.health_status, "?")
        return f"{self.name} ({self.species}) [{status_icon}]"
