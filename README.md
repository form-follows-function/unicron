# Unicron


#### Unicron is an interactive utility application to help manage and edit background processes on macOS which are handled by the system's launchd process. 

##### These jobs are called daemons and agents and work on different user levels such as the current user, administrator or system. Unicron aims to handle background processes, strengthen security and simplify repeating tasks.



##### BUILDING FROM SOURCE

The following modules have to be installed via pip:

- py2app    (https://py2app.readthedocs.io/en/latest/)
- vanilla   (https://github.com/typesupply/vanilla)
- launchd   (https://github.com/infothrill/python-launchd)

Then you can start building the app:
`$ python py2app setup.py -A`



##### RUNNING THE INTERFACE IN DEBUG MODE:

The vanilla tools allow to run the app for testing without any compilation needed. Simply run:

`$ python debug.py`



##### ROADMAP

Currently working features are:

- Grouping and listing daemons by user or system
- Displaying the daemon's status
- Loading and unloading daemons
- Revealing the selected daemon in the Finder

For future releases the following features are planned:

- Modifying existing daemons such as:

  - Name and Label

  - Program

  - Scheduling

  - Advanced settings

- Creation of custom daemons



##### DISCLAIMER

Unicron is provided 'as is' without warranty of any kind. The provider makes no representations of any kind converning the safety, suitability, inaccuracies or other harmful dangers in the use of this software. There are inherent dangers in the use of any software and you are solely responsible for using the software and making changes to your system.



##### BACKGROUND INFORMATION

- https://docs.chef.io/resource_launchd.html
- http://www.launchd.info
- http://launched.zerowidth.com
