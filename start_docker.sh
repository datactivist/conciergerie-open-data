#!/bin/bash

. docker-config.config     # Read config file

Help()
{
   # Display Help
   echo "Start chatbot service using docker-config.config configuration."
   echo
   echo "Syntax: start_service.sh [-a|-i|-d|-s|-h]"
   echo "options:"
   echo "a     Ignore the creation of a new action server image (when in docker mode)."
   echo "i     Ignore the installation and starting of the install.sh script (when in docker mode)."
   echo "d     Ignore the start of the docker (when in docker mode)."
   echo "s     Run the docker in the background"
   echo "h     Show this help panel"
   echo
}


flag_ignore_action=false
flag_ignore_install=false
flag_ignore_docker=false
flag_silence_docker=false

while [ -n "$1" ]; do # while loop starts

	case "$1" in

	-a) flag_ignore_action=true ;;

	-i) flag_ignore_install=true ;;

    -d) flag_ignore_docker=true ;;

	-s) flag_silence_docker=true ;;

    -h) Help 
        exit;;

	*) echo "Option $1 not recognized, use option -h to see available options" 
       exit;; # In case you typed a different option other than a,b,c

	esac

	shift

done



update_expansion_api_adress()
{
    if [ $deployment_method == "docker_solo" ]; then
        sed -i "s/API_expansion_host_name =.*/API_expansion_host_name = $api_expansion_host_name/" api_call.py
        sed -i "s/API_expansion_port =.*/API_expansion_port = $api_expansion_port/" api_call.py

        sed -i "s/API_reranking_host_name =.*/API_reranking_host_name = $api_reranking_host_name/" api_call.py
        sed -i "s/API_reranking_port =.*/API_reranking_port = $api_reranking_port/" api_call.py
    elif [ $deployment_method == "docker_with_expansion" ]; then
        sed -i "s/API_expansion_host_name =.*/API_expansion_host_name = 'query-exp'/" api_call.py
        sed -i "s/API_expansion_port =.*/API_expansion_port = $api_expansion_port/" api_call.py

        sed -i "s/API_reranking_host_name =.*/API_reranking_host_name = $api_reranking_host_name/" api_call.py
        sed -i "s/API_reranking_port =.*/API_reranking_port = $api_reranking_port/" api_call.py
    fi
}

update_rest_webhook_adress()
{
    if [ $deployment_method == "docker_solo" ]; then
        sed -i "s/const rasa_host_name =.*/const rasa_host_name = 'localhost:80'/" script.js
    elif [ $deployment_method == "docker_with_expansion" ]; then
        sed -i "s/const rasa_host_name =.*/const rasa_host_name = 'localhost:80'/" script.js
    fi
}

create_custom_actions_image()
{

    if ! $flag_ignore_action; then
        cd actions/
        update_expansion_api_adress
        cd ..
        echo "Creating a new custom actions docker image"
        sudo docker build . -t $custom_actions_image_name:$custom_actions_image_version
    else
        echo "Ignoring creation of a new custom actions docker image"
    fi
    echo ""

}

install_and_start_script()
{
    if ! $flag_ignore_install
    then

        cd ../widget/static/js
        update_rest_webhook_adress
        cd ../../../chatbot

        echo "Installing and starting install.sh script"

        if ! test -f "install.sh"; then
            curl -sSL -o install.sh https://storage.googleapis.com/rasa-x-releases/0.37.1/install.sh
        else
            echo "install.sh script is already downloaded"
        fi

        sudo bash ./install.sh

    else
        echo "Ignoring installation and start of install.sh script"
    fi
    echo ""
}

add_docker_compose_overrider()
{
    echo "Creating docker-compose.override.yml"

    echo """version: '3.4'
services:    
    app:
        image: $custom_actions_image_name:$custom_actions_image_version""">docker-compose.override.yml

    if [ $deployment_method == "docker_with_expansion" ]; then
        
        echo """
        
    query-exp:
        image: $expansion_api_image_name:$expansion_api_image_version""">>docker-compose.override.yml

    fi

    echo ""

}


add_rest_api()
{
    # ----- Adding rest api to credentials.yml file -----
    if ! grep -q "rest:" credentials.yml; then
        echo "Adding REST api to credentials"
        echo $'\nrest:'>>credentials.yml
    else
        echo "REST API already added"
    fi
    echo ""
}

processing_env()
{
    # ----- Modifying and adding lines to .env -----
    echo "Updating .env"
    sudo sed -i "s/RASA_VERSION=.*/RASA_VERSION=$rasa_version/" .env
    sudo sed -i "s/RASA_X_VERSION=.*/RASA_X_VERSION=$rasa_x_version/" .env
    echo ""
}

start_docker()
{
    # ----- Starting docker -----
    if ! $flag_ignore_docker
    then
        if $flag_silence_docker
        then
            echo "Starting docker in silent mode"
            sudo docker-compose up -d
        else
            echo "Starting docker"
            sudo docker-compose up
        fi
    fi
    echo ""
}


process()
{
    echo "Deploying chatbot with '$deployment_method' mode"
    echo ""
    
    cd chatbot/custom-actions
    create_custom_actions_image

    cd ..
    install_and_start_script

    cd /
    
    sudo chgrp -R root /etc/rasa/* && sudo chmod -R 777 /etc/rasa/*
    sudo chown -R 1001 /etc/rasa/db && sudo chmod -R 750 /etc/rasa/db

    cd etc/rasa
    add_docker_compose_overrider

    add_rest_api

    processing_env

    start_docker
}


if [ $deployment_method == "docker_solo" ]; then
    process

elif [ $deployment_method == "docker_with_expansion" ]; then
    process

else
    echo "'$deployment_method' is not a valid value for deployment_method in config.config"
fi



#In bash
# root path -> ~/etc/rasa