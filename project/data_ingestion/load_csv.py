import sys
import os
from backend.database import SessionLocal, engine
from backend.models import Base, NameRecord

Base.metadata.create_all(bind=engine)

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

df['id_powiat'] = df['KT_USC'].apply(lambda x: str(x).zfill(7)[:4])

aggregated = df.groupby(
    ['id_powiat', 'WOJEWÓDZTWO', 'POWIAT', 'IMIĘ_PIERWSZE', 'PŁEĆ'],
    as_index=False
)['LICZBA_WYSTĄPIEŃ'].sum()

for _, row in aggregated.iterrows():
    existing = db.query(NameRecord).filter_by(
        id_powiat=row['id_powiat'],
        imie_pierwsze=row['IMIĘ_PIERWSZE'],
        plec=row['PŁEĆ'],
    ).first()

    if not existing:
        record = NameRecord(
            id_powiat=row['id_powiat'],
            wojewodztwo=row['WOJEWÓDZTWO'],
            powiat=row['POWIAT'],
            imie_pierwsze=row['IMIĘ_PIERWSZE'],
            plec=row['PŁEĆ'],
            liczba_wystapien=int(row['LICZBA_WYSTĄPIEŃ'])
        )
        db.add(record)

db.commit()

print("CSV załadowane do PostgreSQL")