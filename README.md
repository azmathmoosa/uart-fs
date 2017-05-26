# uart-fs
A File Management Utility for working with Linux based boards like Raspberry Pi, NanoPi, OpenWRT routers etc over serial (UART) console


## The Intention
I was sick and tired of not being able to freely transfer files over uart when working with Nanopi and Linkit Smart - these are linux based boards with good console interface.  In some of my projects, there was no internet connection and hence, SSH wasn't an option.  Thus, I decided to write a python script that would transfer files using *cat* and *echo* commands.  I began enjoying it and decided to write a full fledged python app with web based gui using *bottle* and more useful features like copy and move that would make life easier for file management.  I also went on to implement a websocket based serial console in the web browser for quick debugging and running custom commands without having to switch to other terminal apps.

## Screenshots

![Choose serial port](https://github.com/azmathmoosa/uart-fs/screenshots/initialize.png "Choose serial port")
![The main interface](https://github.com/azmathmoosa/uart-fs/screenshots/interface.png "The main interface")
![Supported Functions](https://github.com/azmathmoosa/uart-fs/screenshots/functions.png "Supported Functions")

## How To Use

* Clone the repo
* Install dependencies - pyserial, bottle-websocket (ex: pip install bottle-websocket)
* Run uartfs.py (Python 3)
* Open browser and point to localhost:5000

I need to add upload file feature.  Please test with your device and let me know if some things need to be fixed.

## Thanks To
* https://github.com/joni2back/angular-filemanager
* https://github.com/zeekay/bottle-websocket
