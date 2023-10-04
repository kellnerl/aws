# Použijte oficiální Python image
FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Nastavte pracovní adresář v kontejneru
WORKDIR /copy

# Nakopírujte requirements.txt a nainstalujte závislosti
COPY requirements.txt /copy/
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn

# Nakopírujte zbytek projektu do kontejneru
COPY . /copy/

# Nastavte prostředí pro Django
ENV DJANGO_SETTINGS_MODULE=diskuze.settings

# Spusťte migrace a sbal aplikaci
#RUN python manage.py makemigrations
#RUN python manage.py migrate
#RUN python manage.py collectstatic --noinput


# Exponujte port, na kterém běží Django
EXPOSE 8000

ENV PATH="/usr/local/bin:${PATH}"

#RUN export JAVA_HOME="$(dirname $(dirname $(readlink -f $(which java))))" && echo $JAVA_HOME

# Spusťte Django server

