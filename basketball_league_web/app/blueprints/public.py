import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from flask import Blueprint, render_template, abort
from app import db
from model import get_teams, get_players, get_all_matches_with_names, get_seasons, get_phases_by_season, calculate_group_stage_standings, calculate_standings_for_phase

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    return render_template('public/index.html')

@public_bp.route('/teams')
def teams():
    all_teams = get_teams(limit=100) # Get all teams
    return render_template('public/teams.html', teams=all_teams)

@public_bp.route('/matches')
def matches():
    all_matches = get_all_matches_with_names(limit=100) # Get all matches
    return render_template('public/matches.html', matches=all_matches)

@public_bp.route('/standings')
def standings_index():
    seasons = get_seasons()
    return render_template('public/standings_index.html', seasons=seasons)

@public_bp.route('/standings/<int:year>')
def standings(year):
    phases = get_phases_by_season(year)
    group_phase = next((p for p in phases if p['phase_id'] == 1), None)
    knockout_phase = next((p for p in phases if p['phase_id'] == 2), None)

    if group_phase:
        group_standings = calculate_group_stage_standings(group_phase['id'])
    else:
        group_standings = []

    if knockout_phase:
        knockout_standings = calculate_standings_for_phase(knockout_phase['id'])
    else:
        knockout_standings = []

    return render_template(
        'public/standings.html',
        year=year,
        group_standings=group_standings,
        knockout_standings=knockout_standings,
        is_group_stage=True if group_phase else False,
        ord=ord,
        chr=chr
    )

@public_bp.route('/stats/mvp/<int:year>')
def mvp_stats(year):
    # Logic to calculate MVP would go here
    # For now, just a placeholder
    return render_template('public/mvp_stats.html', year=year)

@public_bp.route('/teams/<int:id>')
def team_roster(id):
    db_conn = db.get_db()
    cursor = db_conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM Team WHERE id = %s", (id,))
    team = cursor.fetchone()
    
    if not team:
        abort(404)

    players = get_players(id)
    
    cursor.close()
    
    return render_template('public/team_roster.html', team=team, players=players)
