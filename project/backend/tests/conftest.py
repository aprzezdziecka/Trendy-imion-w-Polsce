import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import NameRecord, GUSRecord


def seed_db():
    db = SessionLocal()
    try:
        if db.query(NameRecord).count() > 0:
            return

        names = [
            NameRecord(id_powiat="0201", wojewodztwo="DOLNOŚLĄSKIE", powiat="bolesławiecki", imie_pierwsze="ANNA", plec="KOBIETA", liczba_wystapien=120),
            NameRecord(id_powiat="0201", wojewodztwo="DOLNOŚLĄSKIE", powiat="bolesławiecki", imie_pierwsze="MARIA", plec="KOBIETA", liczba_wystapien=80),
            NameRecord(id_powiat="0201", wojewodztwo="DOLNOŚLĄSKIE", powiat="bolesławiecki", imie_pierwsze="JAN", plec="MĘŻCZYZNA", liczba_wystapien=95),
            NameRecord(id_powiat="0202", wojewodztwo="DOLNOŚLĄSKIE", powiat="dzierżoniowski", imie_pierwsze="ANNA", plec="KOBIETA", liczba_wystapien=60),
            NameRecord(id_powiat="0202", wojewodztwo="DOLNOŚLĄSKIE", powiat="dzierżoniowski", imie_pierwsze="JAN", plec="MĘŻCZYZNA", liczba_wystapien=45),
        ]
        gus = [
            GUSRecord(id_powiat="0201", nazwa="bolesławiecki", rok=2024, ludnosc=85000, wskaznik_urbanizacji=62.5, wiek=41.3),
            GUSRecord(id_powiat="0202", nazwa="dzierżoniowski", rok=2024, ludnosc=100000, wskaznik_urbanizacji=75.0, wiek=43.1),
        ]
        db.add_all(names + gus)
        db.commit()
    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    seed_db()
    with TestClient(app) as c:
        yield c
