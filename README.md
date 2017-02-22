# Categories Backup Tool

Categories Backup Tool is a tool to.. you guessed it, backup your categories. On Steam.
Those things:
![Categories](https://raw.githubusercontent.com/DanielZa2/CategoriesBackupTool/master/Images/Im1.png)

## What does the tool do excatly?

It gives you 3 options. Backup, Restore and Export.

1. Backup allows you to save a copy of the file that stores your steam category information.
2. Restore allows you to return the categories to the state they were in before the backup.
3. Export allows you to create a human readable (nicely looking) file containing all the information about your categories.

![Export output](https://raw.githubusercontent.com/DanielZa2/CategoriesBackupTool/master/Images/Im2.png)

## How does it work?

The tool reads a file in the steam directory called sharedconfig.vdf which contains all the information it needs. This file contain the id number of all the games / apps in the different categories. The backup and restore options are essentially just copying sharedconfig.vdf. The export option reads the file, extracts all the relevant information, matches the ids with names pulled from a local file or from the net and presents it in a nice format.

## Does it support Mac / Linux?
It should work but I don't have a machine to test it on, so you tell me.

## Are there two versions I can download? Which one I should get?
You have two options. You can either download the python version, or the slightly weird windows exe version. If you're not sure get python and the python version, but you'll have to install python on your computer. You can get it from https://www.python.org/.
The exe version was auto-generated using cx_Freeze from the python code.

## FAQ

### Something went wrong, it displays many games as (AppID: <id_number>).
Seems that it can't pull the right name for this steam application. In case of new games, you can delete Applist.txt from the program folder and it will pull new one from the web.

### Is it an official tool? Does it somehow related to Valve?
Nope. **No** endorsement whatsoever on their part. Just something I wrote for myself and decided to post online.

### This program deleted my steam library / self-destructed my computer / initiated a machine upraising. 
I'm sorry to hear that, but you're using this program at your own risk and I'm taking **no** responsability for **anything** it does. It works fine on my computer. Sometimes.

### You take no responsability for potentional machine upraising caused by your software?
All praise our new machine overlords.

### Why python / python3?
Never written anything at python before. Seemed like a good place to start.

### Your code is really unpythonic. 
Never written anything at python before. Seemed like a good way to start.
But seriously feel free contribute and change it.

