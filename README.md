# auto_farm_recorder

## Install dependencies
```
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

sudo apt-get install git htop screen motion libffi-dev libssl-dev python3 python3-pip python3-dev

sudo apt-get install -y \
build-essential \
tk-dev \
libncurses5-dev \
libncursesw5-dev \
libreadline6-dev \
libdb5.3-dev \
libgdbm-dev \
libsqlite3-dev \
libssl-dev \
libbz2-dev \
libexpat1-dev \
liblzma-dev \
zlib1g-dev \
libffi-dev

wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tar.xz
tar xf Python-3.8.0.tar.xz
cd Python-3.8.0
./configure --prefix=/usr/local/opt/python-3.8.0
make -j 4
sudo make altinstall
sudo update-alternatives --config python

echo "" >> ~/.bashrc
echo "alias python3.8='/usr/local/opt/python-3.8.0/bin/python3.8'" >> ~/.bashrc

sudo pip3 install docker-compose

docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up
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

