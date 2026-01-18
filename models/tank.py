"""Tank data model."""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4

from .water_params import WaterParameters


@dataclass
class Tank:
    """Represents a fish tank."""

    name: str
    size_gallons: float
    tank_type: str  # freshwater, saltwater, brackish
    id: UUID = field(default_factory=uuid4)
    location: str = ""
    equipment: list[str] = field(default_factory=list)
    current_parameters: Optional[WaterParameters] = None

    VALID_TANK_TYPES = ("freshwater", "saltwater", "brackish")

    def __post_init__(self):
        """Validate fields after initialization."""
        if self.tank_type not in self.VALID_TANK_TYPES:
            raise ValueError(
                f"Invalid tank type: {self.tank_type}. "
                f"Must be one of {self.VALID_TANK_TYPES}"
            )
        if self.size_gallons <= 0:
            raise ValueError("Tank size must be positive")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "size_gallons": self.size_gallons,
            "tank_type": self.tank_type,
            "location": self.location,
            "equipment": self.equipment,
            "current_parameters": (
                self.current_parameters.to_dict() if self.current_parameters else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tank":
        """Create instance from dictionary."""
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            size_gallons=data["size_gallons"],
            tank_type=data["tank_type"],
            location=data.get("location", ""),
            equipment=data.get("equipment", []),
            current_parameters=(
                WaterParameters.from_dict(data["current_parameters"])
                if data.get("current_parameters")
                else None
            ),
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.name} ({self.size_gallons}gal {self.tank_type})"
