# Použijte oficiální Python image
FROM python:3.8

# Nastavte pracovní adresář v kontejneru
WORKDIR /app

# Nakopírujte requirements.txt a nainstalujte závislosti
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn

# Nakopírujte zbytek projektu do kontejneru
COPY . /app/

# Nastavte prostředí pro Django
ENV DJANGO_SETTINGS_MODULE=diskuze.settings

# Spusťte migrace a sbal aplikaci
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Exponujte port, na kterém běží Django
EXPOSE 8000

ENV PATH="/usr/local/bin:${PATH}"

# Spusťte Django server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "diskuze.wsgi:application"]
