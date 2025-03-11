import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, func
from database import Base


class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    tweet = Column(Text, nullable=False)
    policy = Column(Text, nullable=False)
    rule_id = Column(String, nullable=False)
    rule_violated = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    posted_at = Column(DateTime, nullable=False)



class ScannedUser(Base):
    __tablename__ = "scanned_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    last_scanned_at = Column(DateTime, nullable=True)
