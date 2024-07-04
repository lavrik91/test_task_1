#!/bin/bash

cd src


celery --app=celery_app:app_celery worker -l INFO
