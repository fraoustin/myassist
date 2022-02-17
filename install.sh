#! /bin/bash

cd /root
apt-get update
apt-get upgrade
apt-get -y install vim
apt-get -y install htop
apt-get -y install git
apt-get -y install sqlite3
apt-get -y install python3-pyaudio
apt-get -y install stockfish
apt-get -y install python3-mpv
apt-get -y install python3-pip
apt-get -y install python3-requests
apt-get -y install flac
pip install colorconsole
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config.d/01_permitroot.conf
git clone https://github.com/respeaker/seeed-voicecard.git
cd seeed-voicecard
./install.sh
echo "defaults.pcm.card 1" >> /etc/asound.conf
echo "defaults.ctl.card 1" >> /etc/asound.conf
cd /root
git clone https://github.com/fraoustin/myassist.git
cd myassist
git checkout develop
pip install -r REQUIREMENTS.txt
cd /root
cp myassist/env/.gitconfig .
cp myassist/env/.bashrc .
cp myassist/env/.pythonrc .
reboot