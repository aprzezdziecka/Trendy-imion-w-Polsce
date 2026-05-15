from sqlalchemy import Column, Integer, String, UniqueConstraint
from .database import Base


class NameRecord(Base):
    __tablename__ = "name_records"

    id = Column(Integer, primary_key=True, index=True)

    kt_usc = Column(Integer)

    wojewodztwo = Column(String)
    powiat = Column(String)
    gmina = Column(String)

    imie_pierwsze = Column(String)

    plec = Column(String)

    liczba_wystapien = Column(Integer)

    __table_args__ = (UniqueConstraint('kt_usc', 'imie_pierwsze', 'plec', name='_name_year_uc'),)

class PopulationRecord(Base):
    __tablename__ = "population_records"

    id = Column(Integer, primary_key=True, index=True)
    id_powiat = Column(Integer)
    nazwa = Column(String)
    rok = Column(Integer)
    ludnosc = Column(Integer)

    __table_args__ = (UniqueConstraint('id_powiat', 'rok', name='_powiat_year_uc'),)
