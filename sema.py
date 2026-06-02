from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, Table, UniqueConstraint, func
from sqlalchemy.orm import relationship, backref, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from datetime import timezone

Base = declarative_base()

Follow = Table(
    "follow", Base.metadata,
    Column('who_id', Integer, ForeignKey('user.user_id')),
    Column('whom_id', Integer, ForeignKey('user.user_id'))
)

class User(UserMixin, Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255),  nullable=False)    
    is_admin = Column(Boolean, default=False)
    points = Column(Integer, default=0)
    bets = relationship("Bet", backref=backref("user"))
    followings = relationship(
        "User",
        secondary="follow",
        primaryjoin = user_id == Follow.c.who_id,
        secondaryjoin=user_id == Follow.c.whom_id,
        backref="followers",
    )


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
           return (self.user_id)

    def update_points(self):
        self.points = sum([b.points for b in self.bets])

    def __repr__(self):
        return f'<U id: {self.user_id}; n: {self.name!r}>'

class Candidate(Base):
    __tablename__ = "candidate"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    def __repr__(self):
        return f'<U id: {self.user_id}; n: {self.name!r}>'

def points(bet_H, bet_A, match):
    if match is None:
        return 0

    points = 0
    real_diff = match.goals_H - match.goals_A
    bet_diff = bet_H - bet_A

    #meccs végkimenetelét nem találta el
    if (real_diff * bet_diff <= 0) and (bet_diff != real_diff):
        return 0
    
    if real_diff > 0:
        points += match.odds_H
    elif real_diff == 0:
        points += match.odds_X
    else:
        points += match.odds_A
    
    if (match.goals_H == bet_H) and (match.goals_A == bet_A):
        if {match.goals_H,match.goals_A} in [{1,0}, {2,0}, {1,1}, {2,1}]:
            points += 3
        elif {match.goals_H,match.goals_A} in [{0,0}, {3,0}, {3,1}, {2,2}]:
            points += 5
        else:
            points += 7
    elif (real_diff == 0):
        if match.goals_H in [bet_H+1, bet_H-1]:
            points += 1
    elif (real_diff == bet_diff) \
        or (match.goals_H == bet_H) \
        or (match.goals_A == bet_A):
        points += 1

    return points

class Bet(Base):
    __tablename__ = "bet"
    bet_id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("match.match_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    bet_H = Column(Integer, nullable=False)
    bet_A = Column(Integer, nullable=False)
    points = Column(Integer, default=0)
    UniqueConstraint(user_id, match_id)

    def __repr__(self):
        return f'<B n:{self.user.name}; m:{self.match.match_id}>'
    def info_dict(self):
        if self.match.goals_A is not None:
            return {"match_id": self.match_id,
                    "bet_H": self.bet_H,
                    "bet_A": self.bet_A,
                    "points": self.points}
        else:
            return {"match_id": self.match_id,
                    "bet_H": self.bet_H,
                    "bet_A": self.bet_A}    

    def update_points(self):
        self.points = points(self.bet_H, self.bet_A, self.match)

class Match(Base):
    __tablename__ = "match"
    match_id = Column(Integer, primary_key=True)
    team_H_id = Column(Integer, ForeignKey("team.team_id"), nullable=True)
    team_A_id = Column(Integer, ForeignKey("team.team_id"), nullable=True)
    start_date = Column(DateTime(timezone=True))
    odds_H = Column(Integer)
    odds_X = Column(Integer)
    odds_A = Column(Integer)
    goals_H = Column(Integer)
    goals_A = Column(Integer)

    @hybrid_property
    def start_date_utc(self):
        return self.start_date.replace(tzinfo=timezone.utc)

    @start_date_utc.expression
    def start_date_utc(cls):
        return func.strftime('%Y-%m-%d %H:%M:%S', cls.start_date)
    
    bets = relationship("Bet", backref=backref("match"))

    team_H = relationship(
        "Team", backref=backref('matches_to'),
        foreign_keys=[team_H_id],
    )
    team_A = relationship(
        "Team", backref=backref('matches_from'),
        foreign_keys=[team_A_id],
    )
    
    def __repr__(self):
        if self.team_H_id is not None and self.team_A_id is not None:
            return f'<M: {self.team_H.name} - {self.team_A.name}; id:{self.match_id}>'
        else:
            return '<Meccs ismeretlen résztvevőkkel>'
    def info_dict(self):
        return {"id": self.match_id,
                "start_date": self.start_date,
                "team_H": self.team_H.name,
                "team_A": self.team_A.name,
                "odds_H": self.odds_H,
                "odds_X": self.odds_X,
                "odds_A": self.odds_A,
                "goals_H": self.goals_H,
                "goals_A": self.goals_A}

class Team(Base): 
    __tablename__ = "team"
    team_id = Column(Integer, primary_key=True)
    name = Column(String(100),  nullable=False)

    @property
    def matches(self):
        return self.matches_to + self.matches_from
    
    def __repr__(self):
        return f'<T: {self.name}>'