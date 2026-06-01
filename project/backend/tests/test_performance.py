"""Testy wydajnościowe - sprawdzają czas odpowiedzi endpointów"""
import time


def _elapsed(client, url):
    start = time.perf_counter()
    r = client.get(url)
    return r, time.perf_counter() - start


def test_search_ponizej_2s(client):
    r, t = _elapsed(client, "/names/search?imie=ANNA")
    assert r.status_code == 200
    assert t < 2.0, f"Wyszukiwanie imienia zbyt wolne: {t:.2f}s (limit 2s)"


def test_stats_ponizej_2s(client):
    r, t = _elapsed(client, "/names/stats?imie=JAN")
    assert r.status_code == 200
    assert t < 2.0, f"Statystyki imienia zbyt wolne: {t:.2f}s (limit 2s)"


def test_regions_ponizej_1s(client):
    r, t = _elapsed(client, "/names/regions")
    assert r.status_code == 200
    assert t < 1.0, f"Lista regionów zbyt wolna: {t:.2f}s (limit 1s)"


def test_regional_top_ponizej_3s(client):
    r, t = _elapsed(client, "/names/regional-top?level=woj&id=14&limit=5")
    assert r.status_code == 200
    assert t < 3.0, f"Top regionalny zbyt wolny: {t:.2f}s (limit 3s)"


def test_gus_analysis_ponizej_10s(client):
    """Analiza GUS jest ciężka obliczeniowo - dopuszczamy do 10s."""
    r, t = _elapsed(client, "/gus/analysis")
    assert r.status_code == 200
    assert t < 10.0, f"Analiza GUS zbyt wolna: {t:.2f}s (limit 10s)"
