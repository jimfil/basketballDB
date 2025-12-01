from flask import Blueprint, render_template, request
from .auth import login_required
from basketballDB.model import (
    get_seasons,
    get_phases_by_season,
    get_rounds_by_phase,
    get_matches_by_round,
    get_match,
    get_players_in_match,
    get_match_stats,
    get_matches_by_phase,
    get_scores,
    get_team_name,
    calculate_standings_for_phase,
)

bp = Blueprint("explorer", __name__, url_prefix="/explorer")


def calculate_standings(phase_id):
    """Calculates standings for a given phase_id using an optimized query."""
    return calculate_standings_for_phase(phase_id)


@bp.route("/")
@login_required
def index():
    season_year = request.args.get("season_year")
    phase_id = request.args.get("phase_id")
    round_id = request.args.get("round_id")

    seasons = get_seasons()
    phases = None
    rounds = None
    matches = None

    if season_year:
        phases = get_phases_by_season(season_year)
    if phase_id:
        rounds = get_rounds_by_phase(phase_id)
    if round_id:
        matches = get_matches_by_round(round_id)

    return render_template(
        "explorer/index.html",
        seasons=seasons,
        phases=phases,
        rounds=rounds,
        matches=matches,
        selected_season=season_year,
        selected_phase=phase_id,
        selected_round=round_id,
    )


@bp.route("/match/<int:match_id>")
@login_required
def match_details(match_id):
    match = get_match(match_id)
    players = get_players_in_match(match_id)
    events = get_match_stats(match_id)

    return render_template(
        "explorer/match_details.html",
        match=match[0] if match else None,
        players=players,
        events=events,
    )


@bp.route("/standings")
@login_required
def standings():
    season_year = request.args.get("season_year")
    phase_id = request.args.get("phase_id")
    standings = None
    phases = None
    seasons = get_seasons()
    if season_year:
        phases = get_phases_by_season(season_year)
    if phase_id:
        standings = calculate_standings(phase_id)
    return render_template("explorer/standings.html", standings=standings, phases=phases, seasons=seasons, selected_phase=phase_id, selected_season=season_year)
