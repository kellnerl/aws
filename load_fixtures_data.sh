#!/bin/bash
python manage.py loaddata diskuze/fixtures/theme_table_data.json && \
python manage.py loaddata diskuze/fixtures/section_table_data.json && \
python manage.py loaddata diskuze/fixtures/domain_table_data.json
