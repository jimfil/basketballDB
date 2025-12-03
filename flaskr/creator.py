from flask import Blueprint, render_template, request, redirect, url_for
from .auth import login_required
from basketballDB.model import create_season, create_team, create_stadium, create_person, create_referee, create_event, create_phase, get_seasons

bp = Blueprint("creator", __name__, url_prefix="/creator")

@bp.route("/")
@login_required
def index():
    """Show all the creator options."""
    return render_template("creator/index.html")

@bp.route("/season", methods=("GET", "POST"))
@login_required
def create_season_route():
    """Create a new season."""
    if request.method == "POST":
        year = request.form["year"]
        if year:
            create_season(year)
            return redirect(url_for("creator.index"))
    return render_template("creator/create_season.html")

@bp.route("/team", methods=("GET", "POST"))
@login_required
def create_team_route():
    """Create a new team."""
    if request.method == "POST":
        team_name = request.form["team_name"]
        if team_name:
            create_team(team_name)
            return redirect(url_for("creator.index"))
    return render_template("creator/create_team.html")

@bp.route("/stadium", methods=("GET", "POST"))
@login_required
def create_stadium_route():
    """Create a new stadium."""
    if request.method == "POST":
        stadium_name = request.form["stadium_name"]
        capacity = request.form["capacity"]
        if stadium_name and capacity:
            create_stadium(stadium_name, capacity)
            return redirect(url_for("creator.index"))
    return render_template("creator/create_stadium.html")

@bp.route("/person", methods=("GET", "POST"))
@login_required
def create_person_route():
    """Create a new person."""
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        speciality = request.form["speciality"]
        if first_name and last_name and speciality:
            create_person(first_name, last_name, speciality)
            return redirect(url_for("creator.index"))
    return render_template("creator/create_person.html")

@bp.route("/referee", methods=("GET", "POST"))
@login_required
def create_referee_route():
    """Create a new referee."""
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        if first_name and last_name:
            create_referee(first_name, last_name)
            return redirect(url_for("creator.index"))
    return render_template("creator/create_referee.html")

@bp.route("/event", methods=("GET", "POST"))
@login_required
def create_event_route():
    """Create a new event."""
    if request.method == "POST":
        name = request.form["name"]
        type = request.form["type"]
        subtype = request.form["subtype"]
        if name and type and subtype:
            create_event(name, type, subtype)
            return redirect(url_for("creator.index"))
    return render_template("creator/create_event.html")

@bp.route("/phase", methods=("GET", "POST"))
@login_required
def create_phase_route():
    """Create a new phase."""
    if request.method == "POST":
        year = request.form["year"]
        name = request.form["name"]
        if year and name:
            create_phase(year, name)
            return redirect(url_for("creator.index"))
    seasons = get_seasons()
    return render_template("creator/create_phase.html", seasons=seasons)