# IMO DoBa

IMO Doba (IMO Docubase) is a digitized document database, relying on inputs from the Raspberry Pi which utlizes Optical Character Recognition, to recognize texts and automatically name files accordingly. 

## TABLE OF CONTENTS
1. How to use IMO_Doba
2. Setting up IMO_Doba
3. Setting up the server


### 1. HOW TO USE IMO_Doba

IMO Docubase has two main features, namely the Database View and the Reports Generation View.

**Database View**

This is where users are able to conduct Rename, Delete, and Download functions. Documents sent to the database are seen here, and are able to be sorted by Date, Name, or by Supplier.

**Reports Generation View**

This is where users are able to generate reports based on the date, and type of documents given.


### 2. SETTING UP IMO_DOBA

Upon first cloning of the github repository, it is important that we first look in *parseDoc.py*. Specifically in line  39

``` 
folder_path = r'C:\Users\Carl\Documents\SCHOOLWORKS\IMO_Doba\imodocubase\IMO_Doba\sample_DB'
```

This is essential for parsing the documents that the Raspberry Pi has scanned and sent to the database itsef. This **must** be replaced with the proper directory based on where the Web Application is deployed.

### VENV

An additional point to this, is properly setting up the virtual environment. After cloning the repository, we must then set up the virtual environment before setting up the server.

Navigate to the folder where *requirements.txt* is located, and then execute the following code after the creation of the venv

Create a virtual environment:
`python -m venv dobavenv`

Install required dependencies:
`pip install -r requirements.txt`

Then proceed to the Server Setup...



### 3. SETTING UP THE SERVER (MASTER)
This topic will be further subdivided into multiple parts as this covers the deployment of the Web Application. This covers NGINX configuration, GUNICORN socket and service, as well as SSH configurations, and problems that might arise due to file permissions.


### NGINX

Navigate to `etc/nginx/sites-available` and create a file called IMO_Doba using the command on the directory above

```
sudo nano IMO_Doba
```

This file must contain 

```
server {
    listem 80;
    server_name 192.168.1.14  #REPLACE THIS WITH IP GIVEN BY VIRTUALBOX

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /home/el14s/IMO_Doba/; # MAKE SURE TO HAVE PROPER PERMISSIONS
    }

    locaton / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }



}


```

**CREATING A SYMBOLIC LINK**

After creating the link in sites-available we must next create a *symbolic link* in sites-enabled. This is done by executing the command

```
ln -s /etc/nginx/sites-available/IMO_Doba IMO_Doba
```


**NGINX startup** 
NGINX should also be enabled on system startup

`sudo systemctl enable nginx`


### GUNICORN

Gunicorn once installed, navigate to `etc/systemd/system` and create a new file called *gunicorn.service*. 

```
sudo nano etc/systemd/system/gunicorn.service
```

*gunicorn.service* must contain the following code:

```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=el14s #REPLACE WITH IMO USER
Group=www-data
WorkingDirectory=/home/el14s/IMO_Doba #REPLACE WITH WORKDIR
ExecStart=/home/el14s/dobavenv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \ 
          --bind unix:/run/gunicorn.sock \
          IMO_Doba.wsgi:application

[Install]
WantedBy=multi-user.target

```

**After this, create a new file for the socket**

```
sudo nano etc/systemd/system/gunicorn.socket
```

*gunicorn.socket* must contain the following code:

```
[Unit]
Description=Running IMO Docubase
[Socket]
ListenStream=/run/gunicorn.sock
[Install]
WantedBy=sockets.target
```

### SSH
**IT IS IMPORTANT THAT OPENSSH IS INSTALLED FIRST** 

Generate a public & private key first:
```
ssh-keygen -t rsa
```

Copy this ID to the Server by:

```
ssh-copy-id {username}@{PC-IP}
```

Test the connection using:

```
ssh {username}@{PC-IP}
```

SSH should now work without password authentication for every file transfer.

### MISCELLANEOUS 

These are just miscellaneous setups that need to be modified incase of encountering an issue.

1. FIREWALL CONFIG
Diagnose firewall and allow port 80 (HTTP) and port 22 (SSH) in the firewall. 
```
sudo ufw status
```

Allow by:

```
sudo ufw allow 80

AND

sudo ufw allow 22
```

2. FILE PERMISSIONS
Files may not have the proper user group, or permissions. Usually can be fixed by 

```
sudo chmod 755 -R /home/...
```

3. PROPERLY SET DESTINATION FOLDER IN RASPI
Located in *preprocessed.py* change the username and IP depending on IP given by virtual machine.



tbc

-el14s