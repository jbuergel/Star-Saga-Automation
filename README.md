Star-Saga-Automation
====================

A python/Virtual Box based solution for running Star Saga using a Google Talk bot.  When started, it will invoked a VirtualBox VM running Star Saga, allowing players to play the game remotely, sending commands through the Google Talk interface and seeing the results back on their chat window.  There's also a Google Maps version of the game map included.

The automation solution has a few parts.  First is a Google Talk robot that responds to remote commands from authenticated users.  It requires a config file in order to operate, which contains a list of users as well as a set of credentials for the Google Talk account.  It looks for a creds.yaml in the same directory as StarSagaBot.py.  Contents should look like this:

    jid: username@gmail.com  
    password: google_password  
    users:  
        - name: first  
          password: first_password  
        - name: second  
          password: second_password  

In order to operate, Oracle's VirtualBox (https://www.virtualbox.org/) must be installed on the host box. In addition, the SDK needs to be installed and setup. This bot makes use of some Python dependencies: Pillow, pyqt5, slixmpp, and pyyaml, all installable via pip.

Usage
====================
StarSagaBot.py can simply be run with no options.  It will read its config from creds.yaml and start the VirtualBox instance named Dos622.  A sample image is included with this repo, and should be added to VirtualBox.  The image contains StarSaga already installed.

trainer.py is a training program used to train the custom-built OCR module used to translate the 40x25 DOS screen into characters.  If any unknown characters are found during play, a tile is saved in the tiles directory. Running trainer.py allows you to translate the characters, with the new data saved out to trained_data.

splitter.py is a program used to split a screen shot from VirtualBox and split it into a bunch of tiles.  It's probably not really necessary any more.

For the automation to work properly, it expects the virtual machine to have been run at least once, so it's available to be started. You should run the game once, create a new game, and add the characters that will be playing, and then quit out, so the game is in a state to resume.

Map
====================
This repo also includes the StarSaga map, implemented as a quick-and-dirty Google Map.  Just install it on a web server.  It stores its data using HTML5 local storage, so you'll need to keep accessing things on one machine.
