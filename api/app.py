import datetime
import os
import random
import secrets
import uuid

from flask import Flask, jsonify, request, send_from_directory

from api.utils import DEV_PATHS, QUOTES, require_api_key
from api.views import bp as views_bp

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.register_blueprint(views_bp)

# Simulated database
ROADMAPS_DB = {}


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "service": "Developer Roadmap API",
            "version": "1.0.0",
            "endpoints": [
                {"path": "/create", "method": "POST", "description": "Create a new roadmap"},
                {"path": "/roadmap/<roadmap_id>", "method": "GET", "description": "Retrieve a specific roadmap"},
                {"path": "/quote", "method": "GET", "description": "Get a random inspirational quote"},
                {"path": "/paths", "method": "GET", "description": "List available development paths"},
            ],
            "usage": "Send a POST request to /create with name, interests (array), and timeframe (months)",
        }
    )


@app.route("/quote", methods=["GET"])
def get_random_quote():
    return jsonify(secrets.choice(QUOTES))


@app.route("/paths", methods=["GET"])
def get_paths():
    return jsonify(
        {
            "available_paths": list(DEV_PATHS.keys()),
            "description": "These paths can be used in the 'interests' field when creating a roadmap",
        }
    )


@app.route("/create", methods=["POST"])
@require_api_key
def create_roadmap():
    data = request.json

    # Validate required fields
    required_fields = ["name", "interests", "timeframe"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields", "required_fields": required_fields}), 400

    # Validate interests
    interests = data["interests"]
    if not interests or not all(interest in DEV_PATHS for interest in interests):
        return jsonify({"error": "Invalid interests provided", "available_paths": list(DEV_PATHS.keys())}), 400

    # Validate timeframe
    try:
        timeframe = int(data["timeframe"])
        if timeframe < 1 or timeframe > 24:
            return jsonify({"error": "Timeframe must be between 1 and 24 months"}), 400
    except ValueError:
        return jsonify({"error": "Timeframe must be a number"}), 400

    # Generate a unique ID for the roadmap
    roadmap_id = str(uuid.uuid4())

    # Calculate milestone dates
    start_date = datetime.datetime.now()
    end_date = start_date + datetime.timedelta(days=timeframe * 30)

    # Create personalized roadmap
    roadmap = []

    # Distribute milestones across the timeframe
    for interest in interests:
        path_data = DEV_PATHS[interest]

        # Create milestones with dates
        milestone_count = min(timeframe, len(path_data["milestones"]))
        selected_milestones = path_data["milestones"][:milestone_count]

        for i, milestone in enumerate(selected_milestones):
            milestone_date = start_date + datetime.timedelta(days=(i + 1) * (timeframe * 30 // (milestone_count + 1)))
            roadmap.append(
                {
                    "path": interest,
                    "milestone": milestone,
                    "target_date": milestone_date.strftime("%Y-%m-%d"),
                    "completed": False,
                }
            )

    # Sort roadmap by date
    roadmap.sort(key=lambda x: x["target_date"])

    # Create the roadmap
    time_roadmap = {
        "id": roadmap_id,
        "name": data["name"],
        "interests": interests,
        "timeframe": timeframe,
        "created_at": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "roadmap": roadmap,
        "resources": {
            interest: selected_resources
            for interest, selected_resources in [
                (i, random.sample(DEV_PATHS[i]["resources"], min(3, len(DEV_PATHS[i]["resources"]))))
                for i in interests
            ]
        },
        "tips": {
            interest: selected_tips
            for interest, selected_tips in [
                (i, random.sample(DEV_PATHS[i]["tips"], min(2, len(DEV_PATHS[i]["tips"])))) for i in interests
            ]
        },
        "quote": secrets.choice(QUOTES),
    }

    # Store in our simulated database
    ROADMAPS_DB[roadmap_id] = time_roadmap

    return jsonify(
        {
            "message": "Roadmap created successfully",
            "roadmap_id": roadmap_id,
            "summary": {
                "name": time_roadmap["name"],
                "timeframe": f"{timeframe} months",
                "paths": interests,
                "milestones_count": len(roadmap),
            },
        }
    )


@app.route("/roadmap/<roadmap_id>", methods=["GET"])
def get_roadmap(roadmap_id):
    if roadmap_id not in ROADMAPS_DB:
        return jsonify({"error": "Roadmap not found"}), 404

    return jsonify(ROADMAPS_DB[roadmap_id])


@app.route("/roadmap/<roadmap_id>/milestone/<int:milestone_index>", methods=["PUT"])
@require_api_key
def update_milestone(roadmap_id, milestone_index):
    if roadmap_id not in ROADMAPS_DB:
        return jsonify({"error": "Roadmap not found"}), 404

    roadmap = ROADMAPS_DB[roadmap_id]

    if milestone_index >= len(roadmap["roadmap"]) or milestone_index < 0:
        return jsonify({"error": "Invalid milestone index"}), 400

    data = request.json
    if "completed" in data:
        roadmap["roadmap"][milestone_index]["completed"] = bool(data["completed"])

        # Check if all milestones are completed
        all_completed = all(milestone["completed"] for milestone in roadmap["roadmap"])

        return jsonify(
            {
                "message": "Milestone updated successfully",
                "milestone": roadmap["roadmap"][milestone_index],
                "all_completed": all_completed,
                "progress": sum(1 for m in roadmap["roadmap"] if m["completed"]) / len(roadmap["roadmap"]) * 100,
            }
        )
    else:
        return jsonify({"error": "Missing 'completed' field in request body"}), 400


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon")


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
