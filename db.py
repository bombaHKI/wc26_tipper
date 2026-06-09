import json
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, timezone
import os
import requests
from config import apiJson, adminUser
from sema import Base, Team, User, Match

db_path = os.path.join(os.path.dirname(__file__), 'data/adatok.sqlite')
engine = sa.create_engine('sqlite:///' + db_path)
session = scoped_session(sessionmaker(autocommit=False,
                                    autoflush=False,
                                    bind=engine))
Base.query = session.query_property()

def init_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    response = requests.get(apiJson["base-url"]+"/teams", headers=apiJson["headers"])
    if response.status_code == 200:
        data = response.json()
        teams = data.get("teams", [])
        for team in teams:
            new_team = Team(
                team_id=team["id"],
                name=team["name"]
            )
            session.add(new_team)
        session.commit()
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        print(response.json())
        
    admin = User(name=adminUser["name"],
                 is_admin=True)
    admin.set_password(adminUser["password"])
    session.add(admin)

    session.commit()

