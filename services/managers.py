"""Business logic managers for tanks, fish, and maintenance."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from models import Fish, MaintenanceLog, Tank, WaterParameters
from services.data_manager import DataManager


class TankManager:
    """Manages tank operations and persistence."""

    FILENAME = "tanks.json"

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self._tanks: list[Tank] = []
        self.load()

    def load(self) -> None:
        """Load tanks from storage."""
        self._tanks = self.data_manager.load_entities(self.FILENAME, Tank.from_dict)

    def save(self) -> None:
        """Save tanks to storage."""
        self.data_manager.save_entities(self.FILENAME, self._tanks)

    def get_all(self) -> list[Tank]:
        """Get all tanks."""
        return self._tanks.copy()

    def get_by_id(self, tank_id: UUID) -> Optional[Tank]:
        """Get a tank by ID."""
        for tank in self._tanks:
            if tank.id == tank_id:
                return tank
        return None

    def add(self, tank: Tank) -> None:
        """Add a new tank."""
        self._tanks.append(tank)
        self.save()

    def update(self, tank: Tank) -> bool:
        """Update an existing tank."""
        for i, t in enumerate(self._tanks):
            if t.id == tank.id:
                self._tanks[i] = tank
                self.save()
                return True
        return False

    def delete(self, tank_id: UUID) -> bool:
        """Delete a tank by ID."""
        for i, tank in enumerate(self._tanks):
            if tank.id == tank_id:
                del self._tanks[i]
                self.save()
                return True
        return False

    def update_water_params(self, tank_id: UUID, params: WaterParameters) -> bool:
        """Update current water parameters for a tank."""
        tank = self.get_by_id(tank_id)
        if tank:
            tank.current_parameters = params
            self.save()
            return True
        return False


class FishManager:
    """Manages fish operations and persistence."""

    FILENAME = "fish.json"

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self._fish: list[Fish] = []
        self.load()

    def load(self) -> None:
        """Load fish from storage."""
        self._fish = self.data_manager.load_entities(self.FILENAME, Fish.from_dict)

    def save(self) -> None:
        """Save fish to storage."""
        self.data_manager.save_entities(self.FILENAME, self._fish)

    def get_all(self) -> list[Fish]:
        """Get all fish."""
        return self._fish.copy()

    def get_by_id(self, fish_id: UUID) -> Optional[Fish]:
        """Get a fish by ID."""
        for fish in self._fish:
            if fish.id == fish_id:
                return fish
        return None

    def get_by_tank(self, tank_id: UUID) -> list[Fish]:
        """Get all fish in a specific tank."""
        return [f for f in self._fish if f.tank_id == tank_id]

    def add(self, fish: Fish) -> None:
        """Add a new fish."""
        self._fish.append(fish)
        self.save()

    def update(self, fish: Fish) -> bool:
        """Update an existing fish."""
        for i, f in enumerate(self._fish):
            if f.id == fish.id:
                self._fish[i] = fish
                self.save()
                return True
        return False

    def move_to_tank(self, fish_id: UUID, new_tank_id: UUID) -> bool:
        """Move a fish to a different tank."""
        fish = self.get_by_id(fish_id)
        if fish:
            fish.tank_id = new_tank_id
            self.save()
            return True
        return False

    def update_health_status(self, fish_id: UUID, status: str) -> bool:
        """Update a fish's health status."""
        fish = self.get_by_id(fish_id)
        if fish and status in Fish.VALID_HEALTH_STATUSES:
            fish.health_status = status
            self.save()
            return True
        return False

    def delete(self, fish_id: UUID) -> bool:
        """Delete a fish by ID."""
        for i, fish in enumerate(self._fish):
            if fish.id == fish_id:
                del self._fish[i]
                self.save()
                return True
        return False

    def delete_by_tank(self, tank_id: UUID) -> int:
        """Delete all fish in a tank. Returns count of deleted fish."""
        original_count = len(self._fish)
        self._fish = [f for f in self._fish if f.tank_id != tank_id]
        deleted = original_count - len(self._fish)
        if deleted > 0:
            self.save()
        return deleted


class MaintenanceManager:
    """Manages maintenance log operations and persistence."""

    FILENAME = "maintenance.json"

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self._logs: list[MaintenanceLog] = []
        self.load()

    def load(self) -> None:
        """Load maintenance logs from storage."""
        self._logs = self.data_manager.load_entities(
            self.FILENAME, MaintenanceLog.from_dict
        )

    def save(self) -> None:
        """Save maintenance logs to storage."""
        self.data_manager.save_entities(self.FILENAME, self._logs)

    def get_all(self) -> list[MaintenanceLog]:
        """Get all maintenance logs, sorted by date descending."""
        return sorted(self._logs, key=lambda x: x.date, reverse=True)

    def get_by_tank(self, tank_id: UUID) -> list[MaintenanceLog]:
        """Get all logs for a specific tank, sorted by date descending."""
        logs = [log for log in self._logs if log.tank_id == tank_id]
        return sorted(logs, key=lambda x: x.date, reverse=True)

    def get_recent(self, limit: int = 10) -> list[MaintenanceLog]:
        """Get most recent logs across all tanks."""
        return self.get_all()[:limit]

    def get_by_activity_type(
        self, activity_type: str, tank_id: Optional[UUID] = None
    ) -> list[MaintenanceLog]:
        """Get logs by activity type, optionally filtered by tank."""
        logs = self._logs
        if tank_id:
            logs = [log for log in logs if log.tank_id == tank_id]
        logs = [log for log in logs if log.activity_type == activity_type]
        return sorted(logs, key=lambda x: x.date, reverse=True)

    def add(self, log: MaintenanceLog) -> None:
        """Add a new maintenance log."""
        self._logs.append(log)
        self.save()

    def log_water_change(
        self, tank_id: UUID, description: str, percentage: Optional[int] = None
    ) -> MaintenanceLog:
        """Log a water change activity."""
        if percentage:
            description = f"{percentage}% water change. {description}".strip()
        log = MaintenanceLog(
            tank_id=tank_id,
            activity_type="water_change",
            description=description,
        )
        self.add(log)
        return log

    def log_feeding(self, tank_id: UUID, description: str) -> MaintenanceLog:
        """Log a feeding activity."""
        log = MaintenanceLog(
            tank_id=tank_id,
            activity_type="feeding",
            description=description,
        )
        self.add(log)
        return log

    def log_water_test(
        self, tank_id: UUID, params: WaterParameters, notes: str = ""
    ) -> MaintenanceLog:
        """Log a water test with parameters."""
        log = MaintenanceLog(
            tank_id=tank_id,
            activity_type="water_test",
            description=notes or "Water parameters tested",
            water_params=params,
        )
        self.add(log)
        return log

    def log_filter_clean(self, tank_id: UUID, description: str) -> MaintenanceLog:
        """Log a filter cleaning activity."""
        log = MaintenanceLog(
            tank_id=tank_id,
            activity_type="filter_clean",
            description=description,
        )
        self.add(log)
        return log

    def log_equipment_check(self, tank_id: UUID, description: str) -> MaintenanceLog:
        """Log an equipment check activity."""
        log = MaintenanceLog(
            tank_id=tank_id,
            activity_type="equipment_check",
            description=description,
        )
        self.add(log)
        return log

    def log_medication(self, tank_id: UUID, description: str) -> MaintenanceLog:
        """Log a medication activity."""
        log = MaintenanceLog(
            tank_id=tank_id,
            activity_type="medication",
            description=description,
        )
        self.add(log)
        return log

    def delete_by_tank(self, tank_id: UUID) -> int:
        """Delete all logs for a tank. Returns count of deleted logs."""
        original_count = len(self._logs)
        self._logs = [log for log in self._logs if log.tank_id != tank_id]
        deleted = original_count - len(self._logs)
        if deleted > 0:
            self.save()
        return deleted

    def get_water_param_history(
        self, tank_id: UUID, limit: int = 10
    ) -> list[WaterParameters]:
        """Get water parameter history for a tank."""
        tests = self.get_by_activity_type("water_test", tank_id)
        params = [log.water_params for log in tests if log.water_params]
        return params[:limit]
