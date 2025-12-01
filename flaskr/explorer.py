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
)

bp = Blueprint("explorer", __name__, url_prefix="/explorer")


def calculate_standings(phase_id):
    # 1. Get all matches in this phase
    # Note: We join with Round to filter by phase_id

    matches = get_matches_by_phase(phase_id)  # Structure: {team_id: {'wins': 0, 'losses': 0, 'points_for': 0, 'points_against': 0}}
    standings = {}

    # Helper to init team in dict
    def init_team(tid):
        if tid not in standings:
            standings[tid] = {"wins": 0, "losses": 0}

    for m in matches:
        mid, hid, aid = m["match_id"], m["home_team_id"], m["away_team_id"]
        init_team(hid)
        init_team(aid)

        # Reuse your existing get_scores function!
        scores = get_scores(mid)
        h_score = scores.get(hid, 0)
        a_score = scores.get(aid, 0)

        # Update Wins/Losses
        if h_score > a_score:
            standings[hid]["wins"] += 1
            standings[aid]["losses"] += 1
        else:
            standings[aid]["wins"] += 1
            standings[hid]["losses"] += 1

    # Fetch Team Names for display
    final_standings = []
    for tid, stats in standings.items():
        t_name = get_team_name(tid)[0]["name"]
        stats["name"] = t_name
        stats["id"] = tid
        final_standings.append(stats)

    # Sort by Wins descending
    return sorted(final_standings, key=lambda x: x["wins"], reverse=True)


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
