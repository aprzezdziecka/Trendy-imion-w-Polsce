from sqlalchemy import Column, Integer, String
from database import Base


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