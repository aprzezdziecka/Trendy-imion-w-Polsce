from pydantic import BaseModel
from pydantic import ConfigDict


class NameRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_powiat: str
    wojewodztwo: str
    powiat: str
    imie_pierwsze: str
    plec: str
    liczba_wystapien: int


class GUSRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_powiat: str
    nazwa: str
    rok: int
    ludnosc: int
    wskaznik_urbanizacji: float | None
    wiek: float | None
