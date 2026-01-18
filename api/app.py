"""Flask application for pyFishTank REST API."""

from datetime import date, datetime
from uuid import UUID

from flask import Flask, jsonify, request
from flask_cors import CORS

from models import Fish, MaintenanceLog, Tank, WaterParameters
from services.data_manager import DataManager
from services.managers import FishManager, MaintenanceManager, TankManager

app = Flask(__name__)
CORS(app)

# Initialize managers
data_manager = DataManager()
tank_manager = TankManager(data_manager)
fish_manager = FishManager(data_manager)
maintenance_manager = MaintenanceManager(data_manager)


# Helper functions
def parse_uuid(uuid_str: str) -> UUID:
    """Parse a UUID string."""
    return UUID(uuid_str)


# Tank routes
@app.route("/api/tanks", methods=["GET"])
def get_tanks():
    """Get all tanks."""
    tanks = tank_manager.get_all()
    return jsonify([t.to_dict() for t in tanks])


@app.route("/api/tanks/<tank_id>", methods=["GET"])
def get_tank(tank_id: str):
    """Get a specific tank."""
    tank = tank_manager.get_by_id(parse_uuid(tank_id))
    if not tank:
        return jsonify({"error": "Tank not found"}), 404
    return jsonify(tank.to_dict())


@app.route("/api/tanks", methods=["POST"])
def create_tank():
    """Create a new tank."""
    data = request.json
    try:
        tank = Tank(
            name=data["name"],
            size_gallons=float(data["size_gallons"]),
            tank_type=data["tank_type"],
            location=data.get("location", ""),
            equipment=data.get("equipment", []),
        )
        tank_manager.add(tank)
        return jsonify(tank.to_dict()), 201
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/tanks/<tank_id>", methods=["PUT"])
def update_tank(tank_id: str):
    """Update a tank."""
    data = request.json
    tank = tank_manager.get_by_id(parse_uuid(tank_id))
    if not tank:
        return jsonify({"error": "Tank not found"}), 404

    try:
        updated_tank = Tank(
            id=tank.id,
            name=data.get("name", tank.name),
            size_gallons=float(data.get("size_gallons", tank.size_gallons)),
            tank_type=data.get("tank_type", tank.tank_type),
            location=data.get("location", tank.location),
            equipment=data.get("equipment", tank.equipment),
            current_parameters=tank.current_parameters,
        )
        tank_manager.update(updated_tank)
        return jsonify(updated_tank.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/tanks/<tank_id>", methods=["DELETE"])
def delete_tank(tank_id: str):
    """Delete a tank and all associated fish and logs."""
    uuid = parse_uuid(tank_id)
    tank = tank_manager.get_by_id(uuid)
    if not tank:
        return jsonify({"error": "Tank not found"}), 404

    # Cascade delete
    fish_manager.delete_by_tank(uuid)
    maintenance_manager.delete_by_tank(uuid)
    tank_manager.delete(uuid)
    return jsonify({"message": "Tank deleted"}), 200


@app.route("/api/tanks/<tank_id>/water-params", methods=["PUT"])
def update_water_params(tank_id: str):
    """Update water parameters for a tank."""
    data = request.json
    uuid = parse_uuid(tank_id)
    tank = tank_manager.get_by_id(uuid)
    if not tank:
        return jsonify({"error": "Tank not found"}), 404

    params = WaterParameters(
        temperature=data.get("temperature"),
        ph=data.get("ph"),
        ammonia=data.get("ammonia"),
        nitrite=data.get("nitrite"),
        nitrate=data.get("nitrate"),
        salinity=data.get("salinity"),
    )
    tank_manager.update_water_params(uuid, params)
    return jsonify(params.to_dict())


# Fish routes
@app.route("/api/fish", methods=["GET"])
def get_all_fish():
    """Get all fish, optionally filtered by tank."""
    tank_id = request.args.get("tank_id")
    if tank_id:
        fish = fish_manager.get_by_tank(parse_uuid(tank_id))
    else:
        fish = fish_manager.get_all()
    return jsonify([f.to_dict() for f in fish])


@app.route("/api/fish/<fish_id>", methods=["GET"])
def get_fish(fish_id: str):
    """Get a specific fish."""
    fish = fish_manager.get_by_id(parse_uuid(fish_id))
    if not fish:
        return jsonify({"error": "Fish not found"}), 404
    return jsonify(fish.to_dict())


@app.route("/api/fish", methods=["POST"])
def create_fish():
    """Create a new fish."""
    data = request.json
    try:
        fish = Fish(
            name=data["name"],
            species=data["species"],
            tank_id=parse_uuid(data["tank_id"]),
            health_status=data.get("health_status", "healthy"),
            size=data.get("size"),
            color=data.get("color"),
            feeding_preferences=data.get("feeding_preferences"),
            notes=data.get("notes"),
            birth_date=date.fromisoformat(data["birth_date"]) if data.get("birth_date") else None,
        )
        fish_manager.add(fish)
        return jsonify(fish.to_dict()), 201
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/fish/<fish_id>", methods=["PUT"])
def update_fish(fish_id: str):
    """Update a fish."""
    data = request.json
    fish = fish_manager.get_by_id(parse_uuid(fish_id))
    if not fish:
        return jsonify({"error": "Fish not found"}), 404

    try:
        updated_fish = Fish(
            id=fish.id,
            name=data.get("name", fish.name),
            species=data.get("species", fish.species),
            tank_id=parse_uuid(data["tank_id"]) if "tank_id" in data else fish.tank_id,
            date_added=fish.date_added,
            birth_date=date.fromisoformat(data["birth_date"]) if data.get("birth_date") else fish.birth_date,
            health_status=data.get("health_status", fish.health_status),
            size=data.get("size", fish.size),
            color=data.get("color", fish.color),
            feeding_preferences=data.get("feeding_preferences", fish.feeding_preferences),
            notes=data.get("notes", fish.notes),
        )
        fish_manager.update(updated_fish)
        return jsonify(updated_fish.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/fish/<fish_id>", methods=["DELETE"])
def delete_fish(fish_id: str):
    """Delete a fish."""
    if not fish_manager.delete(parse_uuid(fish_id)):
        return jsonify({"error": "Fish not found"}), 404
    return jsonify({"message": "Fish deleted"}), 200


@app.route("/api/fish/<fish_id>/move", methods=["POST"])
def move_fish(fish_id: str):
    """Move a fish to a different tank."""
    data = request.json
    if not fish_manager.move_to_tank(parse_uuid(fish_id), parse_uuid(data["tank_id"])):
        return jsonify({"error": "Fish not found"}), 404
    return jsonify({"message": "Fish moved"})


@app.route("/api/fish/<fish_id>/health", methods=["PUT"])
def update_fish_health(fish_id: str):
    """Update a fish's health status."""
    data = request.json
    if not fish_manager.update_health_status(parse_uuid(fish_id), data["health_status"]):
        return jsonify({"error": "Fish not found or invalid status"}), 400
    return jsonify({"message": "Health status updated"})


# Maintenance routes
@app.route("/api/maintenance", methods=["GET"])
def get_maintenance_logs():
    """Get maintenance logs, optionally filtered by tank or activity type."""
    tank_id = request.args.get("tank_id")
    activity_type = request.args.get("activity_type")
    limit = request.args.get("limit", type=int)

    if activity_type:
        logs = maintenance_manager.get_by_activity_type(
            activity_type,
            parse_uuid(tank_id) if tank_id else None
        )
    elif tank_id:
        logs = maintenance_manager.get_by_tank(parse_uuid(tank_id))
    elif limit:
        logs = maintenance_manager.get_recent(limit)
    else:
        logs = maintenance_manager.get_all()

    return jsonify([log.to_dict() for log in logs])


@app.route("/api/maintenance", methods=["POST"])
def create_maintenance_log():
    """Create a maintenance log."""
    data = request.json
    tank_id = parse_uuid(data["tank_id"])
    activity_type = data["activity_type"]
    description = data.get("description", "")

    try:
        if activity_type == "water_change":
            log = maintenance_manager.log_water_change(
                tank_id, description, data.get("percentage")
            )
        elif activity_type == "feeding":
            log = maintenance_manager.log_feeding(tank_id, description)
        elif activity_type == "filter_clean":
            log = maintenance_manager.log_filter_clean(tank_id, description)
        elif activity_type == "equipment_check":
            log = maintenance_manager.log_equipment_check(tank_id, description)
        elif activity_type == "medication":
            log = maintenance_manager.log_medication(tank_id, description)
        elif activity_type == "water_test":
            params_data = data.get("water_params", {})
            params = WaterParameters(
                temperature=params_data.get("temperature"),
                ph=params_data.get("ph"),
                ammonia=params_data.get("ammonia"),
                nitrite=params_data.get("nitrite"),
                nitrate=params_data.get("nitrate"),
                salinity=params_data.get("salinity"),
            )
            log = maintenance_manager.log_water_test(tank_id, params, description)
        else:
            return jsonify({"error": f"Invalid activity type: {activity_type}"}), 400

        return jsonify(log.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/tanks/<tank_id>/water-params/history", methods=["GET"])
def get_water_param_history(tank_id: str):
    """Get water parameter history for a tank."""
    limit = request.args.get("limit", 10, type=int)
    params = maintenance_manager.get_water_param_history(parse_uuid(tank_id), limit)
    return jsonify([p.to_dict() for p in params])


# Reports endpoints
@app.route("/api/reports/summary", methods=["GET"])
def get_summary_report():
    """Get a summary report of all tanks."""
    tanks = tank_manager.get_all()
    summary = []

    for tank in tanks:
        fish_list = fish_manager.get_by_tank(tank.id)
        logs = maintenance_manager.get_by_tank(tank.id)

        health_counts = {"healthy": 0, "sick": 0, "recovering": 0, "deceased": 0}
        for fish in fish_list:
            health_counts[fish.health_status] += 1

        last_maintenance = logs[0].date.isoformat() if logs else None

        summary.append({
            "tank": tank.to_dict(),
            "fish_count": len(fish_list),
            "health_counts": health_counts,
            "maintenance_count": len(logs),
            "last_maintenance": last_maintenance,
        })

    return jsonify(summary)


def run_server(host="127.0.0.1", port=5001, debug=True):
    """Run the Flask development server."""
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server()
