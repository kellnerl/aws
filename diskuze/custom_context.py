import requests
from django.utils import timezone
from datetime import date

# custom_context.py
def custom_data(request):
    # Zde můžete provádět logiku pro získání hodnoty, kterou chcete předat do headeru
    version = "0.76"
    # Získání dnešního data

    response = requests.get("https://svatkyapi.cz/api/day")
    data = response.json()
    aktualni_datum_cas = timezone.now()
 # 
 #   today = date.today()

    if data['isHoliday'] == 'true':
        svatek=f"svátek má {data['name']}, {data['holidayName']}"
    else:
        svatek=f"svátek má {data['name']}"
    # Vraťte slovník s daty, které chcete přidat do kontextu
    return {'svatek': svatek, 'version': version, 'aktualni_datum_cas': aktualni_datum_cas}
