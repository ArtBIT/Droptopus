# Droptopus
![Droptopus Logo](/droptopus/assets/droptopus.png)

Droptopus is a drag'n'drop receiver, which routes dropped objects to the designated actions.

# Dependencies 
 - python3
 - pyqt5

# Installation
 - Clone the repo:
 `git clone https://github.com/ArtBIT/Droptopus`
 - Create python3 virtualenv
 `pip install virtualenv # if it's not installed`
 `virtualenv -p python3 env`
 - Install Dependencies:
 `pip3 install -r requirements.txt`
 - Activate virtual environment
 `source env/bin/activate`
 - Run it:
 `python3 droptopus/main.py &`

# Build binary from source
PyInstaller does not yet support Python 3.6, but the current development branch does. In order to build this project you will need to install the PyInstaller development build:
`pip install git+https://github.com/pyinstaller/pyinstaller.git`
And then run the build script:
`./build.sh`

## Acknowledgements

Droptopus uses

- [Nokia's](http://www.nokia.com): [Qt](http://qt.nokia.com)

- [Riverbank Computing Limited's](http://www.riverbankcomputing.co.uk): [SIP](http://www.riverbankcomputing.co.uk/software/sip/intro)

- [Riverbank Computing Limited's](http://www.riverbankcomputing.co.uk): [PyQt5](http://www.riverbankcomputing.co.uk/software/pyqt/intro)

- [Icon8's](http://icons8.com): [awesome icons](http://icons8.com)

Thanks!


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

