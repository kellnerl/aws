import requests
from datetime import date
# custom_context.py
def custom_data(request):
    # Zde můžete provádět logiku pro získání hodnoty, kterou chcete předat do headeru
    version = "0.57"
    # Získání dnešního data

    response = requests.get("https://svatkyapi.cz/api/day")
    data = response.json()
 # 
 #   today = date.today()

# Volání Namedays API pro zjištění svátků dnes
 #   response = requests.get(f"https://api.abalin.net/namedays?country=cz&month={today.month}&day={today.day}", verify=False)
 #   data = response.json()

  #  if "data" in data and data["data"]:
  #      namedays = data["data"]["namedays_cz"]
  #      svatek = f"Dnes má svátek: {', '.join(namedays)}"
    if data['isHoliday'] == 'true':
        svatek=f"svátek má {data['name']}, {data['holidayName']}"
    else:
        svatek=f"svátek má {data['name']}"
    # Vraťte slovník s daty, které chcete přidat do kontextu
    return {'svatek': svatek, 'version': version}
