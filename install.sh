#! /bin/bash

cd /root
apt-get update
apt-get upgrade
apt-get install vim
apt-get install htop
apt-get install git
apt-get install python3-pyaudio
apt-get install stockfish
apt-get install python3-mpv
apt-get install python3-pip
apt-get install python3-requests
apt-get install flac
pip install colorconsole
echo "PermitRootLogin yes" >> /etc/ssh/sshd.conf
git clone https://github.com/respeaker/seeed-voicecard.git
cd seeed-voicecard
./install.sh
echo "defaults.pcm.card 1" >> /etc/asound.conf
echo "defaults.ctl.card 1" >> /etc/asound.conf
cd /root
git clone https://github.com/fraoustin/myassist.git
cd myassist
git checkout develop
pip install -r REQUIREMENTS
cd /root
cp myassist/env/.gitconfig .
cp myassist/env/.bashrc .
cp myassist/env/.pythonrc .
reboot