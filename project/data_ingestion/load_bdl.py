import requests
from backend.database import SessionLocal, engine
from backend.models import Base, GUSRecord
import time

Base.metadata.create_all(bind=engine)

url_lud = "https://bdl.stat.gov.pl/api/v1/data/by-variable/72305"

params_ludnosc = {
    "unit-level": 5,
    "year": 2024,
    "page-size": 20,
    "format": "json"
}

params_urbanizacja = {
    "unit-level": 5,
    "year": 2024,
    "page-size": 20,
    "format": "json"
}

url_urbanizacja = "https://bdl.stat.gov.pl/api/v1/data/by-variable/1725015"


teryt_pos = [2, 3, 7, 8]

db = SessionLocal()
try:
    while url_lud:
        response = requests.get(url_lud, params=params_ludnosc)
        time.sleep(0.5)
        response.raise_for_status()
        data = response.json()
        
        if "results" not in data:
            break

        for res in data["results"]:
            clean_id = "".join([res["id"][i] for i in teryt_pos])
            
            existing = db.query(GUSRecord).filter_by(id_powiat=str(clean_id), rok=res["values"][0]["year"]).first()
            
            if existing:
                existing.ludnosc = res["values"][0]["val"]
            else:
                new_rec = GUSRecord(
                    id_powiat = str(clean_id), # 4 cyfrowe id powiatu          
                    nazwa=res["name"],
                    rok=int(res["values"][0]["year"]),
                    ludnosc=int(res["values"][0]["val"])
                )
                db.add(new_rec)
        
        db.commit() 
        
        url_lud = data.get("links", {}).get("next")
        params_ludnosc = {} 

    print("Populacja powiatów 2024 załadowana do PostgreSQL")

    while url_urbanizacja:
        response = requests.get(url_urbanizacja, params=params_urbanizacja)
        time.sleep(0.5)
        response.raise_for_status()
        data = response.json()

        if "results" not in data:
            break

        for res in data["results"]:
            clean_id = "".join([res["id"][i] for i in teryt_pos])

            existing = (
                db.query(GUSRecord)
                .filter_by(
                    id_powiat=str(clean_id),
                    rok=int(res["values"][0]["year"])
                )
                .first()
            )

            if existing:
                existing.wskaznik_urbanizacji = float(
                    res["values"][0]["val"]
                )

        db.commit()

        url_urbanizacja = data.get("links", {}).get("next")
        params_urbanizacja = {}

    print("Wskaźnik urbanizacji załadowany do PostgreSQL")

except Exception as e:
    print(f"Wystąpił błąd: {e}")
    db.rollback()
finally:
    db.close()

