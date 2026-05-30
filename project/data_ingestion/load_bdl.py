import requests
from backend.database import SessionLocal, engine
from backend.models import Base, PopulationRecord

Base.metadata.create_all(bind=engine)

url = "https://bdl.stat.gov.pl/api/v1/data/by-variable/72305"

params = {
    "unit-level": 5,
    "year": 2024,
    "page-size": 20,
    "format": "json"
}
teryt_pos = [2, 3, 7, 8]

db = SessionLocal()
try:
    while url:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "results" not in data:
            break

        for res in data["results"]:
            clean_id = "".join([res["id"][i] for i in teryt_pos])
            
            existing = db.query(PopulationRecord).filter_by(id_powiat=str(clean_id), rok=res["values"][0]["year"]).first()
            
            if existing:
                existing.ludnosc = res["values"][0]["val"]
            else:
                new_rec = PopulationRecord(
                    id_powiat = str(clean_id), # 4 cyfrowe id powiatu          
                    nazwa=res["name"],
                    rok=int(res["values"][0]["year"]),
                    ludnosc=int(res["values"][0]["val"])
                )
                db.add(new_rec)
        
        db.commit() 
        
        url = data.get("links", {}).get("next")
        params = {} 

    print("Populacja powiatów 2024 załadowana do PostgreSQL")

except Exception as e:
    print(f"Wystąpił błąd: {e}")
    db.rollback()
finally:
    db.close()