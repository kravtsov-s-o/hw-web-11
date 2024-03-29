from sqlalchemy import Column, Integer, String, Date, func, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(length=50), nullable=False)
    last_name = Column(String(length=50), nullable=False)
    email = Column(String(length=255), nullable=False)
    phone = Column(String(length=20), nullable=False)
    birthday = Column(Date, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column('created_at', DateTime, default=func.now())
