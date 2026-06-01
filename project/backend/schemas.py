from pydantic import BaseModel

class NameRecordOut(BaseModel):
    id_powiat: str
    wojewodztwo: str
    powiat: str
    imie_pierwsze: str
    plec: str
    liczba_wystapien: int

    class Config:
        from_attributes = True

class GUSRecordOut(BaseModel):
    id_powiat: str
    nazwa: str
    rok: int
    ludnosc: int
    wskaznik_urbanizacji: float | None
    wiek: float | None
    
    class Config:
        from_attributes = True
