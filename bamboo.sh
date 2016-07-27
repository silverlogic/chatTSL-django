#!/bin/bash

# Create virtual environment and install deps
pyvenv venv
source venv/bin/activate
pip install -r requirements/dev.txt

export DISPLAY=:1
export SECRET_KEY=notsecret
export DATABASE_URL='postgis://bamboo:bamboo@127.0.0.1/baseapp'
export CELERY_BROKER_URL="redis://127.0.0.1"
export URL="http://localhost"
export FRONT_URL="http://blub.com"

py.test --junitxml=test-results.xml --cov="apps" tests
pip install codecov
codecov --token="17ec662a-faa2-4c69-b2ba-e272bf81e0a4"
