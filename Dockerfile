# base image
FROM python:3.10

#maintainer
LABEL Author="IPE software"

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE=1

#directory to store app source code
RUN mkdir /noncensura

#switch to /app directory so that everything runs from here
WORKDIR /noncensura


#let pip install required packages
COPY requirements.txt /noncensura/
RUN pip install  --no-cache-dir -r requirements.txt

#copy the app code to image working directory
COPY . /noncensura/


# Nastavte prostředí pro Django
ENV DJANGO_SETTINGS_MODULE=diskuze.settings


