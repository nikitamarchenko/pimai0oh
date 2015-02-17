#!/usr/bin/env bash

#apt-get update
#apt-get install -y python-dev git
#curl -s https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py | python
#pip install Flask gunicorn 
#pip install supervisor --pre


if [ ! -d pimai0oh ]; then
	git clone https://github.com/nikitamarchenko/pimai0oh.git
    cd pimai0oh
else
	cd pimai0oh
	git pull --rebase
fi

python setup.py install
if [ ! -f /etc/supervisord.conf ]; then
    rm -f /etc/supervisord.conf
	cp /home/vagrant/pimai0oh/script/supervisord.conf /etc/supervisord.conf
fi
cd - 

supervisord
