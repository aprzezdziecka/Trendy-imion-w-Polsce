from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from ..database import SessionLocal
from ..models import GUSRecord, NameRecord
from ..schemas import GUSRecordOut

router = APIRouter(prefix="/gus", tags=["gus"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/",
    response_model=list[GUSRecordOut],
    summary="Lista wskaźników GUS dla powiatów",
    description=(
        "Zwraca dane z Banku Danych Lokalnych GUS dla każdego powiatu: "
        "ludność, wskaźnik urbanizacji (%) oraz mediana wieku mieszkańców."
    ),
)
def get_gus_data(db: Session = Depends(get_db)):
    return db.query(GUSRecord).all()

@router.get(
    "/analysis",
    summary="Analiza korelacji wskaźników GUS z imionami",
    description=(
        "Złożona analiza łącząca dane GUS z danymi o imionach. Zwraca: "
        "dane do scatter plotów (urbanizacja/wiek vs różnorodność imion), "
        "porównanie imion w powiatach o wysokiej/niskiej urbanizacji (kwartyle Q1/Q4), "
        "porównanie imion w regionach starszych/młodszych demograficznie, "
        "mapy choropleth (urban_map, age_map) oraz ranking województw."
    ),
)
def gus_analysis(db: Session = Depends(get_db)):
    gus_records = db.query(GUSRecord).all()

    # Różnorodność imion per powiat
    div_rows = db.query(
        NameRecord.id_powiat,
        func.count(func.distinct(NameRecord.imie_pierwsze)).label("unique_names"),
        func.sum(NameRecord.liczba_wystapien).label("total_births")
    ).group_by(NameRecord.id_powiat).all()

    diversity_map = {
        r.id_powiat: round(int(r.unique_names) / int(r.total_births) * 1000, 1)
        if r.total_births > 0 else 0
        for r in div_rows
    }

    # Dane do scatter plotów
    scatter_data = []
    for g in gus_records:
        div = diversity_map.get(g.id_powiat)
        if div is not None and g.wskaznik_urbanizacji is not None and g.wiek is not None:
            scatter_data.append({
                "id_powiat": g.id_powiat,
                "nazwa": g.nazwa,
                "urbanizacja": g.wskaznik_urbanizacji,
                "wiek": g.wiek,
                "ludnosc": g.ludnosc or 0,
                "diversity": div
            })

    # Kwartyle urbanizacji i wieku
    sorted_urban = sorted(
        [g for g in gus_records if g.wskaznik_urbanizacji is not None],
        key=lambda x: x.wskaznik_urbanizacji
    )
    sorted_age = sorted(
        [g for g in gus_records if g.wiek is not None],
        key=lambda x: x.wiek
    )
    n_u, n_a = len(sorted_urban), len(sorted_age)

    high_urban_ids = list({g.id_powiat for g in sorted_urban[3*n_u//4:]})
    low_urban_ids  = list({g.id_powiat for g in sorted_urban[:n_u//4]})
    old_ids        = list({g.id_powiat for g in sorted_age[3*n_a//4:]})
    young_ids      = list({g.id_powiat for g in sorted_age[:n_a//4]})

    def top_names(powiat_ids, limit=5):
        if not powiat_ids:
            return []
        rows = db.query(
            NameRecord.imie_pierwsze,
            func.sum(NameRecord.liczba_wystapien).label("total")
        ).filter(
            NameRecord.id_powiat.in_(powiat_ids)
        ).group_by(NameRecord.imie_pierwsze).order_by(
            func.sum(NameRecord.liczba_wystapien).desc()
        ).limit(limit).all()
        return [{"imie": r.imie_pierwsze, "liczba": int(r.total)} for r in rows]

    def bottom_names(powiat_ids, limit=5):
        if not powiat_ids:
            return []
        rows = db.query(
            NameRecord.imie_pierwsze,
            func.sum(NameRecord.liczba_wystapien).label("total")
        ).filter(
            NameRecord.id_powiat.in_(powiat_ids)
        ).group_by(NameRecord.imie_pierwsze).having(
            func.sum(NameRecord.liczba_wystapien) > 3
        ).order_by(
            func.sum(NameRecord.liczba_wystapien).asc()
        ).limit(limit).all()
        return [{"imie": r.imie_pierwsze, "liczba": int(r.total)} for r in rows]

    # Nazwy województw
    woj_name_map = {}
    for r in db.query(NameRecord.id_powiat, NameRecord.wojewodztwo).distinct().all():
        woj_name_map[r.id_powiat[:2]] = r.wojewodztwo.title()

    # Top imię per województwo (ogólne, żeńskie, męskie, najrzadsze)
    all_name_rows = db.query(
        NameRecord.id_powiat,
        NameRecord.imie_pierwsze,
        NameRecord.plec,
        func.sum(NameRecord.liczba_wystapien).label("total")
    ).group_by(NameRecord.id_powiat, NameRecord.imie_pierwsze, NameRecord.plec).all()

    woj_name_totals = {}
    woj_name_totals_k = {}
    woj_name_totals_m = {}
    for r in all_name_rows:
        woj = r.id_powiat[:2]
        total = int(r.total)
        woj_name_totals.setdefault(woj, {})
        woj_name_totals[woj][r.imie_pierwsze] = woj_name_totals[woj].get(r.imie_pierwsze, 0) + total
        if r.plec == "KOBIETA":
            woj_name_totals_k.setdefault(woj, {})
            woj_name_totals_k[woj][r.imie_pierwsze] = woj_name_totals_k[woj].get(r.imie_pierwsze, 0) + total
        elif r.plec == "MĘŻCZYZNA":
            woj_name_totals_m.setdefault(woj, {})
            woj_name_totals_m[woj][r.imie_pierwsze] = woj_name_totals_m[woj].get(r.imie_pierwsze, 0) + total

    woj_top_name = {
        woj: max(names.items(), key=lambda x: x[1])[0]
        for woj, names in woj_name_totals.items()
    }
    woj_top_name_k = {
        woj: max(names.items(), key=lambda x: x[1])[0]
        for woj, names in woj_name_totals_k.items()
    }
    woj_top_name_m = {
        woj: max(names.items(), key=lambda x: x[1])[0]
        for woj, names in woj_name_totals_m.items()
    }
    woj_bottom_name = {
        woj: min(
            ((name, cnt) for name, cnt in names.items() if cnt > 3),
            key=lambda x: x[1],
            default=("—", 0)
        )[0]
        for woj, names in woj_name_totals.items()
    }

    # Różnorodność per województwo
    woj_div_rows = db.execute(text("""
        SELECT SUBSTRING(id_powiat, 1, 2) AS woj,
               COUNT(DISTINCT imie_pierwsze) AS unique_names,
               SUM(liczba_wystapien) AS total
        FROM name_records
        GROUP BY SUBSTRING(id_powiat, 1, 2)
    """)).fetchall()

    woj_diversity_map = {
        r.woj: round(int(r.unique_names) / int(r.total) * 1000, 1) if r.total else 0
        for r in woj_div_rows
    }

    # Agregacja GUS per województwo
    woj_gus = {}
    for g in gus_records:
        woj = g.id_powiat[:2]
        woj_gus.setdefault(woj, {"urbanizacja": [], "wiek": [], "ludnosc": 0})
        if g.wskaznik_urbanizacji is not None:
            woj_gus[woj]["urbanizacja"].append(g.wskaznik_urbanizacji)
        if g.wiek is not None:
            woj_gus[woj]["wiek"].append(g.wiek)
        woj_gus[woj]["ludnosc"] += (g.ludnosc or 0)

    woj_ranking = []
    for woj, data in woj_gus.items():
        if data["urbanizacja"] and data["wiek"]:
            woj_ranking.append({
                "woj_kod": woj,
                "nazwa": woj_name_map.get(woj, woj),
                "avg_urbanizacja": round(sum(data["urbanizacja"]) / len(data["urbanizacja"]), 1),
                "avg_wiek": round(sum(data["wiek"]) / len(data["wiek"]), 1),
                "ludnosc": data["ludnosc"],
                "diversity": woj_diversity_map.get(woj, 0),
                "top_imie": woj_top_name.get(woj, "—"),
                "top_imie_k": woj_top_name_k.get(woj, "—"),
                "top_imie_m": woj_top_name_m.get(woj, "—"),
                "bottom_imie": woj_bottom_name.get(woj, "—"),
            })

    woj_ranking.sort(key=lambda x: -x["avg_urbanizacja"])

    return {
        "scatter_data": scatter_data,
        "urban_top": top_names(high_urban_ids),
        "urban_bottom": bottom_names(high_urban_ids),
        "rural_top": top_names(low_urban_ids),
        "rural_bottom": bottom_names(low_urban_ids),
        "young_top": top_names(young_ids),
        "young_bottom": bottom_names(young_ids),
        "old_top": top_names(old_ids),
        "old_bottom": bottom_names(old_ids),
        "woj_ranking": woj_ranking,
        "urban_map": {g.id_powiat: g.wskaznik_urbanizacji for g in gus_records if g.wskaznik_urbanizacji is not None},
        "age_map": {g.id_powiat: g.wiek for g in gus_records if g.wiek is not None},
    }
