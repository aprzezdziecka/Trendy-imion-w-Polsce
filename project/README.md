Aktualna instrukcja:

1. Wchodzimy do repo a później do folderu project → `cd project`
2. `docker compose up -d`
3. opcjonalnie `docker compose --profile init run --rm data_ingestion`

4. w razie potrzeby `docker compose down -v` lub `docker compose down`

docker exec -it project-db-1 psql -U postgres -d namesdb

do testów jednostkowych: docker compose -f docker-compose.yml -f docker-compose.test.yml up --build


Swagger będzie na:
http://127.0.0.1:8000/docs 

http://localhost:8080/