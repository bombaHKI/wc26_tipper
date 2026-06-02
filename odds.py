import requests
from sema import Match, Bet, User
from config import apiJson
from db import session
import sqlalchemy as sa

TOTAL_SUM_GOAL = 16
EXTRA_PTS_APPROX = 1.2

def check_sum(x, y, z):
    return abs(x+y+z-TOTAL_SUM_GOAL) <= 1

def fit_1_10(x, y, z):
    x = max(x, 1)
    z = min(z, 10)
    if not check_sum(x, y, z):
        if abs(y-5) < abs(y-6):
            y = 5
        else:
            y = 6
    return x, y, z

def convert_odds(a0, b0, c0):
    s = a0 + b0 + c0
    mult = (TOTAL_SUM_GOAL + 3 * EXTRA_PTS_APPROX) / s
    a = round(a0 * mult - EXTRA_PTS_APPROX)
    b = round(b0 * mult - EXTRA_PTS_APPROX)
    c = round(c0 * mult - EXTRA_PTS_APPROX)
    if a < 2 or c > 9:
        a, b, c = fit_1_10(a, b, c)
    if c < 2 or a > 9:
        c, b, a = fit_1_10(c, b, a)
    if not check_sum(a, b, c):
        raise Exception(f'{a}+{b}+{c}={a+b+c} is not allowed.')
    return a, b, c

def update_matches():
    response = requests.get(apiJson["base-url"]+"/matches", headers=apiJson["headers"])
    if response.status_code == 200:
        data = response.json()
        matches = data.get("matches", [])
        for match_data in matches:

            match = session.get(Match, match_data["id"])
            match.team_H_id = match_data["homeTeam"]["id"]
            match.team_A_id = match_data["awayTeam"]["id"]

            scoreKey = "fullTime"
            if match_data["score"]["duration"] != "REGULAR":
                scoreKey = "regularTime"

            no_score = None in (match.goals_A, match.goals_H)

            match.goals_H = match_data["score"][scoreKey]["home"]
            match.goals_A = match_data["score"][scoreKey]["away"]
            
            if None not in (match.team_H_id, match.team_A_id):
                try:
                    x0 = match_data["odds"]["homeWin"]
                    y0 = match_data["odds"]["draw"]
                    z0 = match_data["odds"]["awayWin"]
                    if None not in (x0,y0,z0):
                        x0 = float(x0)
                        y0 = float(y0)
                        z0 = float(z0)
                        x1, y1, z1 = convert_odds(x0,y0,z0)
                        
                        match.odds_H = x1
                        match.odds_X = y1
                        match.odds_A = z1
                except KeyError:
                    print("\n\nNincs odds package!!!\n\n")

                if no_score and None not in (match.goals_A, match.goals_H):
                    update_points(match)
        
        for user in User.query.all():
            user.update_points()

        try:
            session.commit()
        except sa.exc.SQLAlchemyError:
            session.rollback()
            error = "\n\nHiba az adatbázisba íráskor!\n\n"
            print(error)
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        print(response.json())

def update_points(Match):
    for b in Match.bets:
        b.update_points()