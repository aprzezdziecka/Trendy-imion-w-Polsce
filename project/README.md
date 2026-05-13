Hej, żeby odpalić projekt:

1. Zainstaluj Docker Desktop

2. Clone repo i wejdź do folderu project

3. Odpal postgresa:
   docker compose up -d

4. Wejdź do backend:
   cd backend

5. Utwórz venv:
   python -m venv venv

6. Aktywuj:
   venv\Scripts\activate (tu musialam cos tam sobie aktywowac )

7. Zainstaluj biblioteki:
   pip install -r requirements.txt

8. Uruchom backend:
   uvicorn main:app --reload

Swagger będzie na:
http://127.0.0.1:8000/docs (czyli mozesz sobie tam wejsc z przegladarki, to jest takie api co backend komunikuje sie z frotend)

9. CSV wrzuć do folderu project/ (powinna juz byc nasza csv)

10. Załaduj dane:
    python ingestion/load_csv.py

11. Test BDL:
    python ingestion/test_bdl.py

ogolnie ostatecznie w postgres powinnas miec tabelke z names a test powin ci w terminalu wystwietlac tabelke

potem ponownie urochomienie:

ODPALENIE PROJEKTU

1. W folderze project:
   docker compose up -d

2. Wejdź do backend:
   cd backend

3. Aktywuj venv:
   venv\Scripts\activate

4. Odpal backend:
   uvicorn main:app --reload

5. Swagger:
   http://127.0.0.1:8000/docs

ZAMYKANIE

1. CTRL + C (backend)

2. W folderze project:
   docker compose down
