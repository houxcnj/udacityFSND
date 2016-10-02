# Linux Server Configuration

A baseline installation of Ubuntu Linux on a virtual machine to host a Flask web application. This includes the installation of updates, securing the system from a number of attack vectors and installing/configuring web and database servers.

ssh grader@52.43.200.135 -i ~/.ssh/udacityProject.rsa -p 2200

### Setup Linux Server

#### Lauch Virtual Machine and SSH into the server

1. Create new development environment.
2. Download private keys and write down your public IP address.
3. Move the private key file into the folder ~/.ssh:
  `$ mv ~/Downloads/udacity_key.rsa ~/.ssh/`
4. Set file rights (only owner can write and read.):
  `$ chmod 600 ~/.ssh/udacity_key.rsa`
5. SSH into the instance:
  `$ ssh -i ~/.ssh/udacity_key.rsa root@PUPLIC-IP-ADDRESS`

  [Based on 'How to set up SSH Keys'][1]

#### Create a new user and give user the permission to sudo

1. Create a new user:
  `$ adduser grader`
2. Give new user the permission to sudo
  1. Create a new file called grader in '/etc/sudoers.d/'.
    `sudo nano grader'
  2. Copy below text to this file.
    `grader ALL=(ALL:ALL) ALL`

  [Based on 'Giving Sudo Access'][2]

#### Change the SSH port from 22 to 2200 and configure SSH access

1. Change ssh config file:
  1. Open the config file:
    `$ vim /etc/ssh/sshd_config`
  2. Change to Port 2200.
  3. Change `PermitRootLogin` from `without-password` to `no`.
  4. * To get more detailed logging messasges, open `/var/log/auth.log` and change LogLevel from `INFO` to `VERBOSE`.
  5. Temporalily change `PasswordAuthentication` from `no` to `yes`.
  6. Append `UseDNS no`.
  7. Append `AllowUsers NEWUSER`.

2. Restart SSH Service:
  `$ /etc/init.d/ssh restart` or `# service sshd restart`

3. Create SSH Keys:
  1. Generate a SSH key pair on the local machine:
    `$ ssh-keygen`
  2. Copy the public id to the server:
    `$ mkdir .ssh`
    `$ touch .ssh/authorized_keys`
    `$ sudo nano .ssh/authorized_keys`
    paste the text here
    `$ sudo chmod 700 .ssh`
    `$ sudo chmod 644 .ssh/authorized_keys`
  3. Login with the new user:
    `$ ssh grader@52.43.200.135 -i ~/.ssh/udacityProject.rsa -p 2200`
  4. Open SSHD config:
    `$ sudo vim /etc/ssh/sshd_config`
  5. Change `PasswordAuthentication` back from `yes` to `no`.

  [Based on 'Installing a Public Key'][3]

#### Configure the Uncomplicated Firewall (UFW)

1. Turn UFW on with the default set of rules:
  `$ sudo ufw enable`
2. Allow incoming TCP packets on port 2200 (SSH):
  `$ sudo ufw allow 2200/tcp`
3. Allow incoming TCP packets on port 80 (HTTP):
  `$ sudo ufw allow 80/tcp`
4. Allow incoming UDP packets on port 123 (NTP):
  `$ sudo ufw allow 123/udp`

  [Based on 'Configuring Ports in UFW'][4]

#### Install and configure Apache to serve a Python mod_wsgi application

1. Install Apache web server:
  `$ sudo apt-get install apache2`
2. Open a browser and open your public ip address
3. Install mod_wsgi for serving Python apps from Apache and the helper package python-setuptools:
  `$ sudo apt-get install python-setuptools libapache2-mod-wsgi`
4. Restart the Apache server for mod_wsgi to load:
  `$ sudo service apache2 restart`

### Setup Catalog App project

#### Install and configure git

1. Install Git:
  `$ sudo apt-get install git`
2. Set your name, e.g. for the commits:
  `$ git config --global user.name "YOUR NAME"`
3. Set up your email address to connect your commits to your account:
  `$ git config --global user.email "YOUR EMAIL ADDRESS"`

  [Based on 'Getting started first time git setup'][5]

#### Setup for deploying a Flask Application on Ubuntu VPS

1. Extend Python with additional packages that enable Apache to serve Flask applications:
  `$ sudo apt-get install libapache2-mod-wsgi python-dev`
2. Enable mod_wsgi:
  `$ sudo a2enmod wsgi`
3. Create a Flask app:
  1. Move to the www directory:
    `$ cd /var/www`
  2. Make a directory for the app:
    1. `$ sudo mkdir catalog`
    2. `$ cd catalog` and `$ sudo mkdir catalog`

4. Install Flask
  1. Install pip installer:
    `$ sudo apt-get install python-pip`
  2. Install virtualenv:
    `$ sudo pip install virtualenv`
  3. Set virtual environment to name 'venv':
    `$ sudo virtualenv venv`
  4. Enable all permissions for the new virtual environment:
    `$ sudo chmod -R 777 venv`
  5. Activate the virtual environment:
    `$ source venv/bin/activate`
  6. Install Flask inside the virtual environment:
    `$ pip install Flask`

5. Configure and Enable a New Virtual Host#
  1. Create a virtual host config file
    `$ sudo nano /etc/apache2/sites-available/catalog.conf`
  2. Paste in the following lines of code and change names and addresses regarding your application:
  ```
    <VirtualHost *:80>
        ServerName PUBLIC-IP-ADDRESS
        ServerAdmin admin@PUBLIC-IP-ADDRESS
        WSGIScriptAlias / /var/www/catalog/catalog.wsgi
        <Directory /var/www/catalog/catalog/>
            Order allow,deny
            Allow from all
        </Directory>
        Alias /static /var/www/catalog/catalog/static
        <Directory /var/www/catalog/catalog/static/>
            Order allow,deny
            Allow from all
        </Directory>
        ErrorLog ${APACHE_LOG_DIR}/error.log
        LogLevel warn
        CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>
  ```
  3. Enable the virtual host:
    `$ sudo a2ensite catalog`

6. Create the .wsgi File and Restart Apache
  1. Create wsgi file:
    `$ cd /var/www/catalog` and `$ sudo nano catalog.wsgi`
  2. Paste in the following lines of code:
  ```
    #!/usr/bin/python
    import sys
    import logging
    logging.basicConfig(stream=sys.stderr)
    sys.path.insert(0,"/var/www/catalog/")

    from catalog import app as application
    application.secret_key = 'Add your secret key'
  ```
7. Restart Apache:
    `$ sudo service apache2 restart`

  [Based on a tutorial on DigitalOcean][6]

#### Clone GitHub repository and make it web inaccessible
1. Clone catalog project to the directory created before

2. Make the GitHub repository inaccessible:

  1. Create and open .htaccess file:
    `$ cd /var/www/catalog/` and `$ sudo vim .htaccess`
  2. Paste in the following:
    `RedirectMatch 404 /\.git`

#### Install other modules & packages
1. Activate virtual environment:
  `$ source venv/bin/activate`
2. Install httplib2 module in venv:
  `$ pip install httplib2`
3. Install requests module in venv:
  `$ pip install requests`
4. Install oauth2client.client:
  `$ sudo pip install --upgrade oauth2client`
5. Install SQLAlchemy:
  `$ sudo pip install sqlalchemy`
6. Install the Python PostgreSQL adapter psycopg:
  `$ sudo apt-get install python-psycopg2`

### Install and configure PostgreSQL

1. Install PostgreSQL:
  `$ sudo apt-get install postgresql postgresql-contrib`
2. Check that no remote connections are allowed (default):
  `$ sudo vim /etc/postgresql/9.3/main/pg_hba.conf`
3. Open the database setup file:
  `$ sudo vim database_setup.py`
4. Change the line starting with "engine" to:
  ```python engine = create_engine('postgresql://grader:grader@localhost/catalog')```
    The first grader is user name and second is the password.
5. Change the same line in application.py
6. Rename application.py:
  `$ sudo mv application.py __init__.py`
7. Change to default user postgres:
  `$ sudo su - postgres`
8. Connect to the system:
  `$ psql`
9. Add postgre user with password:
  1. Create user with LOGIN role and set a password:
    `# CREATE USER grader WITH PASSWORD 'grader';`
  2. Allow the user to create database tables:
    `# ALTER USER grader CREATEDB;`
  3. List current roles and their attributes:
    `# \du`
10. Create database:
  `# CREATE DATABASE catalog WITH OWNER grader;`
11. Revoke all rights:
  `# REVOKE ALL ON SCHEMA public FROM public;`
12. Grant only access to the catalog role:
  `# GRANT ALL ON SCHEMA public TO catalog;`
13. Exit out of PostgreSQl and the postgres user:
  `# \q`, then `$ exit`
14. Create postgreSQL database schema:
  `$ python database_setup.py`
15. Input data to database:
  `$ python lotsofdata.py`

#### Run application
1. Restart Apache:
  `$ sudo service apache2 restart`
2. Open a browser and put in your public ip-address as url, the application should come up

  [Based on a tutorial on DigitalOcean][7]

#### Make OAuth Work

1. Open the Apache configuration files for the web app:
  `$ sudo vim /etc/apache2/sites-available/catalog.conf`
2. Paste in the following line below ServerAdmin:
  `ServerAlias (YOUR HOSTNAME) ec2-52-43-200-135.us-west-2.compute.amazonaws.com
4. Enable the virtual host:
  `$ sudo a2ensite catalog`
5. Make Google+ authorization work:
  1. Go to Google APIs
  2. Under the API Manager click the Credentials and choose the catalog prpject
  3. Add  host name and public IP-address to Authorized JavaScript origins field and host name + oauth2callback to Authorized redirect URIs field


[1]: https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2
[2]: https://classroom.udacity.com/nanodegrees/nd004/parts/00413454014/modules/357367901175461/lessons/4331066009/concepts/48010894710923#
[3]: https://classroom.udacity.com/nanodegrees/nd004/parts/00413454014/modules/357367901175461/lessons/4331066009/concepts/48010894810923#
[4]: https://classroom.udacity.com/nanodegrees/nd004/parts/00413454014/modules/357367901175461/lessons/4331066009/concepts/48010894990923#
[5]: https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup
[6]: https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
[7]: https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps
