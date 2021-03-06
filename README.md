# Unicron

![Interface](https://raw.githubusercontent.com/form-follows-function/unicron/master/ui.png)


## Unicron is an interactive utility to help manage and edit background processes on macOS. Enhancing automation and security. 

### Background processes are called daemons, agents and jobs, or crons within the Unix world. Apple deprecated the Unix crontab process in MacOS X 10.4 Tiger and replaced it with the system's launchd process. They work on different user levels such as the current user, administrator or system. Unicron aims to these handle background processes, strengthens security and simplifies repeating tasks.



## Building from source

### Requirements

##### Easy Installation:
$ `pip3 install -r requirements.txt`



##### Manual Installation:
$ `pip3 install pyobjc   # https://bitbucket.org/ronaldoussoren/pyobjc/src/default/`

$ `pip3 install py2app   # https://py2app.readthedocs.io/en/latest/`

$ `pip3 install launchd  # https://github.com/infothrill/python-launchd`


Additionally download the vanilla framework (https://github.com/robotools/vanilla) and install it via:

$ `git clone https://github.com/robotools/vanilla.git`

$ `cd vanilla && python setup.py install`


For deploys Apple's Xcode command line developer tools are required too, which can be installed with:

$ `xcode-select --install` # Xcode command line developer tools


## Building and deploying
Building the app in Alias-mode allows you to keep a development environment:

$  `python3 setup.py py2app -A`


For deploys use the build command without the `-A` "Alias" parameter:

$  `python3 setup.py py2app`



## Running the app in debug mode

The vanilla tools allow to run the app for testing without any compilation needed. Simply run:

$ `python3 test.py`



## Roadmap

The roadmap can be found at the [Kanban board](https://github.com/form-follows-function/unicron/projects/1)


## Background information

$  `man launchctl`

$  `man launchd`

$  `man launchd.plist`

- http://www.launchd.info
- http://launched.zerowidth.com



## Disclaimer

#### Unicron is provided 'as is' without warranty of any kind. The provider makes no representations of any kind converning the safety, suitability, inaccuracies or other harmful dangers in the use of this software. There are inherent dangers in the use of any software and you are solely responsible for using the software and making changes to your system.

