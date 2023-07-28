#!/usr/bin/env bash

default_port=9000
tag="latest"
image_name="local-sentry"
container_name="local-sentry"
user="davidbarkhuizen"

function configure_buildkit {

    export DOCKER_BUILDKIT=1;
    export BUILDKIT_PROGRESS=plain;
}

function build {

    configure_buildkit

    echo "building $image_name:$tag"
    docker build -t $image_name:$tag -f local-sentry.Dockerfile .
}

function publish {
    docker image tag $image_name:$tag $user/$image_name:$tag
    docker image push $user/$image_name:$tag
}

function stop {
    docker stop $container_name;
    docker container rm $container_name;
}

function run {

    port=$1
    if [ ! "$port" ]; then
        port=$default_port
    fi

    stop

    mkdir -p "${HOME}/Library/Logs/local-sentry";

    docker run \
        -e "LOCAL_SENTRY_PORT=$port" \
        -p 127.0.0.1:$port:$port/tcp \
        --mount type=bind,source="${HOME}/Library/Logs/local-sentry",target=/var/log/local-sentry \
        --name $container_name \
        $image_name:$tag;
}

function usage {
    echo "./local-sentry.sh build|run|stop|publish"
}

case $1 in

    "build")
        build
    ;;

    "publish")
        publish
    ;;

    "run")
        run
    ;;

    "stop")
        stop
    ;;

    *)
        usage
    ;;
esac

