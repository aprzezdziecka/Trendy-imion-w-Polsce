# Trendy imion w Polsce

Celem projektu „Trendy imion w Polsce” jest analiza popularności imion nadawanych dzieciom w Polsce z wykorzystaniem danych pochodzących z rejestrów USC oraz Banku Danych Lokalnych GUS. Aplikacja umożliwia przeglądanie rankingów imion, analizę danych demograficznych oraz prezentację wyników w postaci map i wykresów. System został zaprojektowany jako aplikacja webowa integrująca dane z różnych źródeł i udostępniająca je użytkownikowi w przejrzystej formie.

## 1. Architektura systemu
Projekt został zbudowany w oparciu o architekturę wielowarstwową, w której poszczególne komponenty odpowiadają za określone funkcje systemu. Strukturę aplikacji przedstawiono za pomocą trzech diagramów C4: Context Diagram, Container Diagram oraz Component Diagram.

### Poziom 1: Context diagram
Diagram kontekstowy przedstawia użytkownika systemu oraz zewnętrzne źródła danych, z którymi komunikuje się aplikacja (GUS BDL API oraz Dane.gov.pl).
![Diagram Kontekstu](diagramy/Context_diagram.png)

### Poziom 2: Container diagram
Diagram kontenerów przedstawia strukturę systemu oraz komunikację pomiędzy frontendem, backendem, bazą danych i usługą przetwarzania danych.
![Diagram Kontenerów](diagramy/Container_diagram.png)

### Poziom 3: Component diagram
Diagram komponentów pokazuje wewnętrzną strukturę Backend API oraz współpracę pomiędzy jego najważniejszymi komponentami.
![Diagram Komponentów](diagramy/Component_diagram.png)

---

## 2. Specyfikacja warstw architektonicznych - stack technologiczny

TRZEBA DOPISAC WYJASNINIE CZEMU

### Frontend

Odpowiada za prezentację danych użytkownikowi, wyświetlanie map oraz wykresów statystycznych. Został zrealizowany przy użyciu technologii **HTML5**, **CSS3** i **JavaScript**. Do wizualizacji danych wykorzystano biblioteki **Leaflet.js** (wraz z plikami map w formacie GeoJSON/JSON) oraz **Chart.js**.

### Backend API

Odpowiada za obsługę zapytań użytkowników, udostępnianie danych poprzez REST API oraz realizację logiki aplikacji. Został zaimplementowany w języku **Python** z wykorzystaniem frameworka **FastAPI**. Automatyczna synchronizacja danych realizowana jest przy użyciu **APScheduler**.

### Warstwa dostępu do danych

Odpowiada za komunikację z bazą danych oraz walidację danych przesyłanych przez API. Wykorzystuje biblioteki **SQLAlchemy** oraz **Pydantic**.

### Baza danych

Odpowiada za przechowywanie danych o imionach oraz danych demograficznych wykorzystywanych przez system. Zastosowano relacyjną bazę danych **PostgreSQL**.

### Moduł pobierania danych (Data ingestion)

Odpowiada za pobieranie, przetwarzanie i zapisywanie danych pochodzących z plików CSV oraz API GUS. Został zaimplementowany w języku **Python**.

### Konteneryzacja

Wszystkie komponenty systemu uruchamiane są w kontenerach **Docker**, natomiast ich konfiguracja i zarządzanie realizowane są za pomocą **Docker Compose**.



---

## 3. Przetwarzane dane i integracja z zewnętrznymi źródłami

System wykorzystuje dane pochodzące z dwóch oficjalnych źródeł publicznych.

### 1. Dane.gov.pl (Ministerstwo Cyfryzacji / USC)

Źródłem danych jest plik CSV zawierający wykaz imion pierwszych nadanych dzieciom w Polsce.

**Przetwarzane dane:**

* imię dziecka,
* płeć (M/K),
* liczba nadań danego imienia.

Dane są importowane do bazy PostgreSQL i wykorzystywane do tworzenia rankingów oraz analiz popularności imion.

### 2. Bank Danych Lokalnych GUS

Źródłem danych są pliki statystyczne oraz dane pobierane z API GUS.

**Przetwarzane dane:**

* nazwy województw i powiatów,
* liczba mieszkańców poszczególnych powiatów,
* wskaźnik obciążenia demograficznego określający relację między ludnością w wieku nieprodukcyjnym i produkcyjnym,
* dane przestrzenne wykorzystywane do prezentacji wyników na mapach.

Dane są przetwarzane i łączone z warstwami mapowymi wykorzystywanymi przez aplikację do prezentacji wyników na mapach.

---

## 5. Uruchomienie aplikacji

???

### Wymagania

* Docker
* Docker Compose

### Uruchomienie projektu

```bash
docker compose up --build
```

Aplikacja będzie dostępna pod adresami:

* Frontend: `http://localhost:8080`
* Dokumentacja API: `http://localhost:8000/docs`

### Środowiska

#### Development

#### Test

#### Production

---

## 6. Testowanie aplikacji

### Testy jednostkowe

### Testy wydajnościowe
???

---

???

---

## 7. Podział zadań w zespole

???


