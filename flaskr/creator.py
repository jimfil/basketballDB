from flask import Blueprint, render_template, request, redirect, url_for
from .auth import login_required
from basketballDB.model import (
    create_season, create_team, create_player, get_person_attributes, get_teams,
    return_attributes, create_entry, get_seasons, get_persons, get_phases,
    get_rounds, get_stadiums
)

# ... (imports and blueprint definition)

# ... (existing routes)

@bp.route("/match", methods=("GET", "POST"))
@login_required
def create_match():
    """Create a new match."""
    if request.method == "POST":
        values = [request.form[attr] for attr in return_attributes('match') if attr != 'id']
        create_entry('match', values)
        return redirect(url_for("creator.index"))

    rounds = get_rounds()
    stadiums = get_stadiums()
    teams = get_teams(limit=0)
    return render_template("creator/create_match.html", rounds=rounds, stadiums=stadiums, teams=teams)

@bp.route("/team_stadium", methods=("GET", "POST"))
@login_required
def create_team_stadium():
    """Create a new team-stadium association."""
    if request.method == "POST":
        values = [request.form[attr] for attr in return_attributes('team_stadium') if attr != 'id']
        create_entry('team_stadium', values)
        return redirect(url_for("creator.index"))

    teams = get_teams(limit=0)
    stadiums = get_stadiums()
    rounds = get_rounds()
    return render_template("creator/create_team_stadium.html", teams=teams, stadiums=stadiums, rounds=rounds)

@bp.route("/create/<string:table_name>", methods=("GET", "POST"))
@login_required
def create_entity(table_name):
    """Create a new entry for a given table."""
    # ... (existing code)
