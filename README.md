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

## Credits

This project uses awesome icons from [http://icons8.com](Icons8)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

