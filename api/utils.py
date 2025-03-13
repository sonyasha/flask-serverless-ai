import os
from functools import wraps

from flask import jsonify, request

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


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != os.environ["API_KEY"]:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)

    return decorated_function
