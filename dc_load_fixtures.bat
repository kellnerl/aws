#!/bin/bash
docker-compose run --rm web python manage.py loaddata /noncensura/diskuze/fixtures/theme_table_data.json 
sleep 2
docker-compose run --rm web python manage.py loaddata /noncensura/diskuze/fixtures/section_table_data.json
sleep 2
docker-compose run --rm web python manage.py loaddata /noncensura/diskuze/fixtures/domain_table_data.json
