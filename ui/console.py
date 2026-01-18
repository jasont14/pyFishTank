"""Console UI for pyFishTank."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from models import Fish, Tank, WaterParameters
from services import DataManager, FishManager, MaintenanceManager, TankManager


class ConsoleUI:
    """Console-based user interface for pyFishTank."""

    def __init__(self):
        """Initialize the console UI and managers."""
        self.data_manager = DataManager()
        self.tank_manager = TankManager(self.data_manager)
        self.fish_manager = FishManager(self.data_manager)
        self.maintenance_manager = MaintenanceManager(self.data_manager)

    def run(self) -> None:
        """Run the main application loop."""
        print("\n" + "=" * 40)
        print("       Welcome to pyFishTank!")
        print("=" * 40)

        while True:
            choice = self._show_main_menu()
            if choice == "0":
                print("\nGoodbye! Take care of your fish!")
                break
            elif choice == "1":
                self._tank_menu()
            elif choice == "2":
                self._fish_menu()
            elif choice == "3":
                self._maintenance_menu()
            elif choice == "4":
                self._reports_menu()
            else:
                print("\nInvalid choice. Please try again.")

    def _show_main_menu(self) -> str:
        """Display main menu and get user choice."""
        print("\n" + "=" * 30)
        print("      === pyFishTank ===")
        print("=" * 30)
        print("1. Tank Management")
        print("2. Fish Management")
        print("3. Maintenance Logs")
        print("4. Reports")
        print("0. Exit")
        return input("\nEnter choice: ").strip()

    # ==================== Tank Management ====================

    def _tank_menu(self) -> None:
        """Tank management submenu."""
        while True:
            print("\n--- Tank Management ---")
            print("1. View All Tanks")
            print("2. Add Tank")
            print("3. Edit Tank")
            print("4. Delete Tank")
            print("5. View Tank Details")
            print("0. Back")

            choice = input("\nEnter choice: ").strip()
            if choice == "0":
                break
            elif choice == "1":
                self._view_all_tanks()
            elif choice == "2":
                self._add_tank()
            elif choice == "3":
                self._edit_tank()
            elif choice == "4":
                self._delete_tank()
            elif choice == "5":
                self._view_tank_details()
            else:
                print("\nInvalid choice.")

    def _view_all_tanks(self) -> None:
        """Display all tanks."""
        tanks = self.tank_manager.get_all()
        if not tanks:
            print("\nNo tanks found. Add one to get started!")
            return

        print("\n--- All Tanks ---")
        for i, tank in enumerate(tanks, 1):
            fish_count = len(self.fish_manager.get_by_tank(tank.id))
            print(f"{i}. {tank} - {fish_count} fish")
            if tank.location:
                print(f"   Location: {tank.location}")

    def _add_tank(self) -> None:
        """Add a new tank."""
        print("\n--- Add New Tank ---")

        name = input("Tank name: ").strip()
        if not name:
            print("Name is required.")
            return

        try:
            size = float(input("Size (gallons): ").strip())
        except ValueError:
            print("Invalid size. Please enter a number.")
            return

        print("Tank types: freshwater, saltwater, brackish")
        tank_type = input("Tank type: ").strip().lower()
        if tank_type not in Tank.VALID_TANK_TYPES:
            print(f"Invalid type. Must be one of: {', '.join(Tank.VALID_TANK_TYPES)}")
            return

        location = input("Location (optional): ").strip()
        equipment_str = input("Equipment (comma-separated, optional): ").strip()
        equipment = [e.strip() for e in equipment_str.split(",") if e.strip()]

        try:
            tank = Tank(
                name=name,
                size_gallons=size,
                tank_type=tank_type,
                location=location,
                equipment=equipment,
            )
            self.tank_manager.add(tank)
            print(f"\nTank '{name}' added successfully!")
        except ValueError as e:
            print(f"\nError: {e}")

    def _edit_tank(self) -> None:
        """Edit an existing tank."""
        tank = self._select_tank("Select tank to edit")
        if not tank:
            return

        print(f"\nEditing: {tank}")
        print("(Press Enter to keep current value)")

        name = input(f"Name [{tank.name}]: ").strip() or tank.name

        size_input = input(f"Size [{tank.size_gallons}]: ").strip()
        try:
            size = float(size_input) if size_input else tank.size_gallons
        except ValueError:
            print("Invalid size.")
            return

        print(f"Current type: {tank.tank_type}")
        tank_type = input(f"Tank type [{tank.tank_type}]: ").strip() or tank.tank_type

        location = input(f"Location [{tank.location}]: ").strip()
        if not location and tank.location:
            location = tank.location

        equipment_str = input(
            f"Equipment [{', '.join(tank.equipment)}]: "
        ).strip()
        if equipment_str:
            equipment = [e.strip() for e in equipment_str.split(",") if e.strip()]
        else:
            equipment = tank.equipment

        try:
            tank.name = name
            tank.size_gallons = size
            tank.tank_type = tank_type
            tank.location = location
            tank.equipment = equipment
            self.tank_manager.update(tank)
            print("\nTank updated successfully!")
        except ValueError as e:
            print(f"\nError: {e}")

    def _delete_tank(self) -> None:
        """Delete a tank."""
        tank = self._select_tank("Select tank to delete")
        if not tank:
            return

        fish_count = len(self.fish_manager.get_by_tank(tank.id))
        log_count = len(self.maintenance_manager.get_by_tank(tank.id))

        print(f"\nWarning: This will also delete:")
        print(f"  - {fish_count} fish")
        print(f"  - {log_count} maintenance logs")

        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm == "yes":
            self.fish_manager.delete_by_tank(tank.id)
            self.maintenance_manager.delete_by_tank(tank.id)
            self.tank_manager.delete(tank.id)
            print(f"\nTank '{tank.name}' and all associated data deleted.")
        else:
            print("\nDeletion cancelled.")

    def _view_tank_details(self) -> None:
        """View detailed information about a tank."""
        tank = self._select_tank("Select tank to view")
        if not tank:
            return

        print("\n" + "=" * 40)
        print(f"Tank: {tank.name}")
        print("=" * 40)
        print(f"Size: {tank.size_gallons} gallons")
        print(f"Type: {tank.tank_type}")
        print(f"Location: {tank.location or 'Not specified'}")
        print(f"Equipment: {', '.join(tank.equipment) if tank.equipment else 'None'}")

        if tank.current_parameters:
            print(f"\nCurrent Water Parameters:")
            print(f"  {tank.current_parameters}")

        # Show fish
        fish_list = self.fish_manager.get_by_tank(tank.id)
        print(f"\nFish ({len(fish_list)}):")
        if fish_list:
            for fish in fish_list:
                print(f"  - {fish}")
        else:
            print("  No fish in this tank")

        # Show recent logs
        logs = self.maintenance_manager.get_by_tank(tank.id)[:5]
        print(f"\nRecent Maintenance ({len(logs)} shown):")
        if logs:
            for log in logs:
                print(f"  - {log}")
        else:
            print("  No maintenance logs")

    def _select_tank(self, prompt: str = "Select tank") -> Optional[Tank]:
        """Display tanks and let user select one."""
        tanks = self.tank_manager.get_all()
        if not tanks:
            print("\nNo tanks available.")
            return None

        print(f"\n--- {prompt} ---")
        for i, tank in enumerate(tanks, 1):
            print(f"{i}. {tank}")
        print("0. Cancel")

        try:
            choice = int(input("\nEnter number: ").strip())
            if choice == 0:
                return None
            if 1 <= choice <= len(tanks):
                return tanks[choice - 1]
        except ValueError:
            pass

        print("Invalid selection.")
        return None

    # ==================== Fish Management ====================

    def _fish_menu(self) -> None:
        """Fish management submenu."""
        while True:
            print("\n--- Fish Management ---")
            print("1. View All Fish")
            print("2. Add Fish")
            print("3. Edit Fish")
            print("4. Move Fish")
            print("5. Update Health Status")
            print("6. Remove Fish")
            print("0. Back")

            choice = input("\nEnter choice: ").strip()
            if choice == "0":
                break
            elif choice == "1":
                self._view_all_fish()
            elif choice == "2":
                self._add_fish()
            elif choice == "3":
                self._edit_fish()
            elif choice == "4":
                self._move_fish()
            elif choice == "5":
                self._update_fish_health()
            elif choice == "6":
                self._remove_fish()
            else:
                print("\nInvalid choice.")

    def _view_all_fish(self) -> None:
        """Display all fish grouped by tank."""
        tanks = self.tank_manager.get_all()
        if not tanks:
            print("\nNo tanks found. Add a tank first!")
            return

        total_fish = 0
        for tank in tanks:
            fish_list = self.fish_manager.get_by_tank(tank.id)
            print(f"\n--- {tank.name} ({len(fish_list)} fish) ---")
            if fish_list:
                for fish in fish_list:
                    print(f"  {fish}")
                    total_fish += 1
            else:
                print("  (empty)")

        print(f"\nTotal: {total_fish} fish")

    def _add_fish(self) -> None:
        """Add a new fish."""
        tank = self._select_tank("Select tank for new fish")
        if not tank:
            return

        print(f"\n--- Add Fish to {tank.name} ---")

        name = input("Fish name: ").strip()
        if not name:
            print("Name is required.")
            return

        species = input("Species: ").strip()
        if not species:
            print("Species is required.")
            return

        # Optional fields
        color = input("Color (optional): ").strip() or None
        size = input("Size (optional): ").strip() or None
        feeding = input("Feeding preferences (optional): ").strip() or None
        notes = input("Notes (optional): ").strip() or None

        birth_date = None
        birth_str = input("Birth date (YYYY-MM-DD, optional): ").strip()
        if birth_str:
            try:
                birth_date = date.fromisoformat(birth_str)
            except ValueError:
                print("Invalid date format, skipping birth date.")

        try:
            fish = Fish(
                name=name,
                species=species,
                tank_id=tank.id,
                color=color,
                size=size,
                feeding_preferences=feeding,
                notes=notes,
                birth_date=birth_date,
            )
            self.fish_manager.add(fish)
            print(f"\n{fish.name} added to {tank.name}!")
        except ValueError as e:
            print(f"\nError: {e}")

    def _edit_fish(self) -> None:
        """Edit an existing fish."""
        fish = self._select_fish("Select fish to edit")
        if not fish:
            return

        print(f"\nEditing: {fish}")
        print("(Press Enter to keep current value)")

        name = input(f"Name [{fish.name}]: ").strip() or fish.name
        species = input(f"Species [{fish.species}]: ").strip() or fish.species
        color = input(f"Color [{fish.color or ''}]: ").strip() or fish.color
        size = input(f"Size [{fish.size or ''}]: ").strip() or fish.size
        feeding = (
            input(f"Feeding [{fish.feeding_preferences or ''}]: ").strip()
            or fish.feeding_preferences
        )
        notes = input(f"Notes [{fish.notes or ''}]: ").strip() or fish.notes

        fish.name = name
        fish.species = species
        fish.color = color
        fish.size = size
        fish.feeding_preferences = feeding
        fish.notes = notes

        self.fish_manager.update(fish)
        print("\nFish updated successfully!")

    def _move_fish(self) -> None:
        """Move a fish to a different tank."""
        fish = self._select_fish("Select fish to move")
        if not fish:
            return

        current_tank = self.tank_manager.get_by_id(fish.tank_id)
        print(f"\n{fish.name} is currently in: {current_tank.name if current_tank else 'Unknown'}")

        new_tank = self._select_tank("Select destination tank")
        if not new_tank:
            return

        if new_tank.id == fish.tank_id:
            print("Fish is already in that tank.")
            return

        self.fish_manager.move_to_tank(fish.id, new_tank.id)
        print(f"\n{fish.name} moved to {new_tank.name}!")

    def _update_fish_health(self) -> None:
        """Update a fish's health status."""
        fish = self._select_fish("Select fish to update")
        if not fish:
            return

        print(f"\nCurrent status: {fish.health_status}")
        print("Available statuses:")
        for i, status in enumerate(Fish.VALID_HEALTH_STATUSES, 1):
            print(f"  {i}. {status}")

        try:
            choice = int(input("\nSelect new status: ").strip())
            if 1 <= choice <= len(Fish.VALID_HEALTH_STATUSES):
                new_status = Fish.VALID_HEALTH_STATUSES[choice - 1]
                self.fish_manager.update_health_status(fish.id, new_status)
                print(f"\n{fish.name}'s status updated to: {new_status}")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")

    def _remove_fish(self) -> None:
        """Remove a fish."""
        fish = self._select_fish("Select fish to remove")
        if not fish:
            return

        confirm = input(f"Remove {fish.name}? (yes/no): ").strip().lower()
        if confirm == "yes":
            self.fish_manager.delete(fish.id)
            print(f"\n{fish.name} has been removed.")
        else:
            print("\nCancelled.")

    def _select_fish(self, prompt: str = "Select fish") -> Optional[Fish]:
        """Display fish and let user select one."""
        all_fish = self.fish_manager.get_all()
        if not all_fish:
            print("\nNo fish available.")
            return None

        print(f"\n--- {prompt} ---")
        for i, fish in enumerate(all_fish, 1):
            tank = self.tank_manager.get_by_id(fish.tank_id)
            tank_name = tank.name if tank else "Unknown"
            print(f"{i}. {fish} - Tank: {tank_name}")
        print("0. Cancel")

        try:
            choice = int(input("\nEnter number: ").strip())
            if choice == 0:
                return None
            if 1 <= choice <= len(all_fish):
                return all_fish[choice - 1]
        except ValueError:
            pass

        print("Invalid selection.")
        return None

    # ==================== Maintenance Logs ====================

    def _maintenance_menu(self) -> None:
        """Maintenance logs submenu."""
        while True:
            print("\n--- Maintenance Logs ---")
            print("1. View Recent Logs")
            print("2. Log Water Change")
            print("3. Log Feeding")
            print("4. Log Water Test")
            print("5. Log Filter Cleaning")
            print("6. Log Equipment Check")
            print("7. Log Medication")
            print("0. Back")

            choice = input("\nEnter choice: ").strip()
            if choice == "0":
                break
            elif choice == "1":
                self._view_recent_logs()
            elif choice == "2":
                self._log_water_change()
            elif choice == "3":
                self._log_feeding()
            elif choice == "4":
                self._log_water_test()
            elif choice == "5":
                self._log_filter_clean()
            elif choice == "6":
                self._log_equipment_check()
            elif choice == "7":
                self._log_medication()
            else:
                print("\nInvalid choice.")

    def _view_recent_logs(self) -> None:
        """View recent maintenance logs."""
        logs = self.maintenance_manager.get_recent(20)
        if not logs:
            print("\nNo maintenance logs found.")
            return

        print("\n--- Recent Maintenance Logs ---")
        for log in logs:
            tank = self.tank_manager.get_by_id(log.tank_id)
            tank_name = tank.name if tank else "Unknown"
            print(f"[{tank_name}] {log}")
            if log.water_params:
                print(f"    Parameters: {log.water_params}")

    def _log_water_change(self) -> None:
        """Log a water change."""
        tank = self._select_tank("Select tank")
        if not tank:
            return

        try:
            percentage = int(input("Water change percentage: ").strip())
        except ValueError:
            percentage = None

        description = input("Notes (optional): ").strip()
        log = self.maintenance_manager.log_water_change(tank.id, description, percentage)
        print(f"\nWater change logged for {tank.name}!")

    def _log_feeding(self) -> None:
        """Log a feeding."""
        tank = self._select_tank("Select tank")
        if not tank:
            return

        description = input("Food type/amount: ").strip()
        if not description:
            description = "Regular feeding"

        log = self.maintenance_manager.log_feeding(tank.id, description)
        print(f"\nFeeding logged for {tank.name}!")

    def _log_water_test(self) -> None:
        """Log water test with parameters."""
        tank = self._select_tank("Select tank")
        if not tank:
            return

        print("\nEnter water parameters (press Enter to skip):")

        params = {}

        temp = input("Temperature (F): ").strip()
        if temp:
            try:
                params["temperature"] = float(temp)
            except ValueError:
                pass

        ph = input("pH: ").strip()
        if ph:
            try:
                params["ph"] = float(ph)
            except ValueError:
                pass

        ammonia = input("Ammonia (ppm): ").strip()
        if ammonia:
            try:
                params["ammonia"] = float(ammonia)
            except ValueError:
                pass

        nitrite = input("Nitrite (ppm): ").strip()
        if nitrite:
            try:
                params["nitrite"] = float(nitrite)
            except ValueError:
                pass

        nitrate = input("Nitrate (ppm): ").strip()
        if nitrate:
            try:
                params["nitrate"] = float(nitrate)
            except ValueError:
                pass

        if tank.tank_type == "saltwater":
            salinity = input("Salinity (ppt): ").strip()
            if salinity:
                try:
                    params["salinity"] = float(salinity)
                except ValueError:
                    pass

        notes = input("Notes (optional): ").strip()

        water_params = WaterParameters(**params)
        log = self.maintenance_manager.log_water_test(tank.id, water_params, notes)

        # Update tank's current parameters
        self.tank_manager.update_water_params(tank.id, water_params)

        print(f"\nWater test logged for {tank.name}!")
        print(f"Parameters: {water_params}")

    def _log_filter_clean(self) -> None:
        """Log filter cleaning."""
        tank = self._select_tank("Select tank")
        if not tank:
            return

        description = input("Description: ").strip()
        if not description:
            description = "Filter cleaned/rinsed"

        log = self.maintenance_manager.log_filter_clean(tank.id, description)
        print(f"\nFilter cleaning logged for {tank.name}!")

    def _log_equipment_check(self) -> None:
        """Log equipment check."""
        tank = self._select_tank("Select tank")
        if not tank:
            return

        description = input("Equipment checked/notes: ").strip()
        if not description:
            description = "Equipment checked - all functioning"

        log = self.maintenance_manager.log_equipment_check(tank.id, description)
        print(f"\nEquipment check logged for {tank.name}!")

    def _log_medication(self) -> None:
        """Log medication administration."""
        tank = self._select_tank("Select tank")
        if not tank:
            return

        description = input("Medication and dosage: ").strip()
        if not description:
            print("Medication description is required.")
            return

        log = self.maintenance_manager.log_medication(tank.id, description)
        print(f"\nMedication logged for {tank.name}!")

    # ==================== Reports ====================

    def _reports_menu(self) -> None:
        """Reports submenu."""
        while True:
            print("\n--- Reports ---")
            print("1. Tank Summary")
            print("2. Maintenance History")
            print("3. Water Parameter Trends")
            print("0. Back")

            choice = input("\nEnter choice: ").strip()
            if choice == "0":
                break
            elif choice == "1":
                self._tank_summary()
            elif choice == "2":
                self._maintenance_history()
            elif choice == "3":
                self._water_param_trends()
            else:
                print("\nInvalid choice.")

    def _tank_summary(self) -> None:
        """Display summary of all tanks."""
        tanks = self.tank_manager.get_all()
        if not tanks:
            print("\nNo tanks to summarize.")
            return

        print("\n" + "=" * 50)
        print("           TANK SUMMARY REPORT")
        print("=" * 50)

        total_fish = 0
        total_gallons = 0

        for tank in tanks:
            fish_list = self.fish_manager.get_by_tank(tank.id)
            fish_count = len(fish_list)
            healthy = sum(1 for f in fish_list if f.health_status == "healthy")
            sick = sum(1 for f in fish_list if f.health_status == "sick")
            logs = self.maintenance_manager.get_by_tank(tank.id)
            last_maintenance = logs[0].date.strftime("%Y-%m-%d") if logs else "Never"

            print(f"\n{tank.name}")
            print("-" * 30)
            print(f"  Size: {tank.size_gallons} gallons ({tank.tank_type})")
            print(f"  Location: {tank.location or 'Not specified'}")
            print(f"  Fish: {fish_count} total ({healthy} healthy, {sick} sick)")
            print(f"  Last maintenance: {last_maintenance}")

            total_fish += fish_count
            total_gallons += tank.size_gallons

        print("\n" + "=" * 50)
        print(f"TOTALS: {len(tanks)} tanks, {total_gallons} gallons, {total_fish} fish")
        print("=" * 50)

    def _maintenance_history(self) -> None:
        """Display maintenance history for a tank."""
        tank = self._select_tank("Select tank for history")
        if not tank:
            return

        logs = self.maintenance_manager.get_by_tank(tank.id)
        if not logs:
            print(f"\nNo maintenance history for {tank.name}.")
            return

        print(f"\n--- Maintenance History: {tank.name} ---")
        print(f"Total entries: {len(logs)}\n")

        # Group by activity type
        by_type: dict[str, int] = {}
        for log in logs:
            by_type[log.activity_type] = by_type.get(log.activity_type, 0) + 1

        print("Activity breakdown:")
        for activity, count in sorted(by_type.items()):
            display_name = {
                "water_change": "Water Changes",
                "filter_clean": "Filter Cleanings",
                "feeding": "Feedings",
                "water_test": "Water Tests",
                "equipment_check": "Equipment Checks",
                "medication": "Medications",
            }.get(activity, activity)
            print(f"  {display_name}: {count}")

        print("\nRecent entries:")
        for log in logs[:10]:
            print(f"  {log}")

    def _water_param_trends(self) -> None:
        """Display water parameter history for a tank."""
        tank = self._select_tank("Select tank for water trends")
        if not tank:
            return

        params_history = self.maintenance_manager.get_water_param_history(tank.id, 10)
        if not params_history:
            print(f"\nNo water test data for {tank.name}.")
            return

        print(f"\n--- Water Parameter Trends: {tank.name} ---")
        print(f"Last {len(params_history)} tests:\n")

        for params in params_history:
            print(f"  {params}")

        # Show averages if we have data
        if len(params_history) > 1:
            print("\nAverages:")
            temps = [p.temperature for p in params_history if p.temperature is not None]
            phs = [p.ph for p in params_history if p.ph is not None]
            ammonias = [p.ammonia for p in params_history if p.ammonia is not None]
            nitrites = [p.nitrite for p in params_history if p.nitrite is not None]
            nitrates = [p.nitrate for p in params_history if p.nitrate is not None]

            if temps:
                print(f"  Temperature: {sum(temps) / len(temps):.1f}F")
            if phs:
                print(f"  pH: {sum(phs) / len(phs):.2f}")
            if ammonias:
                print(f"  Ammonia: {sum(ammonias) / len(ammonias):.2f} ppm")
            if nitrites:
                print(f"  Nitrite: {sum(nitrites) / len(nitrites):.2f} ppm")
            if nitrates:
                print(f"  Nitrate: {sum(nitrates) / len(nitrates):.1f} ppm")
