# auto_farm_recorder

## Install dependencies
```
sudo apt-get update && sudo apt-get upgrade

curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

sudo apt-get install git htop screen motion libffi-dev libssl-dev python3 python3-pip python3-dev python3-opencv

cd ~
git clone https://github.com/freefarmdata/auto_farm_recorder
cd auto_farm_recorder
sudo su
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

## Control Motion
```
// to start, stop, and restart motion service
sudo service motion start
sudo service motion stop
sudo service motion restart

// to configure motion service
sudo nano /etc/motion/motion.conf

// Make sure to set permissions to motion user on folder
sudo chown motion:adm /var/lib/motion

// View the .avi movie files
ls -lha /var/lib/motion

// To start on reboot
sudo nano /etc/default/motion
start_motion_daemon=yes
```

### Custom Parameters for motion.conf
```
width 640
height 480
framerate 30
threshold 0
max_movie_time 300
emulate_motion on
output_pictures off
quality 50
ffmpeg_output_movies on
ffmpeg_bps 500000
target_dir /var/lib/motion
stream_port 8081
stream_quality 50
stream_maxrate 60
stream_localhost off
webcontrol_port 8080
webcontrol_localhost off
videodevice /dev/video0
```

