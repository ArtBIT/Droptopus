# Droptopus
![Droptopus Logo](/droptopus/assets/droptopus.png)

Droptopus is a drag'n'drop receiver, which routes dropped objects to the designated actions.

# Dependencies
 - PyQt4
 - Python Magic 

# Installation

## Install Dependencies:
 - Install python-qt4 globaly:
    `sudo apt-get install python-qt4`

 - Create symbolic link of PyQt4 to your virtual env 
    `ln -s /usr/lib/python2.7/dist-packages/PyQt4/ .env/lib/python2.7/site-packages/`

 - Create symbolic link of sip.so to your virtual env
    `ln -s /usr/lib/python2.7/dist-packages/sip.so .env/lib/python2.7/site-packages/`

## Run the Droptopus App from source
 - Clone the repo:
 `git clone https://github.com/ArtBIT/Droptopus`
 - Run it:
 `cd Droptopus && ./bin/droptopus`

## ...Or build the binary yourself
 - Install the dependencies
 - Clone the repo:
 `git clone https://github.com/ArtBIT/Droptopus`
 - Build the binary:
 `cd Droptopus && bash build.sh`
 - Copy the binary to your bin path:
 `cp dist/droptopus /usr/local/bin`

## Credits

This project uses awesome icons from [http://icons8.com](Icons8)

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

