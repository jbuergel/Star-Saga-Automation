Star-Saga-Automation
====================

A python/Virtual Box based solution for running Star Saga using a Google chat bot.  When started, it will invoked a VirtualBox VM running Star Saga, allowing players to play the game remotely, sending commands through the chat interface and seeing the results back on their chat window.  There's also a Google Maps version of the game map included.

The automation solution has a few parts.  First is a Google chat robot that responds to remote commands from authenticated users.  It requires a config file in order to operate, which contains a list of users as well as a set of credentials for the Google account you are going to use.  It looks for a config.yaml in the same directory as StarSagaBot.py.  Contents should look like this:

    discordtoken: discord_token 
    vboxpath: C:/Program Files/Oracle/VirtualBox
    users:
        - discord_id_0
        - discord_id_1

Note that you will need to create your own bot using Discord and get the token from them so your bot can sign in (https://discord.com/developers/applications). The users who are going to play need to be added to the users array in config.yaml. Finally, the automation needs to know where the VBoxManage.exe executable lives so it can take screen shots. I ran this thing on Windows, I suppose it would work on other platforms.

In order to operate, Oracle's VirtualBox (https://www.virtualbox.org/) must be installed on the host box. In addition, the SDK needs to be installed and setup. This bot makes use of some Python dependencies: Pillow, pyqt5, discord, and pyyaml, all installable via pip. Finally, it expects the VBoxManage.exe executable to be in the same directory as StarSagaBoy.py, to facilitate taking screen shots.

Usage
====================
StarSagaBot.py can simply be run with no options.  It will read its config from config.yaml and start the VirtualBox instance named Dos622.  A sample image is included with this repo, and should be added to VirtualBox.  The image contains StarSaga already installed. Before running the automation, you should start the image, make sure that it runs (you might need to re-bind the network adapater to get it to stop complaining), and make sure that the shared directory that it uses exists (by default, C:\temp\vb, but you can change that). During this first run, you should also create a new game and add the characters you want to play in it.

trainer.py is a training program used to train the custom-built OCR module used to translate the 40x25 DOS screen into characters.  If any unknown characters are found during play, a tile is saved in the tiles directory. Running trainer.py allows you to translate the characters, with the new data saved out to trained_data.

splitter.py is a program used to split a screen shot from VirtualBox and split it into a bunch of tiles.  It's probably not really necessary any more.

Map
====================
This repo also includes the StarSaga map, implemented as a quick-and-dirty Google Map.  Just install it on a web server.  It stores its data using HTML5 local storage, so you'll need to keep accessing things on one machine.
