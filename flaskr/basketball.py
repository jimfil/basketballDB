from flask import Blueprint, render_template
from .auth import login_required
from basketballDB.model import get_teams, get_players, get_all_events, get_player_stats, get_matches, get_match_stats

bp = Blueprint("basketball", __name__, url_prefix="/basketball")


@bp.route("/")
@login_required
def index():
    """Show all the teams and players."""
    teams = get_teams()
    players = get_players()
    return render_template("basketball/index.html", teams=teams, players=players)


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
    """Show a match's stats."""
    stats = get_match_stats(id)
    return render_template("basketball/match_details.html", stats=stats)
