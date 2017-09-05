#!/bin/bash

# If the virtual environment has not yet been initialized
if [[ ! -d .env ]]; then
    virtualenv --no-site-packages .env && source .env/bin/activate && pip install -r env.requirements.txt
fi

# activate virtual environment
source .env/bin/activate

# start the app
python ./droptopus.py &
