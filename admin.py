# admin.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
import sqlalchemy as sa
from functools import wraps
from secrets import token_urlsafe
from datetime import datetime, timezone
import db
from odds import update_matches, convert_odds, update_all_points
from sema import User, Bet, Follow, Match

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
    return redirect(url_for('admin.meccsek'))

@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    if request.method == 'GET':
        users = User.query.all()
        return render_template('admin/users.jinja',
                               users=users)
    
    try:
        data = request.json
        action = data['action']
        user_data = data['userData']
        
        if not action or not user_data:
            return {"response": "Missing action or user data", "type": "error"}
        
        if action == "delete-user":
            return delete_user(user_data)

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

@admin_bp.route('/meccsek', methods=['GET', 'POST'])
@login_required
@admin_required
def meccsek():
    now = datetime.now(timezone.utc)

    if request.method == 'GET':
        coming_matches = Match.query \
            .filter(Match.team_H_id.isnot(None)) \
            .filter(Match.team_A_id.isnot(None)) \
            .filter(Match.start_date_utc > now) \
            .order_by(Match.start_date) \
            .all()

        return render_template(
            'admin/add_meccsek.jinja',
            coming_matches=coming_matches
        )

    data = request.json

    if data["action"] == "update-matches":
        try:
            update_matches()
            return {
                "response": "Meccsek frissítése sikeres!",
                "type": "message"
            }

        except Exception as e:
            import traceback
            traceback.print_exc()

            return {
                "response": f"Valami hiba történt: {str(e)}",
                "type": "error"
            }
    elif data["action"] == "update-all-points":
        try:
            update_all_points()
            return {
                "response": "Pontok frissítése sikeres!",
                "type": "message"
            }

        except Exception as e:
            import traceback
            traceback.print_exc()

            return {
                "response": f"Valami hiba történt: {str(e)}",
                "type": "error"
            }

    elif data["action"] == "update-odds":
        error = ""

        for match_id, odds in data["odds"].items():
            try:
                m_id = int(match_id)
                odds_H = float(odds["odds_H"])
                odds_X = float(odds["odds_X"])
                odds_A = float(odds["odds_A"])
            except Exception:
                error = "Hibás odds bemenet!"
                break

            match = db.session.get(Match, m_id)

            if match is None:
                error = "Nem létező meccsre próbált oddsot adni!"
                break

            if match.start_date_utc < now:
                error = "Már lezárult meccsre próbált oddsot adni!"
                break

            x1, y1, z1 = convert_odds(odds_H, odds_X, odds_A)

            match.odds_H = x1
            match.odds_X = y1
            match.odds_A = z1

        if error:
            db.session.rollback()
            return {"response": error, "type": "error"}

        try:
            db.session.commit()
        except sa.exc.SQLAlchemyError as e:
            db.session.rollback()

            return {
                "response": "Hiba az adatbázisba íráskor!",
                "type": "error",
                "error": str(e)
            }

        return {
            "response": "Oddsok frissítése sikeres",
            "type": "message"
        }

    return {
        "response": "Ismeretlen művelet",
        "type": "error"
    }
