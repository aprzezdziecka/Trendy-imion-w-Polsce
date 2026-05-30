from sqlalchemy import Column, Float, Integer, String, UniqueConstraint
from .database import Base


class NameRecord(Base):
    __tablename__ = "name_records"

    id = Column(Integer, primary_key=True, index=True)
    id_powiat = Column(String)

    wojewodztwo = Column(String)
    powiat = Column(String)

    imie_pierwsze = Column(String)

    plec = Column(String)

    liczba_wystapien = Column(Integer)

    __table_args__ = (UniqueConstraint('id_powiat', 'imie_pierwsze', 'plec', name='_name_year_uc'),)

class GUSRecord(Base):
    __tablename__ = "gus_records"

    id = Column(Integer, primary_key=True, index=True)
    id_powiat = Column(String)
    nazwa = Column(String)
    rok = Column(Integer)
    ludnosc = Column(Integer)
    wskaznik_urbanizacji = Column(Float)

    __table_args__ = (UniqueConstraint('id_powiat', 'rok', name='_powiat_year_uc'),)
