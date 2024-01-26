docker-compose run web python manage.py loaddata /noncensura/diskuze/fixtures/theme_table_data.json &&
docker-compose run web python manage.py loaddata /noncensura/diskuze/fixtures/section_table_data.json
 &&
docker-compose run web python manage.py loaddata /noncensura/diskuze/fixtures/domain_table_data.json
