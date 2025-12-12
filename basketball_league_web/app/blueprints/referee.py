import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from model import create_referee

referee_bp = Blueprint('referee', __name__, url_prefix='/referees')

@referee_bp.before_request
@login_required
def before_request():
    pass

@referee_bp.route('/')
def index():
    return render_template('referees/index.html')

@referee_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        if create_referee(first_name, last_name):
            flash('Referee created successfully!', 'success')
            return redirect(url_for('referee.index'))
        else:
            flash('Error creating referee.', 'danger')
    return render_template('referees/create.html')
