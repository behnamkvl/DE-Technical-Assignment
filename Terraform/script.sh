#!/bin/bash

# sleep until instance is ready
until [[ -f /var/lib/cloud/instance/boot-finished ]]; do
  sleep 1
done

sudo apt-get update
sudo apt-get -y upgrade 

# install docker
if [ -x "$(command -v docker)" ]; then
  echo "docker is available"
else
  echo "Install docker"
  sudo apt-get -y install \
                  ca-certificates \
                  curl \
                  gnupg \
                  lsb-release

  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

  echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

  sudo apt-get update
  sudo apt-get -y install docker-ce docker-ce-cli containerd.io
fi

# install docker-compose
if [ -x "$(command -v docker-compose)" ]; then
  echo "docker-compose is available"
else
  echo "Install docker-compose"
  sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
fi
