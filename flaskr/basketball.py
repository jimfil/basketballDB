from flask import Blueprint, render_template, request, redirect, url_for
from .auth import login_required
from basketballDB.model import (
    get_teams,
    get_players,
    get_all_events,
    get_player_stats,
    get_matches,
    get_match_stats,
    create_team,
    get_matches_by_team,
    get_scores,
    get_player_shot_stats,
    create_season,
    create_player,
    get_person_attributes,
)

bp = Blueprint("basketball", __name__, url_prefix="/basketball")


@bp.route("/", defaults={"offset": 0})
@bp.route("/<int:offset>")
@login_required
def index(offset):
    """Show teams with pagination."""
    teams = get_teams(offset=offset)
    return render_template("basketball/index.html", teams=teams, offset=offset)


@bp.route("/events")
@login_required
def events():
    """Show all the events."""
    events = get_all_events()
    return render_template("basketball/events.html", events=events)


@bp.route("/matches")
@login_required
def matches():
    """Show all the matches."""
    matches = get_matches()
    print(matches)
    return render_template("basketball/matches.html", matches=matches)


@bp.route("/player/<int:id>")
@login_required
def player_details(id):
    """Show a player's stats."""
    stats = get_player_stats(id)
    return render_template("basketball/player_details.html", stats=stats)


@bp.route("/match/<int:id>")
@login_required
def match_details(id):
    """Show a match's stats and score."""
    stats = get_match_stats(id)
    scores = get_scores(id)
    return render_template("basketball/match_details.html", stats=stats, scores=scores)


@bp.route("/team/create", methods=("GET", "POST"))
@login_required
def create_team_route():
    """Create a new team."""
    if request.method == "POST":
        team_name = request.form["team_name"]
        if team_name:
            create_team(team_name)
            return redirect(url_for("basketball.index", offset=0))
    return render_template("basketball/create_team.html")


@bp.route("/team/<int:team_id>/matches")
@login_required
def team_matches(team_id):
    """Show all the matches for a team."""
    team_name, matches = get_matches_by_team(team_id, 0)
    return render_template(
        "basketball/team_matches.html", team_name=team_name[0]["name"], matches=matches
    )

@bp.route("/team/<int:team_id>/players")
@login_required
def team_players(team_id):
    """Show all the players for a team."""
    players = get_players(team_id)
    return render_template("basketball/team_players.html", players=players, team_id=team_id)


@bp.route("/player/<int:player_id>/shot-percentage")
@login_required
def player_shot_percentage(player_id):
    """Show a player's shot percentage."""
    shot_types = ["Free Throw", "2-Point Field Goal", "3-Point Field Goal"]
    shot_stats = {}
    for shot_type in shot_types:
        stats = get_player_shot_stats(player_id, shot_type)
        made = stats.get(f"{shot_type} Made", 0)
        missed = stats.get(f"{shot_type} Attempt", 0)
        total_attempts = made + missed
        if total_attempts == 0:
            percentage = 0
        else:
            percentage = (made / total_attempts) * 100
        shot_stats[shot_type] = {
            "made": made,
            "missed": missed,
            "total": total_attempts,
            "percentage": percentage,
        }
    return render_template(
        "basketball/player_shot_percentage.html",
        player_id=player_id,
        shot_stats=shot_stats,
    )


@bp.route("/season/create", methods=("GET", "POST"))
@login_required
def create_season_route():
    """Create a new season."""
    if request.method == "POST":
        year = request.form["year"]
        if year:
            create_season(year)
            return redirect(url_for("explorer.index"))
    return render_template("basketball/create_season.html")


@bp.route("/player/create", methods=("GET", "POST"))
@login_required
def create_player_route():
    """Create a new player."""
    if request.method == "POST":
        player_data = request.form.to_dict()
        create_player(player_data)
        return redirect(url_for("basketball.index", offset=0))
    
    person_attributes = get_person_attributes()
    # Limit to 1000 teams to avoid performance issues with a large number of teams
    teams = get_teams(limit=1000)
    return render_template("basketball/create_player.html", person_attributes=person_attributes, teams=teams)
