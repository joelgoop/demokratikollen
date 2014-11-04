#!/bin/bash

#first time we run create folders
mkdir -p docker
mkdir -p data

#kill everything for now.
sudo docker rm -f $(sudo docker ps -a -q)
sudo docker rmi demokratikollen/postgres:latest
sudo docker rmi demokratikollen/nginx:latest
sudo docker rmi demokratikollen/webapp:latest
sudo docker rmi demokratikollen/mongo:latest

#copy files
cp -r src/dockerfiles/webapp docker/
cp -r src/demokratikollen/* docker/webapp/

cp -r src/dockerfiles/mongo docker/

cp -r src/dockerfiles/postgres docker/

cp -r src/dockerfiles/nginx docker/
cp -r src/demokratikollen/www/app/static docker/nginx/

#copy files for import_data
cp src/demokratikollen/data/create_tables.sql data/
cp src/dockerfiles/webapp/urls.txt data/

echo "Creating postgres images and containers"
#Get the postgres image id, if it does not exist, create it
postgres_image_id=`sudo docker images | sed -nr 's/demokratikollen\/postgres\s*[a-z0-9]*\s*([a-z0-9]*).*/\1/p'`

if [ -z $postgres_image_id ]; then
    sudo docker build -t demokratikollen/postgres docker/postgres
fi

#Get the posgres container id, if it does not exist create it
postgres_container_id=`sudo docker ps | sed -nr 's/([a-z0-9]*)\s*demokratikollen\/postgres.*/\1/p'`

if [ -z $postgres_container_id ]; then
    sudo docker run -d --name postgres demokratikollen/postgres
fi

echo "Creating mongo images and containers"

mongodb_image_id=`sudo docker images | sed -nr 's/demokratikollen\/mongo\s*[a-z0-9]*\s*([a-z0-9]*).*/\1/p'`

if [ -z $mongodb_image_id ]; then
	sudo docker build -t demokratikollen/mongo docker/mongo
fi

#Get the posgres container id, if it does not exist create it
mongodb_container_id=`sudo docker ps | sed -nr 's/([a-z0-9]*)\s*demokratikollen\/mongo.*/\1/p'`

if [ -z $mongo_container_id ]; then
    sudo docker run -d --name mongo demokratikollen/mongo
fi	

echo "Creating webapp images and containers"
#Get the webapp image id. Build it if it does not exist
webapp_image_id=`sudo docker images | sed -nr 's/demokratikollen\/webapp\s*[a-z0-9]*\s*([a-z0-9]*).*/\1/p'`

if [ -z $webapp_image_id ]; then
	sudo docker build -t demokratikollen/webapp docker/webapp

	while read cmd; do
		sudo docker $cmd
	done < docker/webapp/setup 

	#create the final container
	deamon = $(cat docker/webapp/deamon)
	sudo docker $deamon
fi

#Get the webapp container id. Start it if it is not already started
webapp_container_id=`sudo docker ps | sed -nr 's/([a-z0-9]*)\s*demokratikollen\/webapp.*/\1/p'`

if [ -z $webapp_container_id ]; then
    sudo docker start webapp
fi

echo "Creating nginx images and containers"
#Create the nginx image if it does not exist
nginx_image_id=`sudo docker images | sed -nr 's/demokratikollen\/nginx\s*[a-z0-9]*\s*([a-z0-9]*).*/\1/p'`

if [ -z $nginx_image_id ]; then
    sudo docker build -t demokratikollen/nginx docker/nginx
fi

#Get the webapp container id. Start it if it is not already started
nginx_container_id=`sudo docker ps | sed -nr 's/([a-z0-9]*)\s*demokratikollen\/nginx.*/\1/p'`

if [ -z $nginx_container_id ]; then
    sudo docker run -d -p 80:80 --link webapp:webapp demokratikollen/nginx 
fi

#remove old source files
rm -rf old_src
#copy cur to old
cp -r src old_src

#remove files.
rm -rf docker/webapp
rm -rf docker/postgres
rm -rf docker/mongo
rm -rf docker/nginx
