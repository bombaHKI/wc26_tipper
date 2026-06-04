import requests
from sema import Match, Bet, User
from config import apiJson
from db import session
import sqlalchemy as sa
from datetime import datetime

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
    response = requests.get(
        apiJson["base-url"] + "/matches",
        headers=apiJson["headers"]
    )

    if response.status_code != 200:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    matches = data.get("matches", [])

    for match_data in matches:

        home_team = match_data.get("homeTeam", {}).get("id")
        away_team = match_data.get("awayTeam", {}).get("id")

        if home_team is None or away_team is None:
            continue

        match = session.get(Match, match_data["id"])

        if match is None:
            match = Match(
                match_id=match_data["id"],
                start_date=datetime.fromisoformat(
                    match_data["utcDate"].replace("Z", "+00:00")
                ),
                team_H_id=home_team,
                team_A_id=away_team,
                odds_H=1,
                odds_X=1,
                odds_A=1
            )
            session.add(match)

        else:
            match.team_H_id = home_team
            match.team_A_id = away_team
            match.start_date = datetime.fromisoformat(
                match_data["utcDate"].replace("Z", "+00:00")
            )
            
        score = match_data.get("score", {})
        score_key = "fullTime" if score.get("duration") == "REGULAR" else "regularTime"
        score_data = score.get(score_key) or {}

        home = score_data.get("home")
        away = score_data.get("away")

        was_unscored = match.goals_H is None or match.goals_A is None

        if home is not None and away is not None:
            match.goals_H = home
            match.goals_A = away

            if was_unscored:
                update_match_points(match)


        odds_data = match_data.get("odds")

        if odds_data:
            x0 = odds_data.get("homeWin")
            y0 = odds_data.get("draw")
            z0 = odds_data.get("awayWin")

            if None not in (x0, y0, z0):
                x0, y0, z0 = map(float, (x0, y0, z0))
                x1, y1, z1 = convert_odds(x0, y0, z0)

                match.odds_H = x1
                match.odds_X = y1
                match.odds_A = z1
        else:
            match.odds_H = match.odds_H or 1
            match.odds_X = match.odds_X or 1
            match.odds_A = match.odds_A or 1

    for user in User.query.all():
        user.update_points()

    try:
        session.commit()
    except sa.exc.SQLAlchemyError as e:
        session.rollback()
        print("Database error during update:", str(e))

def update_match_points(match):
    for b in match.bets:
        b.update_points()