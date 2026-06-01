from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from ..database import SessionLocal
from ..models import NameRecord, GUSRecord
from ..schemas import NameRecordOut

router = APIRouter(prefix="/names", tags=["names"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[NameRecordOut])
def get_names(plec: str = None, powiat: str = None, limit: int = 100, db: Session = Depends(get_db)):
    q = db.query(NameRecord)
    if plec:
        q = q.filter(NameRecord.plec == plec)
    if powiat:
        q = q.filter(NameRecord.powiat == powiat)
    return q.limit(limit).all()

@router.get("/top", response_model=list[NameRecordOut])
def get_top_names(plec: str = None, limit: int = 10, db: Session = Depends(get_db)):
    q = db.query(NameRecord)
    if plec:
        q = q.filter(NameRecord.plec == plec)
    return q.order_by(NameRecord.liczba_wystapien.desc()).limit(limit).all()

@router.get("/search")
def search_name(imie: str, plec: str = None, db: Session = Depends(get_db)):
    q = db.query(NameRecord).filter(NameRecord.imie_pierwsze == imie.upper())
    if plec:
        q = q.filter(NameRecord.plec == plec)
    records = q.order_by(NameRecord.liczba_wystapien.desc()).all()

    if not records:
        return []

    powiat_ids = [r.id_powiat for r in records]

    gus_map = {
        g.id_powiat: g.ludnosc
        for g in db.query(GUSRecord).filter(GUSRecord.id_powiat.in_(powiat_ids)).all()
    }

    # Rangi w powiatach — window function po wszystkich imionach w tych powiatach
    subq = db.query(
        NameRecord.id_powiat,
        NameRecord.imie_pierwsze,
        NameRecord.plec,
        func.rank().over(
            partition_by=NameRecord.id_powiat,
            order_by=NameRecord.liczba_wystapien.desc()
        ).label("rank_all"),
        func.rank().over(
            partition_by=[NameRecord.id_powiat, NameRecord.plec],
            order_by=NameRecord.liczba_wystapien.desc()
        ).label("rank_plec"),
    ).filter(NameRecord.id_powiat.in_(powiat_ids)).subquery()

    rank_q = db.query(
        subq.c.id_powiat, subq.c.plec, subq.c.rank_all, subq.c.rank_plec
    ).filter(subq.c.imie_pierwsze == imie.upper())
    if plec:
        rank_q = rank_q.filter(subq.c.plec == plec)
    pow_rank_map = {
        (r.id_powiat, r.plec): (int(r.rank_all), int(r.rank_plec))
        for r in rank_q.all()
    }

    # Rangi w województwach — agregacja + window function
    woj_rank_rows = db.execute(text("""
        WITH woj_totals AS (
            SELECT SUBSTRING(id_powiat, 1, 2) AS woj_kod,
                   imie_pierwsze, plec,
                   SUM(liczba_wystapien) AS total
            FROM name_records
            GROUP BY SUBSTRING(id_powiat, 1, 2), imie_pierwsze, plec
        ),
        ranked AS (
            SELECT woj_kod, imie_pierwsze, plec,
                   RANK() OVER (PARTITION BY woj_kod ORDER BY total DESC) AS rank_all,
                   RANK() OVER (PARTITION BY woj_kod, plec ORDER BY total DESC) AS rank_plec
            FROM woj_totals
        )
        SELECT woj_kod, plec, rank_all, rank_plec
        FROM ranked
        WHERE imie_pierwsze = :imie AND (:plec IS NULL OR plec = :plec)
    """), {"imie": imie.upper(), "plec": plec}).fetchall()

    woj_rank_map = {
        (r.woj_kod, r.plec): (int(r.rank_all), int(r.rank_plec))
        for r in woj_rank_rows
    }

    result = []
    for r in records:
        pow_rank_all, pow_rank_plec = pow_rank_map.get((r.id_powiat, r.plec), (None, None))
        woj_kod = r.id_powiat[:2]
        woj_rank_all, woj_rank_plec = woj_rank_map.get((woj_kod, r.plec), (None, None))
        result.append({
            "id_powiat": r.id_powiat,
            "wojewodztwo": r.wojewodztwo,
            "powiat": r.powiat,
            "imie_pierwsze": r.imie_pierwsze,
            "plec": r.plec,
            "liczba_wystapien": r.liczba_wystapien,
            "ludnosc": gus_map.get(r.id_powiat),
            "rank_pow_all": pow_rank_all,
            "rank_pow_plec": pow_rank_plec,
            "rank_woj_all": woj_rank_all,
            "rank_woj_plec": woj_rank_plec,
        })
    return result

@router.get("/regions")
def get_regions(db: Session = Depends(get_db)):
    rows = db.query(
        NameRecord.id_powiat,
        NameRecord.powiat,
        NameRecord.wojewodztwo
    ).distinct().order_by(NameRecord.wojewodztwo, NameRecord.powiat).all()

    result = {}
    for r in rows:
        woj_kod = r.id_powiat[:2]
        if woj_kod not in result:
            result[woj_kod] = {"nazwa": r.wojewodztwo.title(), "powiaty": []}
        result[woj_kod]["powiaty"].append({"id": r.id_powiat, "nazwa": r.powiat.title()})
    return result


@router.get("/regional-top")
def regional_top(level: str, id: str, limit: int = 5, db: Session = Depends(get_db)):
    q = db.query(
        NameRecord.imie_pierwsze,
        NameRecord.plec,
        func.sum(NameRecord.liczba_wystapien).label("total")
    )
    if level == "powiat":
        q = q.filter(NameRecord.id_powiat == id)
    else:
        q = q.filter(NameRecord.id_powiat.like(f"{id}%"))
    rows = q.group_by(NameRecord.imie_pierwsze, NameRecord.plec).all()

    imie_map = {}
    for r in rows:
        imie_map[r.imie_pierwsze] = imie_map.get(r.imie_pierwsze, 0) + int(r.total)

    total_births = sum(imie_map.values())
    unique_names = len(imie_map)
    diversity = round(unique_names / total_births * 1000, 1) if total_births > 0 else 0

    # Rangi krajowe
    nat_rows = db.query(
        NameRecord.imie_pierwsze,
        func.sum(NameRecord.liczba_wystapien).label("total")
    ).group_by(NameRecord.imie_pierwsze).all()
    nat_map = {r.imie_pierwsze: int(r.total) for r in nat_rows}
    nat_rank_map = {
        name: i + 1
        for i, (name, _) in enumerate(sorted(nat_map.items(), key=lambda x: -x[1]))
    }

    sorted_all = sorted(imie_map.items(), key=lambda x: -x[1])
    reg_rank_map = {name: i + 1 for i, (name, _) in enumerate(sorted_all)}

    def with_rank(name, liczba):
        rk = nat_rank_map.get(name)
        diff = (reg_rank_map[name] - rk) if rk else None
        return {"imie": name, "liczba": liczba, "rank_krajowy": rk, "diff": diff}

    top_all = [with_rank(k, v) for k, v in sorted_all[:limit]]
    top_k = [with_rank(r.imie_pierwsze, int(r.total))
              for r in sorted(rows, key=lambda r: -r.total) if r.plec == "KOBIETA"][:limit]
    top_m = [with_rank(r.imie_pierwsze, int(r.total))
              for r in sorted(rows, key=lambda r: -r.total) if r.plec == "MĘŻCZYZNA"][:limit]

    # Imiona charakterystyczne dla regionu (>= 20% polskich nadań tu)
    characteristic = sorted([
        {"imie": name, "liczba": count,
         "pct_krajowe": round(count / nat_map[name] * 100, 1)}
        for name, count in imie_map.items()
        if nat_map.get(name, 0) > 0 and count > 3
        and count / nat_map[name] >= 0.20
    ], key=lambda x: -x["pct_krajowe"])[:8]

    # Dane do wykresu: top 10 z podziałem K/M
    top10_names = [k for k, _ in sorted_all[:10]]
    gender_map = {}
    for r in rows:
        if r.imie_pierwsze in top10_names:
            gm = gender_map.setdefault(r.imie_pierwsze, {"k": 0, "m": 0})
            if r.plec == "KOBIETA":
                gm["k"] = int(r.total)
            elif r.plec == "MĘŻCZYZNA":
                gm["m"] = int(r.total)
    chart_data = [
        {"imie": name, "k": gender_map.get(name, {}).get("k", 0),
         "m": gender_map.get(name, {}).get("m", 0)}
        for name in top10_names
    ]

    return {
        "total_births": total_births,
        "unique_names": unique_names,
        "diversity_per_1000": diversity,
        "top_all": top_all,
        "top_kobiety": top_k,
        "top_mezczyzni": top_m,
        "characteristic": characteristic,
        "chart_data": chart_data,
    }


@router.get("/stats")
def name_stats(imie: str, plec: str = None, db: Session = Depends(get_db)):
    q = db.query(NameRecord).filter(NameRecord.imie_pierwsze == imie.upper())
    if plec:
        q = q.filter(NameRecord.plec == plec)
    records = q.all()

    if not records:
        return {"error": "Nie znaleziono imienia"}

    total = sum(r.liczba_wystapien for r in records)
    top3 = sorted(records, key=lambda r: r.liczba_wystapien, reverse=True)[:3]

    powiat_ids = [r.id_powiat for r in records]
    gus = db.query(GUSRecord).filter(GUSRecord.id_powiat.in_(powiat_ids)).all()
    gus_map = {g.id_powiat: g for g in gus}

    urbanizacja = [
        gus_map[r.id_powiat].wskaznik_urbanizacji
        for r in records
        if r.id_powiat in gus_map and gus_map[r.id_powiat].wskaznik_urbanizacji is not None
    ]
    avg_urban = round(sum(urbanizacja) / len(urbanizacja), 1) if urbanizacja else None

    liczba_wojewodztw = len({r.id_powiat[:2] for r in records})

    plec_split = {}
    for r in records:
        plec_split[r.plec] = plec_split.get(r.plec, 0) + r.liczba_wystapien

    krajowa_srednia = db.query(func.avg(GUSRecord.wskaznik_urbanizacji)).scalar()
    krajowa_srednia = round(float(krajowa_srednia), 1) if krajowa_srednia else None

    return {
        "imie": imie.upper(),
        "total": total,
        "liczba_powiatow": len(records),
        "liczba_wojewodztw": liczba_wojewodztw,
        "plec_split": plec_split,
        "top3": [{"powiat": r.powiat, "wojewodztwo": r.wojewodztwo, "liczba": r.liczba_wystapien} for r in top3],
        "avg_wskaznik_urbanizacji": avg_urban,
        "krajowa_srednia_urbanizacji": krajowa_srednia,
    }
