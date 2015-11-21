# This Script installs all the necessary packages
# Also installs Django, PHP admin, Jhoomla, Wordpress
# Configures applications and the tables

echo "preInstall phase started."

#instaling Python
sudo apt-get install python2.7
sudo apt-get install python-pip
sudo pip install django=1.8.2
sudo pip install

#installing mysql
sudo apt-get install mysql-server

#install phpmyadmin
sudo apt-get install phpmyadmin apache2-utils
sudo echo "" >> /etc/apache2/apache2.conf
sudo echo "Include /etc/phpmyadmin/apache.conf" >> /etc/apache2/apache2.conf
sudo service apache2 restart

# Installing Joomla
sudo apt-get update &&sudo apt-get update && sudo apt-get install apache2 mysql-server mysql-client php5 libapache2-mod-php5 php5-mysql php5-curl php5-gd php5-intl php-pear php5-imagick php5-imap php5-mcrypt php5-memcache php5-ming php5-ps php5-pspell php5-snmp php5-tidy php5-xmlrpc

mysql -u root -p
    CREATE DATABASE joomladb;
    CREATE USER joomlauser@localhost IDENTIFIED BY 'root';
    GRANT ALL ON joomladb.* TO joomlauser@localhost;
    \q

cd /tmp/ && wget http://joomlacode.org/gf/download/frsrelease/19665/160049/Joomla_3.3.3-Stable-Full_Package.zip

sudo unzip -q Joomla*.zip -d /var/www/html
sudo chown -R www-data.www-data /var/www/html
sudo chmod -R 755 /var/www/html
sudo service apache2 restart

mkdir -p /var/www/joomla
cd /var/www/joomla/
sudo find . -type f -exec chmod 644 {} \;
sudo find . -type d -exec chmod 755 {} \;

mysql -u root -p
	GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, CREATE TEMPORARY TABLES, LOCK TABLES ON joomla.* TO 'joomla'@'localhost' IDENTIFIED BY 'root';
	\q

open libraries/joomla/filter/input.php, modify the file and restart apache

echo "Replace the below lines of the file libraries/joomla/filter/input.php"
echo "$source = preg_replace('/&#(\d+);/me', "utf8_encode(chr(\\1))", $source); // decimal notation"
echo "$source = preg_replace('/&#x([a-f0-9]+);/mei', "utf8_encode(chr(0x\\1))", $source); // hex notation"
echo "with"
echo "$source = preg_replace_callback('/&#x(\d+);/mi', function($m){return utf8_encode(chr('0x'.$m[1]));}, $source); // decimal notation"
echo "$source = preg_replace_callback('/&#x([a-f0-9]+);/mi', function($m){return utf8_encode(chr('0x'.$m[1]));}, $source); // hex notation"

echo -n "Are you done updating?(y/n)"
read ch
if [ $ch == 'y' ]
then
    echo "Restarting Apache...!!"
else
    echo "Aborting..!!"
    exit
fi

# Restarting apache
sudo service apache2 restart

echo "Please follow the report document to install WordPress.!"
echo "preInstall phase completed.!"
