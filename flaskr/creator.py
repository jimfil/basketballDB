from flask import Blueprint, render_template, request, redirect, url_for, flash
from .auth import login_required
from basketballDB import model

bp = Blueprint("creator", __name__, url_prefix="/creator")

@bp.route("/")
@login_required
def index():
    """Show links to create different entities."""
    return render_template("creator/index.html")

@bp.route("/season/create", methods=("GET", "POST"))
@login_required
def create_season_route():
    if request.method == "POST":
        year = request.form["year"]
        error = None

        if not year:
            error = "Year is required."

        if error is not None:
            flash(error)
        else:
            model.create_season(year)
            return redirect(url_for("creator.index"))

    return render_template("creator/create_season.html")

@bp.route("/team/create", methods=("GET", "POST"))
@login_required
def create_team_route():
    if request.method == "POST":
        team_name = request.form["team_name"]
        error = None

        if not team_name:
            error = "Team name is required."

        if error is not None:
            flash(error)
        else:
            model.create_team(team_name)
            return redirect(url_for("basketball.index"))

    return render_template("creator/create_team.html")

@bp.route("/person/create", methods=("GET", "POST"))
@login_required
def create_person_route():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        speciality = request.form["speciality"]
        error = None

        if not first_name:
            error = "First name is required."
        elif not last_name:
            error = "Last name is required."
        elif not speciality:
            error = "Speciality is required."

        if error is not None:
            flash(error)
        else:
            model.create_person(first_name, last_name, speciality)
            return redirect(url_for("creator.index"))

    return render_template("creator/create_person.html")

@bp.route("/phase/create", methods=("GET", "POST"))
@login_required
def create_phase_route():
    if request.method == "POST":
        year = request.form["year"]
        phase_id = request.form["phase_id"]
        error = None

        if not year:
            error = "Year is required."
        elif not phase_id:
            error = "Phase ID is required."

        if error is not None:
            flash(error)
        else:
            model.create_phase(phase_id, year)
            return redirect(url_for("creator.index"))

    seasons = model.get_seasons()
    return render_template("creator/create_phase.html", seasons=seasons)

@bp.route("/round/create", methods=("GET", "POST"))
@login_required
def create_round_route():
    if request.method == "POST":
        phase_id = request.form["phase_id"]
        round_id = request.form["round_id"]
        error = None

        if not phase_id:
            error = "Phase is required."
        elif not round_id:
            error = "Round ID is required."

        if error is not None:
            flash(error)
        else:
            model.create_entry('round', [round_id, phase_id])
            return redirect(url_for("creator.index"))

    phases = model.get_phases()
    return render_template("creator/create_round.html", phases=phases)

@bp.route("/person_team/create", methods=("GET", "POST"))
@login_required
def create_person_team_route():
    if request.method == "POST":
        person_id = request.form["person_id"]
        team_id = request.form["team_id"]
        shirt_num = request.form["shirt_num"]
        beginning = request.form["beginning"] or None
        ending = request.form["ending"] or None
        error = None

        if not person_id:
            error = "Person is required."
        elif not team_id:
            error = "Team is required."
        elif not shirt_num:
            error = "Shirt number is required."

        if error is not None:
            flash(error)
        else:
            model.create_entry('person_team', [person_id, team_id, beginning, ending, shirt_num])
            return redirect(url_for("creator.index"))

    persons = model.get_persons()
    teams = model.get_teams(limit=0)
    return render_template("creator/create_person_team.html", persons=persons, teams=teams)

@bp.route("/match_referee/create", methods=("GET", "POST"))
@login_required
def create_match_referee_route():
    if request.method == "POST":
        match_id = request.form["match_id"]
        referee_id = request.form["referee_id"]
        error = None

        if not match_id:
            error = "Match is required."
        elif not referee_id:
            error = "Referee is required."

        if error is not None:
            flash(error)
        else:
            model.create_entry('match_referee', [match_id, referee_id])
            return redirect(url_for("creator.index"))

    matches = model.get_matches()
    referees = model.get_referees()
    return render_template("creator/create_match_referee.html", matches=matches, referees=referees)

@bp.route("/event_creation/create", methods=("GET", "POST"))
@login_required
def create_event_creation_route():
    if request.method == "POST":
        event_id = request.form["event_id"]
        person_id = request.form["person_id"]
        match_id = request.form["match_id"]
        game_time = request.form["game_time"] or None
        error = None

        if not event_id:
            error = "Event is required."
        elif not person_id:
            error = "Person is required."
        elif not match_id:
            error = "Match is required."

        if error is not None:
            flash(error)
        else:
            model.create_event_creation(match_id, person_id, event_id, game_time)
            return redirect(url_for("creator.index"))

    events = model.get_all_events()
    persons = model.get_persons()
    matches = model.get_matches()
    return render_template("creator/create_event_creation.html", events=events, persons=persons, matches=matches)

@bp.route("/match", methods=("GET", "POST"))
@login_required
def create_match_route():
    """Create a new match."""
    if request.method == "POST":
        # 'id' is auto-increment, so we don't provide it.
        # The order of columns in the table is: id, match_date, status, round_id, stadium_id, home_team_id, away_team_id
        match_date = request.form["match_date"]
        status = request.form["status"]
        round_id = request.form["round_id"]
        stadium_id = request.form["stadium_id"]
        home_team_id = request.form["home_team_id"]
        away_team_id = request.form["away_team_id"]
        
        values = [match_date, status, round_id, stadium_id, home_team_id, away_team_id]
        model.create_entry('match', values)
        return redirect(url_for("creator.index"))

    season_year = request.args.get("season_year")
    phase_id = request.args.get("phase_id")
    round_id = request.args.get("round_id")

    seasons = model.get_seasons()
    phases = None
    rounds = None
    stadiums = None
    teams = None

    if season_year:
        phases = model.get_phases_by_season(season_year)
    if phase_id:
        rounds = model.get_rounds_by_phase(phase_id)
    if round_id:
        stadiums = model.get_stadiums()
        teams = model.get_teams(limit=0)

    return render_template(
        "creator/create_match.html",
        seasons=seasons,
        phases=phases,
        rounds=rounds,
        stadiums=stadiums,
        teams=teams,
        selected_season=season_year,
        selected_phase=phase_id,
        selected_round=round_id,
    )

@bp.route("/team_stadium", methods=("GET", "POST"))
@login_required
def create_team_stadium_route():
    """Create a new team-stadium association."""
    if request.method == "POST":
        values = [request.form[attr] for attr in model.return_attributes('team_stadium') if attr != 'id']
        model.create_entry('team_stadium', values)
        return redirect(url_for("creator.index"))

    teams = model.get_teams(limit=0)
    stadiums = model.get_stadiums()
    rounds = model.get_rounds()
    return render_template("creator/create_team_stadium.html", teams=teams, stadiums=stadiums, rounds=rounds)

@bp.route("/create/<string:table_name>", methods=("GET", "POST"))
@login_required
def create_entity(table_name):
    """Create a new entry for a given table."""
    if request.method == "POST":
        attributes = model.return_attributes(table_name)
        values = [request.form[attr] for attr in attributes if attr != 'id']
        model.create_entry(table_name, values)
        return redirect(url_for("creator.index"))

    attributes = model.return_attributes(table_name)
    return render_template("creator/create_entity.html", table_name=table_name, attributes=[attr for attr in attributes if attr != 'id'])


