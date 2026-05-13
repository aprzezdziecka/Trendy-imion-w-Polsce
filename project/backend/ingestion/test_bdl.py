import requests
import pandas as pd
# tu jest tylko test czy api działa, nic nie nie zapisuje w tabelkach:)

url = "https://bdl.stat.gov.pl/api/v1/data/by-variable/72305"

params = {
    "unit-level": 5,
    "year": 2024,
    "page-size": 20,
    "format": "json"
}

response = requests.get(url, params=params)
#kod teryt to literki 3,4,8,9,10,11, 12, trzeba to bedzie ogarnąć   
data = response.json()

records = []

for res in data["results"]:

    records.append({
        "id": res["id"],
        "nazwa": res["name"],
        "rok": res["values"][0]["year"],
        "ludnosc": res["values"][0]["val"]
    })

df = pd.DataFrame(records)

print(df)