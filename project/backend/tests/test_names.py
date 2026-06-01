"""Testy jednostkowe endpointów /names"""


def test_root_ok(client):
    r = client.get("/")
    assert r.status_code == 200


def test_search_znane_imie_zwraca_liste(client):
    r = client.get("/names/search?imie=ANNA")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_search_nieznane_imie_zwraca_pusta_liste(client):
    r = client.get("/names/search?imie=XYZQWERTY999")
    assert r.status_code == 200
    assert r.json() == []


def test_search_wynik_ma_wymagane_pola(client):
    r = client.get("/names/search?imie=JAN")
    data = r.json()
    assert len(data) > 0
    first = data[0]
    for field in ("id_powiat", "imie_pierwsze", "liczba_wystapien", "powiat", "wojewodztwo"):
        assert field in first, f"Brak pola: {field}"


def test_stats_znane_imie(client):
    r = client.get("/names/stats?imie=MARIA")
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert data["total"] > 0
    assert "top3" in data
    assert len(data["top3"]) <= 3


def test_stats_nieznane_imie_zwraca_blad(client):
    r = client.get("/names/stats?imie=XYZQWERTY999")
    assert r.status_code == 200
    assert "error" in r.json()


def test_regions_zwraca_slownik_woj(client):
    r = client.get("/names/regions")
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    for kod, woj in data.items():
        assert "nazwa" in woj
        assert "powiaty" in woj
        assert isinstance(woj["powiaty"], list)


def test_regional_top_wojewodztwo(client):
    r = client.get("/names/regional-top?level=woj&id=14&limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "top_all" in data
    assert "total_births" in data
    assert "diversity_per_1000" in data
    assert len(data["top_all"]) <= 5


def test_regional_top_limit_jest_respektowany(client):
    r = client.get("/names/regional-top?level=woj&id=14&limit=3")
    data = r.json()
    assert len(data["top_all"]) <= 3
