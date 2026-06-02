import json
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, timezone
import os
import requests
from config import apiJson, adminUser
from sema import Base, Team, User, Candidate, Match

db_path = os.path.join(os.path.dirname(__file__), 'data/adatok.sqlite')
engine = sa.create_engine('sqlite:///' + db_path)
session = scoped_session(sessionmaker(autocommit=False,
                                    autoflush=False,
                                    bind=engine))
Base.query = session.query_property()

def read_teams():
    txt_path = os.path.join(os.path.dirname(__file__), 'data/id_csapat.txt')
    teams = []
    with open(txt_path, 'r', encoding='utf-8') as file:
        for line in file:
            team_id, name = line.strip().split(',')
            teams.append({"team_id": int(team_id), "name": name})
    return teams

def init_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    for team in read_teams():
        session.add(Team(name=team["name"],
                        team_id=team["team_id"]))

    response = requests.get(apiJson["base-url"]+"/matches", headers=apiJson["headers"])
    if response.status_code == 200:
        data = response.json()
        matches = data.get("matches", [])
        for match in matches:
            new_match = Match(
                match_id = match["id"],
                team_H_id = match["homeTeam"]["id"],
                team_A_id = match["awayTeam"]["id"],
                start_date = datetime.fromisoformat(match["utcDate"]),
                odds_H = match["odds"]["homeWin"],
                odds_X = match["odds"]["draw"],
                odds_A = match["odds"]["awayWin"],
                goals_H = match["score"]["regularTime"]["home"],
                goals_A = match["score"]["regularTime"]["away"]
            )
            session.add(new_match)
        session.commit()
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        print(response.json())
        
    admin = User(name=adminUser["name"],
                 email=adminUser["email"],
                 is_admin=True)
    user = User(name="Guest",
                 email="guest@guest.com")
    admin.set_password(adminUser["password"])
    user.set_password("guest")
    session.add(admin)
    session.add(user)

    for i in range(20):
        session.add(Candidate(name=("Kada"+str(i)),email=str(i)+"@asd.com"))
    session.commit()

