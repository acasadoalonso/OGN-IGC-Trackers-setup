#!/bin/bash
echo								#
echo " "							#
echo "Installing the SGP 2D live tracking interface ...." 	#
echo "=================================================="	#
echo " "							#
echo								#
export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8		#
sudo apt-get install -y software-properties-common 		#
sudo apt-get install -y python3-software-properties 		#
sudo apt-get install -y build-essential 			#
#sudo rm /etc/apt/sources.list.d/ondre*				#
#sudo add-apt-repository ppa:ondrej/php				#
echo								#
echo " "							#
echo "Lets update the operating system libraries  ...." 	#
echo "=================================================="	#
echo " "							#
echo								#
sudo apt-get update						#
export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8		#
echo "export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8 " >>~/.profile #
echo "export LD_LIBRARY_PATH=/usr/local/lib" >>~/.profile 	#
sudo apt-get -y upgrade						#
echo								#
echo " "							#
echo "Installing the packages required . (LAMP stack)..."	#
echo "=================================================="	#
echo " "							#
echo								#
sudo apt-get install -y tasksel  				#
sudo tasksel install lamp-server                                #
sudo apt-get install -y sqlite3					#
sudo apt-get install -y python3-dev python3-pip 		#
sudo apt-get install -y python-mysqld  				#
sudo apt-get install -y figlet  				#
sudo apt-get install -y dos2unix libarchive-dev	 autoconf mc	#
sudo apt-get install -y pkg-config git	mutt 		vim	# 
git config --global user.email "acasadoalonso@gmail.com"        #
git config --global user.name "Angel Casado"                    #
sudo apt-get install -y apache2 php 				#
sudo apt-get install -y php-sqlite3 php-mysql php-cli 		#
sudo apt-get install -y php-mcrypt 				#
sudo apt-get install -y php-mbstring php-gettext php-json	#
sudo apt-get install -y php7.3					#
sudo apt-get install -y ntpdate					#
sudo apt-get install -y minicom					#
sudo apt-get install python3-mysqldb				#
sudo a2enmod rewrite						#
sudo phpenmod mcrypt						#
sudo phpenmod mbstring						#
sudo -H python3 -m pip install --upgrade pip			#
pip3 -V								#
sudo -H python3 -m pip install ephem pytz geopy configparser 	#
sudo -H python3 -m pip install pycountry			#
sudo -H python3 -m pip install beeprint ogn.client		#
sudo -H python3 -m pip install tqdm psutil 			#
sudo -H python3 -m pip install ttn 				#
sudo -H python3 -m pip install eciespy pycryptodome             #


