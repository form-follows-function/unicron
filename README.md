# Unicron

![Interface](https://raw.githubusercontent.com/form-follows-function/unicron/master/ui.png)


## Unicron is an interactive utility to help manage and edit background processes on macOS. Enhancing automation and security. 

### These processes are called daemons, agents and jobs, or crons within the Unix world. Apple deprecated the Unix' crontab process in 10.4 and replaced it with the system's launchd process. They work on different user levels such as the current user, administrator or system. Unicron aims to handle background processes, strengthens security and simplifies repeating tasks.



## Building from source

### Requirements

##### Easy Installation:
$ `pip install -r requirements.txt`


##### Manual Installation:
$ `pip install pyobjc   # https://bitbucket.org/ronaldoussoren/pyobjc/src/default/`

`pip install py2app   # https://py2app.readthedocs.io/en/latest/`

`pip install launchd  # https://github.com/infothrill/python-launchd`


Additionally download the vanilla framework (https://github.com/robotools/vanilla) and install it via:
`$ python setup.py install`


Then you can start building the app:
 `$ python py2app setup.py -A`


## Running the app in debug mode

The vanilla tools allow to run the app for testing without any compilation needed. Simply run:
`$ python debug.py`



## Roadmap

- [x] Grouping and listing daemons by user or system
- [x] Displaying the daemon's status
- [x] Loading and unloading daemons
- [x] Revealing the selected daemon in the Finder
- [ ] Displaying an application icon
   - [ ] Easteregg
- [ ] Refactor the code to use QT as GUI library
- [ ] Providing builds (no GitHub CI/CD) with md5 checksum
- [ ] Modifying existing daemons such as:
  - [ ] Name and Label
  - [ ] Program
  - [ ] Scheduling
  - [ ] Advanced settings
- [ ] Creation of custom daemons
- [ ] UX improvements



## Background information

- https://docs.chef.io/resource_launchd.html
- http://www.launchd.info
- http://launched.zerowidth.com


## Disclaimer

#### Unicron is provided 'as is' without warranty of any kind. The provider makes no representations of any kind converning the safety, suitability, inaccuracies or other harmful dangers in the use of this software. There are inherent dangers in the use of any software and you are solely responsible for using the software and making changes to your system.

