from sqlalchemy import Integer, String, Column, create_engine, DateTime
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime

DB_path = "warehouse.db"
engine = create_engine("sqlite:///{DB_path}")
Base = declarative_base()

class packages(Base):
    __tablename__ = "packages"
    id = Column(Integer,primary_key = True)
    name = Column(String)