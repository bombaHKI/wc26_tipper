from flask import Flask, request, render_template, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import sqlalchemy as sa
from datetime import datetime, timezone
from unidecode import unidecode
from sema import User, Candidate, Match, Bet, points
from db import session
from send_email import send_email
from config import appConfigJson
from admin import admin_bp

def create_app():
   app = Flask(__name__)
   app.config["SECRET_KEY"] = appConfigJson["SECRET_KEY"]

   login_manager = LoginManager()
   login_manager.login_view = "login"
   login_manager.init_app(app)

   app.register_blueprint(admin_bp)

   @login_manager.user_loader
   def load_user(user_id):
      return session.get(User, int(user_id))

   return app
app = create_app()

def img_url_from_name(str):
   return url_for('static', filename=f'media/csapatok/{unidecode(str).lower().replace(" ","_")}.svg')

app.jinja_env.filters["img_url_from_name"] = img_url_from_name
app.jinja_env.globals.update(points=points) 

@app.route("/")
@login_required
def index():
   return render_template("alap_header.jinja")

@app.route("/login", methods=["GET","POST"])
def login():
   if request.method == "GET":
      return render_template("login.jinja")

   error = None
   message = None
   formJSON = request.json
   email = formJSON["email"].strip()
   if formJSON["action"] == "login":
      user = User.query.filter(User.email == email).first()
      if user == None or \
         not user.check_password(formJSON["password"]):
         error = "Jelszó vagy email nem stimmelt!"
      else:
         login_user(user)
         return {
            "url": url_for("index",_external=True), 
            "type": "message" 
         }
   elif formJSON["action"] == "signup":
      name =  formJSON["username"].strip()
      if User.query.filter(User.email == email).first() != None:
         error = "Ezzel az e-amil címmel már létezik fiók!"
      elif Candidate.query.filter(Candidate.email == email).first() != None:
         error = "Ezzel az e-amil címmel már jelentkeztek!"
      else:
         candidate = Candidate(name=name, email=email)
         session.add(candidate)
         session.commit()
         message = "Sikeres jelentkezés!"
         send_email(candidate,"at_signup")
   if error != None:
      return {"response": error, "type": "error"}
   else:
      return {"response": message, "type": "message"}

@app.route("/szabalyok")
@login_required
def szabalyok():
   return render_template("szabalyok.jinja")

@app.route("/meccsek", methods=["GET","POST"])
@login_required
def meccsek():
   now=datetime.now(timezone.utc)
   if request.method == "GET":
      matches_bets = session.query(Match,Bet) \
            .outerjoin(Bet,
                        sa.and_(Bet.match_id==Match.match_id,
                                Bet.user_id==current_user.user_id))
      matches_bets = session.query(Match, Bet) \
                  .outerjoin(Bet, sa.and_(Bet.match_id == Match.match_id, 
                                          Bet.user_id == current_user.user_id)) \
                  .filter(Match.team_H_id.isnot(None)) \
                  .filter(Match.team_A_id.isnot(None)) \
                  .order_by(Match.start_date) \
                  .all()
      print(matches_bets[0][0].start_date_utc)
      return render_template("meccsek.jinja",
                             now = now,
                             matches_bets = matches_bets)
   
   betsJson = request.json
   error = ""
   for match_id, bets in betsJson.items():
      try:
         m_id = int(match_id)
         bet_H = int(bets["bet_H"])
         bet_A = int(bets["bet_A"])
      except Exception:
         error = "Hibás bemenet!"
         break

      match = session.get(Match, m_id)
      if match == None:
         error = "Nem létező meccsre próbált tippelni!"
         break
      if match.start_date_utc < now:
            error = "Már lezárult meccsre próbált tippelni!"
            break

      bet = Bet.query.filter(Bet.user_id == current_user.user_id,
                              Bet.match_id == m_id).first()
      if bet == None:
         session.add(Bet(user_id = current_user.user_id,
                        match_id = m_id,
                        bet_H = bet_H,
                        bet_A = bet_A))
      else:
         bet.bet_H = bet_H
         bet.bet_A = bet_A
   
   if error != "":
      session.rollback()
      return {'response': error}

   try:
      session.commit()
   except sa.exc.SQLAlchemyError:
      session.rollback()
      error = "Hiba az adatbázisba íráskor!"
   return {'response': error}

@app.route("/allas", methods=["GET","POST"])
@login_required
def allas():
   if request.method == "GET":
      users = User.query.order_by(User.points.desc()).all()
      ranking = {} #{ rank: [userX, userY, ...] }
      currentRank, userIdx, prevPoints = 1, 0, -1
      for u in users:
         userIdx += 1
         if u.points != prevPoints:
               currentRank = userIdx
               prevPoints = u.points
               ranking[currentRank] = []
         ranking[currentRank].append(u)      
      return render_template("allas.jinja", ranking=ranking)

   action = request.json["action"]
   uid = request.json["uid"]
   error = ""
   clickedUser = session.get(User, uid)
   if clickedUser == None or \
      (action == "follow" and clickedUser in current_user.followings) or \
      (action == "unfollow" and clickedUser not in current_user.followings):
      error = "Hibás adat!"
   else:
      try:
         if action == "follow":
            current_user.followings.append(clickedUser)
         else:
            current_user.followings.remove(clickedUser)
         session.commit()
      except sa.exc.SQLAlchemyError:
            session.rollback()
            error = "Hiba az adatbázisba íráskor!"
   return {'response': error}

@app.route("/tippek", methods=["GET"])
@login_required
def tippek_data():
   now = datetime.now(timezone.utc)

   responseDict = {} # { [matches], [ bets{id:[bets]} ] }
   matches_with_scores = Match.query.filter(
         Match.start_date_utc < now
         # Match.goals_A.isnot(None), 
         # Match.goals_H.isnot(None)
      ).order_by(Match.start_date.desc()).all()
   

   responseDict["matches"] = [
         {
            "id": m.match_id,
            "team_H": m.team_H.name,
            "team_A": m.team_A.name,
            "goals_H": m.goals_H,
            "goals_A": m.goals_A,
            "start_date": m.start_date,
            "kep_H": img_url_from_name(m.team_H.name),
            "kep_A": img_url_from_name(m.team_A.name)
         }
         for m in matches_with_scores
      ]
   print("eddig eltelt ido: ",(datetime.now(timezone.utc) - now).total_seconds(), " mp") #TODO: ez teszthez kell
  

   results = session.query(User.user_id, Bet, Match.match_id)\
                     .join(Bet, Bet.user_id == User.user_id)\
                     .join(Match, Bet.match_id == Match.match_id)\
                     .filter(
                           Match.start_date_utc < now
                           # Match.goals_A.isnot(None),
                           # Match.goals_H.isnot(None)
                     ).all()
   responseDict["all_bets"] = {}
   for user_id, bet, match_id in results:
      if user_id not in responseDict["all_bets"]:
         responseDict["all_bets"][user_id] = {}
      responseDict["all_bets"][user_id][match_id] = bet.info_dict()

   print("eddig eltelt ido: ",(datetime.now(timezone.utc) - now).total_seconds(), " mp") #TODO: ez teszthez kell    
   return responseDict

@app.route("/meccsinfo/<m_id>", methods=["GET"])
@login_required
def meccs_data(m_id):
   match = Match.query.filter(Match.match_id == m_id).first()
   if not match or None in (match.goals_H, match.goals_A):
      return {"valid": False}
   matchInfo = match.info_dict()
   matchInfo["kep_H"] = img_url_from_name(match.team_H.name)
   matchInfo["kep_A"] = img_url_from_name(match.team_A.name)
   responseDict = { "matchInfo": matchInfo }
   responseDict["maxPoint"] = points(match.goals_H,
                                    match.goals_A,
                                    match)

   avgBets = session.query(sa.func.avg(Bet.bet_H), sa.func.avg(Bet.bet_A))\
                  .filter(Bet.match_id==match.match_id)\
                  .first()
   if None in avgBets:
      avgBets = (0,0)
   responseDict["avgBets"] = list(map(lambda x: round(x,2),avgBets))

   pointDistribution = {}
   for pointGroup in session.query(Bet.points, sa.func.count(Bet.bet_id))\
                              .filter(Bet.match_id == match.match_id)\
                              .group_by(Bet.points):
      pointDistribution[pointGroup[0]] = pointGroup[1]
   responseDict["pointDistribution"] = pointDistribution
   responseDict["valid"] = True
   return responseDict

@app.route("/profil", methods=["GET","POST"])
@login_required
def profil():
   if request.method == "GET":
      return render_template("profil.jinja")

   error = None
   formJSON = request.json
   password = formJSON["password"]
   if not current_user.check_password(password):
      error = "Rossz jelszó!"
   elif formJSON["action"] == "data-change":
      current_user.name = formJSON["username"].strip()
      current_user.email =  formJSON["email"].strip()
      
   elif formJSON["action"] == "password-change":
      newPass =  formJSON["new-password"]
      confPass = formJSON["confirm-password"]
      if newPass != confPass:
         error = "Jelszó megerősítése nem egyezik!"
      else:
         current_user.set_password(newPass)

   if error == None:
      try:
         session.commit()
         send_email(current_user,"at_data_change")
         return {"response": "Sikeres módosítás!", "type": "message"}
      except:
         error = "Valami hiba történt!"
   return {"response": error, "type": "error"}

@app.route("/logout")
def logout():
   logout_user()
   return redirect(url_for("login"))

if __name__ == "__main__":
   app.run(debug=False)
