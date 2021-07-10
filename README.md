# auto_farm_recorder

## Install dependencies
```
sudo apt-get update && sudo apt-get upgrade

curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

sudo apt-get install \
    git \
    htop \
    screen \
    motion \
    libffi-dev \
    libssl-dev \
    python3 \
    python3-pip \
    python3-dev \
    python3-opencv \
    awscli

cd ~
git clone https://github.com/freefarmdata/auto_farm_recorder
cd auto_farm_recorder
sudo su

docker-compose -f docker-compose.yml build --parallel
docker-compose -f docker-compose.yml up

pip3 install -r requirements.txt

mkdir grafana
sudo chown 472:472 grafana

sudo pip3 install docker-compose
docker-compose -f docker-compose.yml up -d
```

## Set Static IP
```
echo "" >> /etc/dhcpcd.conf && \
echo "interface eth0" >> /etc/dhcpcd.conf && \
echo "static ip_address=192.168.0.100/24" >> /etc/dhcpcd.conf && \
echo "static routers=192.168.0.1" >> /etc/dhcpcd.conf && \
echo "static domain_name_servers=192.168.0.1 8.8.8.8 4.4.4.4" >> /etc/dhcpcd.conf
```

## Setup Systemd
```
cp auto_farm_recorder/bin/recorder.service /etc/systemd/system/recorder.service
sudo systemctl enable recorder
sudo service recorder start
```

### Backup Postgres
```
docker exec -t postgres pg_dump farmdata -U admin > ./backup.sql
```

### Backup Images
```
scp -r pi@192.168.0.100:/etc/recorder/images ./
```