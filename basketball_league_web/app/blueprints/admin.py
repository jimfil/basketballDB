import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, abort, flash
from flask_login import login_required
from app import db
from model import get_seasons, get_phases_by_season, get_rounds_by_phase, get_teams, create_match as create_match_model, create_player


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def before_request():
    pass

@admin_bp.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/create/team', methods=['GET', 'POST'])
def create_team():
    if request.method == 'POST':
        name = request.form['name']
        
        db_conn = db.get_db()
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO Team (name) VALUES (%s)", (name,))
        db_conn.commit()
        cursor.close()
        
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_team.html')


@admin_bp.route('/match/<int:id>/scorer')
def match_scorer(id):
    db_conn = db.get_db()
    cursor = db_conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.*, ht.name as home_team_name, at.name as away_team_name
        FROM `Match` m
        JOIN Team ht ON m.home_team_id = ht.id
        JOIN Team at ON m.away_team_id = at.id
        WHERE m.id = %s
    """, (id,))
    match = cursor.fetchone()

    if not match:
        abort(404)

    cursor.execute("""
        SELECT p.id, p.first_name, p.last_name, pt.shirt_num
        FROM Person p
        JOIN Person_Team pt ON p.id = pt.person_id
        WHERE pt.team_id = %s AND p.speciality = 'Player'
    """, (match['home_team_id'],))
    home_players = cursor.fetchall()

    cursor.execute("""
        SELECT p.id, p.first_name, p.last_name, pt.shirt_num
        FROM Person p
        JOIN Person_Team pt ON p.id = pt.person_id
        WHERE pt.team_id = %s AND p.speciality = 'Player'
    """, (match['away_team_id'],))
    away_players = cursor.fetchall()

    cursor.close()

    return render_template('admin/match_scorer.html', match=match, home_players=home_players, away_players=away_players)

@admin_bp.route('/api/event/add', methods=['POST'])
def add_event():
    data = request.get_json()
    match_id = data.get('match_id')
    player_id = data.get('player_id')
    event_type = data.get('event_type')
    
    if not all([match_id, player_id, event_type]):
        return jsonify({'error': 'Missing data'}), 400

    event_map = {
        '2pt': '2-Point Field Goal Made',
        '3pt': '3-Point Field Goal Made',
        'foul': 'Personal Foul'
    }

    event_name = event_map.get(event_type)
    if not event_name:
        return jsonify({'error': 'Invalid event type'}), 400

    db_conn = db.get_db()
    cursor = db_conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM Event WHERE name = %s", (event_name,))
    event = cursor.fetchone()
    if not event:
        cursor.close()
        return jsonify({'error': 'Event type not found in database'}), 400
    
    event_id = event['id']

    cursor.execute(
        "INSERT INTO Event_Creation (match_id, person_id, event_id) VALUES (%s, %s, %s)",
        (match_id, player_id, event_id)
    )
    db_conn.commit()
    new_event_id = cursor.lastrowid
    cursor.close()

    return jsonify({'success': True, 'event_id': new_event_id}), 201

@admin_bp.route('/create/match', methods=['GET', 'POST'])
def create_match():
    if request.method == 'POST':
        session['year'] = request.form['year']
        return redirect(url_for('admin.create_match_step2'))
    
    seasons = get_seasons()
    return render_template('admin/create_match_step1.html', seasons=seasons)

@admin_bp.route('/create/match/step2', methods=['GET', 'POST'])
def create_match_step2():
    if 'year' not in session:
        return redirect(url_for('admin.create_match'))

    if request.method == 'POST':
        session['phase_id'] = request.form['phase_id']
        return redirect(url_for('admin.create_match_step3'))

    phases = get_phases_by_season(session['year'])
    return render_template('admin/create_match_step2.html', phases=phases)

@admin_bp.route('/create/match/step3', methods=['GET', 'POST'])
def create_match_step3():
    if 'phase_id' not in session:
        return redirect(url_for('admin.create_match_step2'))

    if request.method == 'POST':
        session['round_id'] = request.form['round_id']
        return redirect(url_for('admin.create_match_step4'))

    rounds = get_rounds_by_phase(session['phase_id'])
    return render_template('admin/create_match_step3.html', rounds=rounds)

@admin_bp.route('/create/match/step4', methods=['GET', 'POST'])
def create_match_step4():
    if 'round_id' not in session:
        return redirect(url_for('admin.create_match_step3'))

    if request.method == 'POST':
        from datetime import datetime
        match_date_str = request.form['match_date']
        match_date_obj = datetime.strptime(match_date_str, '%Y-%m-%d').date()
        status = 'Scheduled' if match_date_obj > datetime.now().date() else 'Completed'
        
        match_data = {
            'home_team_id': request.form['home_team_id'],
            'away_team_id': request.form['away_team_id'],
            'round_id': session['round_id'],
            'match_date': match_date_str,
            'status': status
        }
        
        if create_match_model(match_data):
            flash('Match created successfully!', 'success')
        else:
            flash('Error creating match.', 'danger')
            
        session.pop('year', None)
        session.pop('phase_id', None)
        session.pop('round_id', None)
        
        return redirect(url_for('admin.dashboard'))

    teams = get_teams(limit=100)
    return render_template('admin/create_match_step4.html', teams=teams)

@admin_bp.route('/create/player', methods=['GET', 'POST'])
def create_player_step1():
    if request.method == 'POST':
        session['team_id'] = request.form['team_id']
        return redirect(url_for('admin.create_player_step2'))
    
    teams = get_teams(limit=100)
    return render_template('admin/create_player_step1.html', teams=teams)

@admin_bp.route('/create/player/step2', methods=['GET', 'POST'])
def create_player_step2():
    if 'team_id' not in session:
        return redirect(url_for('admin.create_player_step1'))

    if request.method == 'POST':
        player_data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'shirt_num': request.form['shirt_num'],
            'team_id': session['team_id'],
            'speciality': 'Player'
        }
        
        if create_player(player_data):
            flash('Player created successfully!', 'success')
        else:
            flash('Error creating player.', 'danger')
            
        session.pop('team_id', None)
        
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/create_player_step2.html')
