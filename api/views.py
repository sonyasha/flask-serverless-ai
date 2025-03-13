import os

import requests
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

API_KEY = os.environ["API_KEY"]
bp = Blueprint("views", __name__, template_folder="templates")


def api_request(method, endpoint, data=None):
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    url = f"{request.url_root}{endpoint}"

    if method.lower() == "get":
        response = requests.get(url, headers=headers)
    elif method.lower() == "post":
        response = requests.post(url, headers=headers, json=data)
    elif method.lower() == "put":
        response = requests.put(url, headers=headers, json=data)
    else:
        raise ValueError(f"Unsupported method: {method}")

    return response


@bp.route("/home", methods=["GET"])
def home():
    quote_response = requests.get(f"{request.url_root}quote")
    quote = quote_response.json() if quote_response.ok else {"text": "Loading failed", "author": "System"}

    return render_template("home.html", quote=quote)


@bp.route("/dashboard", methods=["GET"])
def dashboard():
    quote_response = requests.get(f"{request.url_root}quote")
    quote = quote_response.json() if quote_response.ok else {"text": "Loading failed", "author": "System"}

    paths_response = requests.get(f"{request.url_root}paths")
    paths = paths_response.json()["available_paths"] if paths_response.ok else []

    user_roadmaps = session.get("user_roadmaps", [])
    roadmaps_data = []

    for roadmap_id in user_roadmaps:
        try:
            response = api_request("get", f"roadmap/{roadmap_id}")
            if response.ok:
                roadmaps_data.append(response.json())
        except Exception:
            # Log the error in a production app
            pass

    return render_template("dashboard.html", quote=quote, paths=paths, roadmaps=roadmaps_data)


@bp.route("/create-roadmap", methods=["GET", "POST"])
def create_roadmap():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        interests = request.form.getlist("interests")
        timeframe = request.form.get("timeframe")

        if not all([name, email, interests, timeframe]):
            flash("All fields are required", "error")
            return redirect(url_for("views.create_roadmap"))

        try:
            timeframe = int(timeframe)
        except ValueError:
            flash("Timeframe must be a number", "error")
            return redirect(url_for("views.create_roadmap"))

        data = {"name": name, "email": email, "interests": interests, "timeframe": timeframe}

        try:
            response = api_request("post", "create", data)

            if response.ok:
                response_data = response.json()
                roadmap_id = response_data.get("roadmap_id")

                user_roadmaps = session.get("user_roadmaps", [])
                user_roadmaps.append(roadmap_id)
                session["user_roadmaps"] = user_roadmaps

                flash("Roadmap created successfully!", "success")
                return redirect(url_for("views.view_roadmap", roadmap_id=roadmap_id))
            else:
                error_data = response.json()
                flash(f"Error: {error_data.get('error', 'Unknown error')}", "error")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for("views.create_roadmap"))

    paths_response = requests.get(f"{request.url_root}paths")
    paths = paths_response.json()["available_paths"] if paths_response.ok else []

    return render_template("create_roadmap.html", paths=paths)


@bp.route("/roadmaps/<roadmap_id>", methods=["GET"])
def view_roadmap(roadmap_id):
    try:
        response = api_request("get", f"roadmap/{roadmap_id}")

        if response.ok:
            roadmap_data = response.json()
            return render_template("view_roadmap.html", roadmap=roadmap_data)
        else:
            flash("Roadmap not found", "error")
            return redirect(url_for("views.dashboard"))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("views.dashboard"))


@bp.route("/roadmaps/<roadmap_id>/update-milestone/<int:milestone_index>", methods=["POST"])
def update_milestone(roadmap_id, milestone_index):
    completed = request.form.get("completed") == "true"

    try:
        response = api_request("put", f"roadmap/{roadmap_id}/milestone/{milestone_index}", {"completed": completed})

        if response.ok:
            flash("Milestone updated successfully", "success")
        else:
            error_data = response.json()
            flash(f"Error: {error_data.get('error', 'Unknown error')}", "error")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")

    return redirect(url_for("views.view_roadmap", roadmap_id=roadmap_id))


# Redirect root to home page
@bp.route("/ui", methods=["GET"])
def ui_redirect():
    return redirect(url_for("views.home"))
