# auto_farm_recorder

sudo apt install postgresql libpq-dev postgresql-client
postgresql-client-common -y

sudo su postgres
createuser pi -P --interactive
psql
create database farmdata;

curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

sudo apt-get install libffi-dev libssl-dev
sudo apt install python3-dev
sudo apt-get install -y python3 python3-pip
sudo pip3 install docker-compose

docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up