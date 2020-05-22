#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate
source myvenv/bin/activate
export FLASK_APP=run.py
export FLASK_ENV=development
flask run 
