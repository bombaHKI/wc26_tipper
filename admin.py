# admin.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
import sqlalchemy as sa
from functools import wraps
from secrets import token_urlsafe
from datetime import datetime, timezone
import db
from odds import update_matches, convert_odds
from sema import User, Candidate, Bet, Follow, Match
from send_email import send_email

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin login required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    return render_template('admin/admin_header.jinja')

@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    if request.method == 'GET':
        candidates = Candidate.query.all()
        users = User.query.all()
        return render_template('admin/users.jinja',
                               candidates=candidates,
                               users=users)
    
    try:
        data = request.json
        action = data['action']
        user_data = data['userData']
        
        if not action or not user_data:
            return {"response": "Missing action or user data", "type": "error"}
        
        if action == 'addUser':
            return add_user(user_data)
        elif action == "delete-user":
            return delete_user(user_data)
        else:
            return handle_candidate(action, user_data["id"])

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return {"response": "Internal Server Error", "type": "error"}

def delete_user(user_data):
    id = user_data["id"]
    if not id:
        return {"response": "Nincs u_id!", "type": "error"}
    
    user = User.query.get(int(id))
    if not user:
        return {"response": "Ehhez az u_id-hoz nincs fiók!", "type": "error"}
    db.session.query(Follow).filter_by(whom_id=user.user_id).delete()
    db.session.query(Follow).filter_by(who_id=user.user_id).delete()
    Bet.query.filter_by(user_id=user.user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return {"response": "Fiók törölve!", "type": "message"}

def add_user(user_data):
    password = token_urlsafe(13)
    if User.query.filter(User.email == user_data["email"]).first():
        return {"response": "Email cím már létezik!", "type": "error"}

    new_user = User(
        name=user_data["name"],
        email=user_data["email"]
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    send_email(new_user, "at_new_user", password)
    return {"response": "Fiók létrehozva!", "type": "message"}

def handle_candidate(action, candidate_id):
    if not candidate_id:
        return {"response": "Missing candidate ID", "type": "error"}

    candidate = Candidate.query.get(int(candidate_id))
    if not candidate:
        return {"response": "Candidate not found", "type": "error"}
    
    if action == "accept-candidate":
        user = User(
            name=candidate.name,
            email=candidate.email
        )
        password = token_urlsafe(13)
        user.set_password(password)
        db.session.add(user)
        send_email(user, "at_new_user", password)
        message = "Jelentkező sikeresen hozzáadva!"
    elif action == "delete-candidate":
        message = "Jelentkező törölve!"
    else:
        return {"response": "Unknown action", "type": "error"}
    
    
    db.session.delete(candidate)
    db.session.commit()
    return {"response": message, "type": "message"}

@admin_bp.route('/meccsek', methods=['GET', 'POST'])
@login_required
@admin_required
def meccsek():
    now=datetime.now(timezone.utc)
    if request.method == 'GET':
        coming_matches = Match.query \
            .filter(Match.team_H_id.isnot(None)) \
            .filter(Match.team_A_id.isnot(None)) \
            .filter(Match.start_date_utc > now) \
            .order_by(Match.start_date) \
            .all()
        return render_template('admin/add_meccsek.jinja',
                                coming_matches = coming_matches)
    
    data = request.json
    if data["action"] == "update-matches":
        try:
            update_matches()
            return {"response": "Meccsek frissítése sikeres!", "type": "message"}
        except Exception as e:
            return {"response": "Valami hiba!", "type": "error", "error": e}

    elif data["action"] == "update-odds":
        error = ""
        for match_id, odds in data["odds"].items():
            try:
                m_id = int(match_id)
                odds_H = float(odds["odds_H"])
                odds_X = float(odds["odds_X"])
                odds_A = float(odds["odds_A"])
            except Exception:
                error = "Hibás bemenet!"
                break

            match = db.session.get(Match, m_id)
            if match == None:
                error = "Nem létező meccsre próbált oddsot adni!"
                break
            if match.start_date_utc < now:
                    error = "Már lezárult meccsre próbált  oddsot adni!"
                    break
            
            x1, y1, z1 = convert_odds(odds_H,odds_X,odds_A)                        
            match.odds_H = x1
            match.odds_X = y1
            match.odds_A = z1
    
        if error != "":
            db.session.rollback()
            return {'response': error}
        try:
            db.session.commit()
        except sa.exc.SQLAlchemyError as e:
            db.session.rollback()
            error = "Hiba az adatbázisba íráskor!"
            return {'response': error, "error": e}
        return {"response": "Oddsok frissítése sikeres", "type": "message"}