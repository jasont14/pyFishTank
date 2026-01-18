"""Business logic managers for tanks, fish, and maintenance."""

from datetime import datetime, date
from typing import Optional
from uuid import UUID

from models import Fish, MaintenanceLog, Tank, WaterParameters
from services.data_manager import DataManager


class TankManager:
    """Manages tank operations and persistence."""

    def __init__(self, data_manager: DataManager):
        self.db = data_manager

    def get_all(self) -> list[Tank]:
        """Get all tanks."""
        cursor = self.db.execute("SELECT * FROM tanks")
        tanks = []
        for row in cursor.fetchall():
            tank = self._row_to_tank(row)
            tank.current_parameters = self._get_latest_params(tank.id)
            tanks.append(tank)
        return tanks

    def get_by_id(self, tank_id: UUID) -> Optional[Tank]:
        """Get a tank by ID."""
        cursor = self.db.execute("SELECT * FROM tanks WHERE id = ?", (str(tank_id),))
        row = cursor.fetchone()
        if row:
            tank = self._row_to_tank(row)
            tank.current_parameters = self._get_latest_params(tank.id)
            return tank
        return None

    def add(self, tank: Tank) -> None:
        """Add a new tank."""
        self.db.execute(
            """INSERT INTO tanks (id, name, size_gallons, tank_type, location, equipment)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                str(tank.id),
                tank.name,
                tank.size_gallons,
                tank.tank_type,
                tank.location,
                ",".join(tank.equipment),
            ),
        )
        self.db.commit()

    def update(self, tank: Tank) -> bool:
        """Update an existing tank."""
        cursor = self.db.execute(
            """UPDATE tanks SET name = ?, size_gallons = ?, tank_type = ?,
               location = ?, equipment = ? WHERE id = ?""",
            (
                tank.name,
                tank.size_gallons,
                tank.tank_type,
                tank.location,
                ",".join(tank.equipment),
                str(tank.id),
            ),
        )
        self.db.commit()
        return cursor.rowcount > 0

    def delete(self, tank_id: UUID) -> bool:
        """Delete a tank by ID."""
        cursor = self.db.execute("DELETE FROM tanks WHERE id = ?", (str(tank_id),))
        self.db.commit()
        return cursor.rowcount > 0

    def update_water_params(self, tank_id: UUID, params: WaterParameters) -> bool:
        """Update current water parameters for a tank."""
        self.db.execute(
            """INSERT INTO water_parameters
               (tank_id, date_tested, temperature, ph, ammonia, nitrite, nitrate, salinity)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(tank_id),
                params.date_tested.isoformat(),
                params.temperature,
                params.ph,
                params.ammonia,
                params.nitrite,
                params.nitrate,
                params.salinity,
            ),
        )
        self.db.commit()
        return True

    def _get_latest_params(self, tank_id: UUID) -> Optional[WaterParameters]:
        """Get the most recent water parameters for a tank."""
        cursor = self.db.execute(
            """SELECT * FROM water_parameters WHERE tank_id = ?
               ORDER BY date_tested DESC LIMIT 1""",
            (str(tank_id),),
        )
        row = cursor.fetchone()
        if row:
            return WaterParameters(
                date_tested=datetime.fromisoformat(row["date_tested"]),
                temperature=row["temperature"],
                ph=row["ph"],
                ammonia=row["ammonia"],
                nitrite=row["nitrite"],
                nitrate=row["nitrate"],
                salinity=row["salinity"],
            )
        return None

    def _row_to_tank(self, row) -> Tank:
        """Convert a database row to a Tank object."""
        equipment = row["equipment"].split(",") if row["equipment"] else []
        return Tank(
            id=UUID(row["id"]),
            name=row["name"],
            size_gallons=row["size_gallons"],
            tank_type=row["tank_type"],
            location=row["location"] or "",
            equipment=equipment,
        )


class FishManager:
    """Manages fish operations and persistence."""

    def __init__(self, data_manager: DataManager):
        self.db = data_manager

    def get_all(self) -> list[Fish]:
        """Get all fish."""
        cursor = self.db.execute("SELECT * FROM fish")
        return [self._row_to_fish(row) for row in cursor.fetchall()]

    def get_by_id(self, fish_id: UUID) -> Optional[Fish]:
        """Get a fish by ID."""
        cursor = self.db.execute("SELECT * FROM fish WHERE id = ?", (str(fish_id),))
        row = cursor.fetchone()
        return self._row_to_fish(row) if row else None

    def get_by_tank(self, tank_id: UUID) -> list[Fish]:
        """Get all fish in a specific tank."""
        cursor = self.db.execute(
            "SELECT * FROM fish WHERE tank_id = ?", (str(tank_id),)
        )
        return [self._row_to_fish(row) for row in cursor.fetchall()]

    def add(self, fish: Fish) -> None:
        """Add a new fish."""
        self.db.execute(
            """INSERT INTO fish (id, name, species, tank_id, date_added, birth_date,
               health_status, size, color, feeding_preferences, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(fish.id),
                fish.name,
                fish.species,
                str(fish.tank_id),
                fish.date_added.isoformat(),
                fish.birth_date.isoformat() if fish.birth_date else None,
                fish.health_status,
                fish.size,
                fish.color,
                fish.feeding_preferences,
                fish.notes,
            ),
        )
        self.db.commit()

    def update(self, fish: Fish) -> bool:
        """Update an existing fish."""
        cursor = self.db.execute(
            """UPDATE fish SET name = ?, species = ?, tank_id = ?, date_added = ?,
               birth_date = ?, health_status = ?, size = ?, color = ?,
               feeding_preferences = ?, notes = ? WHERE id = ?""",
            (
                fish.name,
                fish.species,
                str(fish.tank_id),
                fish.date_added.isoformat(),
                fish.birth_date.isoformat() if fish.birth_date else None,
                fish.health_status,
                fish.size,
                fish.color,
                fish.feeding_preferences,
                fish.notes,
                str(fish.id),
            ),
        )
        self.db.commit()
        return cursor.rowcount > 0

    def move_to_tank(self, fish_id: UUID, new_tank_id: UUID) -> bool:
        """Move a fish to a different tank."""
        cursor = self.db.execute(
            "UPDATE fish SET tank_id = ? WHERE id = ?",
            (str(new_tank_id), str(fish_id)),
        )
        self.db.commit()
        return cursor.rowcount > 0

    def update_health_status(self, fish_id: UUID, status: str) -> bool:
        """Update a fish's health status."""
        if status not in Fish.VALID_HEALTH_STATUSES:
            return False
        cursor = self.db.execute(
            "UPDATE fish SET health_status = ? WHERE id = ?",
            (status, str(fish_id)),
        )
        self.db.commit()
        return cursor.rowcount > 0

    def delete(self, fish_id: UUID) -> bool:
        """Delete a fish by ID."""
        cursor = self.db.execute("DELETE FROM fish WHERE id = ?", (str(fish_id),))
        self.db.commit()
        return cursor.rowcount > 0

    def delete_by_tank(self, tank_id: UUID) -> int:
        """Delete all fish in a tank. Returns count of deleted fish."""
        cursor = self.db.execute(
            "DELETE FROM fish WHERE tank_id = ?", (str(tank_id),)
        )
        self.db.commit()
        return cursor.rowcount

    def _row_to_fish(self, row) -> Fish:
        """Convert a database row to a Fish object."""
        return Fish(
            id=UUID(row["id"]),
            name=row["name"],
            species=row["species"],
            tank_id=UUID(row["tank_id"]),
            date_added=date.fromisoformat(row["date_added"]),
            birth_date=date.fromisoformat(row["birth_date"]) if row["birth_date"] else None,
            health_status=row["health_status"],
            size=row["size"],
            color=row["color"],
            feeding_preferences=row["feeding_preferences"],
            notes=row["notes"],
        )


class MaintenanceManager:
    """Manages maintenance log operations and persistence."""

    def __init__(self, data_manager: DataManager):
        self.db = data_manager

    def get_all(self) -> list[MaintenanceLog]:
        """Get all maintenance logs, sorted by date descending."""
        cursor = self.db.execute(
            "SELECT * FROM maintenance_logs ORDER BY date DESC"
        )
        return [self._row_to_log(row) for row in cursor.fetchall()]

    def get_by_tank(self, tank_id: UUID) -> list[MaintenanceLog]:
        """Get all logs for a specific tank, sorted by date descending."""
        cursor = self.db.execute(
            "SELECT * FROM maintenance_logs WHERE tank_id = ? ORDER BY date DESC",
            (str(tank_id),),
        )
        return [self._row_to_log(row) for row in cursor.fetchall()]

    def get_recent(self, limit: int = 10) -> list[MaintenanceLog]:
        """Get most recent logs across all tanks."""
        cursor = self.db.execute(
            "SELECT * FROM maintenance_logs ORDER BY date DESC LIMIT ?", (limit,)
        )
        return [self._row_to_log(row) for row in cursor.fetchall()]

    def get_by_activity_type(
        self, activity_type: str, tank_id: Optional[UUID] = None
    ) -> list[MaintenanceLog]:
        """Get logs by activity type, optionally filtered by tank."""
        if tank_id:
            cursor = self.db.execute(
                """SELECT * FROM maintenance_logs
                   WHERE activity_type = ? AND tank_id = ? ORDER BY date DESC""",
                (activity_type, str(tank_id)),
            )
        else:
            cursor = self.db.execute(
                "SELECT * FROM maintenance_logs WHERE activity_type = ? ORDER BY date DESC",
                (activity_type,),
            )
        return [self._row_to_log(row) for row in cursor.fetchall()]

    def add(self, log: MaintenanceLog) -> None:
        """Add a new maintenance log."""
        water_params_id = None
        if log.water_params:
            cursor = self.db.execute(
                """INSERT INTO water_parameters
                   (tank_id, date_tested, temperature, ph, ammonia, nitrite, nitrate, salinity)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(log.tank_id),
                    log.water_params.date_tested.isoformat(),
                    log.water_params.temperature,
                    log.water_params.ph,
                    log.water_params.ammonia,
                    log.water_params.nitrite,
                    log.water_params.nitrate,
                    log.water_params.salinity,
                ),
            )
            water_params_id = cursor.lastrowid

        self.db.execute(
            """INSERT INTO maintenance_logs
               (id, tank_id, date, activity_type, description, water_params_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                str(log.id),
                str(log.tank_id),
                log.date.isoformat(),
                log.activity_type,
                log.description,
                water_params_id,
            ),
        )
        self.db.commit()

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
        # First delete associated water parameters
        self.db.execute(
            """DELETE FROM water_parameters WHERE id IN
               (SELECT water_params_id FROM maintenance_logs WHERE tank_id = ?)""",
            (str(tank_id),),
        )
        cursor = self.db.execute(
            "DELETE FROM maintenance_logs WHERE tank_id = ?", (str(tank_id),)
        )
        self.db.commit()
        return cursor.rowcount

    def get_water_param_history(
        self, tank_id: UUID, limit: int = 10
    ) -> list[WaterParameters]:
        """Get water parameter history for a tank."""
        cursor = self.db.execute(
            """SELECT wp.* FROM water_parameters wp
               JOIN maintenance_logs ml ON wp.id = ml.water_params_id
               WHERE ml.tank_id = ? AND ml.activity_type = 'water_test'
               ORDER BY wp.date_tested DESC LIMIT ?""",
            (str(tank_id), limit),
        )
        params = []
        for row in cursor.fetchall():
            params.append(
                WaterParameters(
                    date_tested=datetime.fromisoformat(row["date_tested"]),
                    temperature=row["temperature"],
                    ph=row["ph"],
                    ammonia=row["ammonia"],
                    nitrite=row["nitrite"],
                    nitrate=row["nitrate"],
                    salinity=row["salinity"],
                )
            )
        return params

    def _row_to_log(self, row) -> MaintenanceLog:
        """Convert a database row to a MaintenanceLog object."""
        water_params = None
        if row["water_params_id"]:
            cursor = self.db.execute(
                "SELECT * FROM water_parameters WHERE id = ?",
                (row["water_params_id"],),
            )
            wp_row = cursor.fetchone()
            if wp_row:
                water_params = WaterParameters(
                    date_tested=datetime.fromisoformat(wp_row["date_tested"]),
                    temperature=wp_row["temperature"],
                    ph=wp_row["ph"],
                    ammonia=wp_row["ammonia"],
                    nitrite=wp_row["nitrite"],
                    nitrate=wp_row["nitrate"],
                    salinity=wp_row["salinity"],
                )

        return MaintenanceLog(
            id=UUID(row["id"]),
            tank_id=UUID(row["tank_id"]),
            date=datetime.fromisoformat(row["date"]),
            activity_type=row["activity_type"],
            description=row["description"],
            water_params=water_params,
        )
