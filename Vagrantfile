# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT
if hash pip 2>/dev/null; then
    echo "[+] pip already installed"
else
    curl -sSL https://bootstrap.pypa.io/get-pip.py | python
    pip -q install -U docker-compose tox invoke
    curl -sSL https://raw.githubusercontent.com/docker/compose/1.2.0/contrib/completion/bash/docker-compose > /etc/bash_completion.d/docker-compose
    wget --no-check-certificate -q  https://raw.github.com/petervanderdoes/gitflow/develop/contrib/gitflow-installer.sh && bash gitflow-installer.sh install develop; rm gitflow-installer.sh; rm -rf gitflow/
fi
SCRIPT

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "ubuntu/trusty64"

  config.vm.hostname = "local-dev"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network "forwarded_port", guest: 80,   host: 8080
  config.vm.network "forwarded_port", guest: 5000, host: 15000
  config.vm.network "forwarded_port", guest: 8080, host: 18080

  config.vm.provision "docker" do |d|
    d.pull_images "alpine"
    d.pull_images "nginx"
  end

  config.vm.provision "file", source: "~/.gitconfig", destination: ".gitconfig"
  config.vm.provision "file", source: "~/.ssh/id_rsa", destination: ".ssh/id_rsa"
  config.vm.provision "file", source: "~/.ssh/id_rsa.pub", destination: ".ssh/id_rsa.pub"
  config.vm.provision "file", source: "~/.pypirc", destination: ".pypirc"


  config.vm.provision "file", source: "./dev/fig.yml", destination: "fig.yml"
  config.vm.provision "file", source: "./dev/bash_aliases", destination: ".bash_aliases"

  config.vm.synced_folder ".", "/home/vagrant/seedbox", type: "rsync", rsync__exclude: [".tox/", "cover/", "doc/build"]

  # Provision using shell to execute ansible because of windows issues
  config.vm.provision "shell", inline: $script

  config.vm.provider "virtualbox" do |vb|
    vb.customize ['modifyvm', :id, '--memory', 1024]
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

end
