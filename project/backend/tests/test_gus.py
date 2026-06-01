"""Testy jednostkowe endpointów /gus"""


def test_gus_lista_nie_jest_pusta(client):
    r = client.get("/gus/")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_gus_rekord_ma_wymagane_pola(client):
    r = client.get("/gus/")
    first = r.json()[0]
    for field in ("id_powiat", "nazwa", "rok", "ludnosc"):
        assert field in first, f"Brak pola: {field}"


def test_gus_analysis_struktura_odpowiedzi(client):
    r = client.get("/gus/analysis")
    assert r.status_code == 200
    data = r.json()
    wymagane_klucze = (
        "scatter_data", "urban_map", "age_map",
        "urban_top", "urban_bottom", "rural_top", "rural_bottom",
        "old_top", "old_bottom", "young_top", "young_bottom",
        "woj_ranking",
    )
    for klucz in wymagane_klucze:
        assert klucz in data, f"Brak klucza: {klucz}"


def test_gus_analysis_scatter_ma_dane(client):
    r = client.get("/gus/analysis")
    scatter = r.json()["scatter_data"]
    assert len(scatter) > 0
    first = scatter[0]
    for field in ("id_powiat", "nazwa", "urbanizacja", "wiek", "diversity"):
        assert field in first, f"Brak pola w scatter: {field}"


def test_gus_analysis_woj_ranking_posortowany(client):
    r = client.get("/gus/analysis")
    ranking = r.json()["woj_ranking"]
    assert len(ranking) > 0
    urbanizacje = [w["avg_urbanizacja"] for w in ranking]
    assert urbanizacje == sorted(urbanizacje, reverse=True), \
        "Ranking nie jest posortowany malejąco po urbanizacji"


def test_gus_analysis_top_names_maja_imie_i_liczbe(client):
    r = client.get("/gus/analysis")
    data = r.json()
    for klucz in ("urban_top", "rural_top", "old_top", "young_top"):
        for item in data[klucz]:
            assert "imie" in item
            assert "liczba" in item
            assert item["liczba"] > 0
