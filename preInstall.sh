# This Script installs all the necessary packages
# Also installs Django, PHP admin, Jhoomla, Wordpress
# Configures applications and the tables

#instaling Python
sudo apt-get install python2.7
sudo apt-get install python-pip
sudo pip install django=1.8.2
sudo pip install



#installing joomla



#installing mysql
sudo apt-get install mysql-server

#install phpmyadmin
sudo apt-get install phpmyadmin apache2-utils
sudo echo "" >> /etc/apache2/apache2.conf
sudo echo "Include /etc/phpmyadmin/apache.conf" >> /etc/apache2/apache2.conf
sudo service apache2 restart

