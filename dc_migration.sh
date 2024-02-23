#!/bin/bash
docker-compose run --rm web python manage.py makemigrations discussions 
sleep 2
docker-compose run --rm web python manage.py migrate 



