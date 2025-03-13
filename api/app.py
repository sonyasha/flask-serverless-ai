import datetime
import os
import random
import uuid

from flask import Flask, jsonify, request

from api.views import bp as views_bp

from .utils import require_api_key

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.register_blueprint(views_bp)

# Simulated database
ROADMAPS_DB = {}

# Development paths with associated resources, milestones and tips
DEV_PATHS = {
    "frontend": {
        "resources": [
            "MDN Web Docs for fundamentals",
            "React official documentation",
            "CSS Tricks for advanced styling",
            "Frontend Masters courses",
            "State of JS reports for trends",
        ],
        "milestones": [
            "Build a responsive portfolio website",
            "Create a dynamic web app with React",
            "Implement animations and transitions",
            "Master state management patterns",
            "Build a progressive web app",
        ],
        "tips": [
            "Focus on accessibility from day one",
            "Learn browser dev tools deeply",
            "Practice responsive design principles",
            "Test on multiple browsers regularly",
            "Study popular UI libraries' source code",
        ],
    },
    "backend": {
        "resources": [
            "Official Python documentation",
            "FastAPI or Flask documentation",
            "Database design patterns book",
            "API design guidelines",
            "Systems Design primer",
        ],
        "milestones": [
            "Build a RESTful API service",
            "Implement user authentication",
            "Create a data processing pipeline",
            "Set up automated testing",
            "Deploy microservices architecture",
        ],
        "tips": [
            "Always validate user input",
            "Use environment variables for configuration",
            "Handle errors gracefully with clear messages",
            "Design with scaling in mind",
            "Document your APIs thoroughly",
        ],
    },
    "devops": {
        "resources": [
            "AWS official documentation",
            "Docker and Kubernetes guides",
            "Terraform or CloudFormation tutorials",
            "CI/CD pipeline examples",
            "SRE books from Google",
        ],
        "milestones": [
            "Automate deployment processes",
            "Set up monitoring and alerting",
            "Implement infrastructure as code",
            "Create disaster recovery plans",
            "Optimize for cost and performance",
        ],
        "tips": [
            "Start with small, focused services",
            "Practice chaos engineering",
            "Prioritize security at every layer",
            "Automate everything possible",
            "Learn to interpret performance metrics",
        ],
    },
    "mobile": {
        "resources": [
            "Flutter or React Native documentation",
            "iOS/Android design guidelines",
            "Mobile UX research articles",
            "App store optimization guides",
            "Mobile performance benchmarks",
        ],
        "milestones": [
            "Create a basic app with navigation",
            "Implement offline functionality",
            "Add push notifications",
            "Optimize battery usage",
            "Release to app stores",
        ],
        "tips": [
            "Test on real devices regularly",
            "Focus on performance from the start",
            "Design for different screen sizes",
            "Consider accessibility features",
            "Plan for app updates and maintenance",
        ],
    },
    "ai": {
        "resources": [
            "Fast.ai courses",
            "PyTorch or TensorFlow tutorials",
            "Kaggle competitions",
            "Research papers on arXiv",
            "Hugging Face documentation",
        ],
        "milestones": [
            "Implement a basic ML model",
            "Build a data preprocessing pipeline",
            "Train a model on custom data",
            "Deploy a model to production",
            "Create an AI-powered application",
        ],
        "tips": [
            "Start with simple, well-understood models",
            "Focus on data quality first",
            "Keep track of all experiments",
            "Consider ethical implications",
            "Learn to explain your models to non-experts",
        ],
    },
}

# Inspirational quotes about learning and growth
QUOTES = [
    {
        "text": "The best time to plant a tree was 20 years ago. The second best time is now.",
        "author": "Chinese Proverb",
    },
    {"text": "Your future is created by what you do today, not tomorrow.", "author": "Robert Kiyosaki"},
    {"text": "The expert in anything was once a beginner.", "author": "Helen Hayes"},
    {"text": "The only way to learn programming is by writing code.", "author": "Richard Stallman"},
    {
        "text": "Don't worry about failure; worry about the chances you miss when you don't even try.",
        "author": "Jack Canfield",
    },
    {
        "text": "Learning is not attained by chance, it must be sought for with ardor and diligence.",
        "author": "Abigail Adams",
    },
    {
        "text": "The capacity to learn is a gift; the ability to learn is a skill; the willingness to learn is a choice.",
        "author": "Brian Herbert",
    },
    {
        "text": "Patience, persistence and perspiration make an unbeatable combination for success.",
        "author": "Napoleon Hill",
    },
    {"text": "Every expert was once a beginner. Don't be afraid to take that first step.", "author": "Unknown"},
    {"text": "The beautiful thing about learning is that nobody can take it away from you.", "author": "B.B. King"},
]


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
            "usage": "Send a POST request to /create with name, email, interests (array), and timeframe (months)",
        }
    )


@app.route("/quote", methods=["GET"])
def get_random_quote():
    return jsonify(random.choice(QUOTES))


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
    required_fields = ["name", "email", "interests", "timeframe"]
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
        "email": data["email"],
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
        "quote": random.choice(QUOTES),
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
