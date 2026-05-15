import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pandas as pd

from backend.database import SessionLocal
from backend.models import NameRecord


df = pd.read_csv(
    "data/Wykaz_imion_pierwszych_nadanych_dzieciom_w_Polsce_w_2024_wg_USC.csv",
    sep=","
)

print(df.columns)

db = SessionLocal()

for _, row in df.iterrows():

    existing = db.query(NameRecord).filter_by(
        kt_usc=int(row["KT_USC"]),
        wojewodztwo=row["WOJEWÓDZTWO"],
        powiat=row["POWIAT"],
        gmina=row["GMINA"],
        imie_pierwsze=row["IMIĘ_PIERWSZE"],
        plec=row["PŁEĆ"],
    ).first()
    
    if not existing:
        record = NameRecord(
            kt_usc=int(row["KT_USC"]),
            wojewodztwo=row["WOJEWÓDZTWO"],
            powiat=row["POWIAT"],
            gmina=row["GMINA"],
            imie_pierwsze=row["IMIĘ_PIERWSZE"],
            plec=row["PŁEĆ"],
            liczba_wystapien=int(row["LICZBA_WYSTĄPIEŃ"])
        )

        db.add(record)

db.commit()

print("CSV załadowane do PostgreSQL")