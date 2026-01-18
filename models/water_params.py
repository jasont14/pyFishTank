"""Water parameters data model for tracking tank water quality."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class WaterParameters:
    """Represents water quality parameters for a fish tank."""

    date_tested: datetime = field(default_factory=datetime.now)
    temperature: Optional[float] = None  # Fahrenheit
    ph: Optional[float] = None
    ammonia: Optional[float] = None  # ppm
    nitrite: Optional[float] = None  # ppm
    nitrate: Optional[float] = None  # ppm
    salinity: Optional[float] = None  # ppt, for saltwater tanks

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "date_tested": self.date_tested.isoformat(),
            "temperature": self.temperature,
            "ph": self.ph,
            "ammonia": self.ammonia,
            "nitrite": self.nitrite,
            "nitrate": self.nitrate,
            "salinity": self.salinity,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WaterParameters":
        """Create instance from dictionary."""
        return cls(
            date_tested=datetime.fromisoformat(data["date_tested"]),
            temperature=data.get("temperature"),
            ph=data.get("ph"),
            ammonia=data.get("ammonia"),
            nitrite=data.get("nitrite"),
            nitrate=data.get("nitrate"),
            salinity=data.get("salinity"),
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        parts = [f"Tested: {self.date_tested.strftime('%Y-%m-%d %H:%M')}"]
        if self.temperature is not None:
            parts.append(f"Temp: {self.temperature}°F")
        if self.ph is not None:
            parts.append(f"pH: {self.ph}")
        if self.ammonia is not None:
            parts.append(f"Ammonia: {self.ammonia} ppm")
        if self.nitrite is not None:
            parts.append(f"Nitrite: {self.nitrite} ppm")
        if self.nitrate is not None:
            parts.append(f"Nitrate: {self.nitrate} ppm")
        if self.salinity is not None:
            parts.append(f"Salinity: {self.salinity} ppt")
        return " | ".join(parts)
