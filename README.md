# local sentry

## build

execute the script `build.sh` to build docker image tagged `lumos-sentry:image` from dockerfile `local-sentry.Dockerfile`.    

    $ ./build.sh

## run

execute the script `run.sh` to launch docker container `local-sentry` from image `local-sentry:latest`  
- local folder `~/Library/Logs/local-sentry` is bound to folder `/var/log/local-sentry` in the container  

    # listen on default port (9000)
    $ ./run.sh

    # listen on non-default port 9001
    $ ./run.sh 9001

## test

once the docker container has been started via executing `run.sh`, it can be tested from the host machine via changing the current working directory to `local-sentry/local-sentry`, and running pytest `python3 -m pytest`.

## operation

local-sentry runs a fastapi http server on a default port of 9000 that mimics the `/store` endpoint exposed by `sentry`, and writes the json received to the local file system as a .json file at `~/Library/Logs/local-sentry`.
