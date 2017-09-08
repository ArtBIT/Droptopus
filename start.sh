#!/bin/bash
pushd . >/dev/null
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

# If the virtual environment has not yet been initialized
if [[ ! -d .env ]]; then
    virtualenv --no-site-packages .env && source .env/bin/activate && pip install -r env.requirements.txt
fi

# activate virtual environment
source .env/bin/activate

# start the app
python ./droptopus.py &
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
popd >/dev/null
