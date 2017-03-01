# Categories Backup Tool

Categories Backup Tool is a tool to.. you guessed it, backup your categories. On Steam. Those things:

![Categories](https://raw.githubusercontent.com/DanielZa2/CategoriesBackupTool/master/Images/Im1.png)

## What does the tool do?

The tool gives you 3 options. To backup, restore and export your categories. Backup and restore are self explanatory. You create a file that contains all the information on your current categories which you can letter return to. The restore option does not delete anything and can be reversed if something goes wrong. Export creates a human readable (nicely looking) file containing the same information.

![Export output](https://raw.githubusercontent.com/DanielZa2/CategoriesBackupTool/master/Images/Im2.png)

## How does it work?

The tool reads a file in the steam directory called *sharedconfig.vdf* which contains all the information it needs. This file contain the application id numbers of your games and  the different categories to which they belong. The backup option copy the "tags" key for each game and stores it in a JSON file. The restore option puts this data back into the file while preserving any other changes. It renames the current *sharedconfig.vdf* instead of deleting it so that it could be reversed, in cae something goes wrong.
The export option reads the file, extracts all the relevant information, matches the ids with names pulled either from a local file or from the net and presents it in a nice format.

## Does it support Mac / Linux?
It should work but I don't have a machine to test it on, so you tell me.

## There are two versions available  out there to download. Which one should I get?
You have the cross-platform python version and the 64bit Windows executable version.

1. Getting the python version will require having python installed on your system, but it (probably) will run on any platform that runs python. You can get python from:  https://www.python.org/ 
2. If you're using 64bit windows, you can get an ready to be used executable file. This version was automatically generated from the python code using pyinstaller. It should be possible to do the same on any other platform.

## FAQ

### Something went wrong, the tool displays too many games as (AppID: \<id_number\>).
Seems that it can't pull the right name for this steam application. In case of new games, you can delete Applist.txt from the program folder and it will pull new one from the web.

### Is it an official tool? Does it somehow related to Steam or Valve?
Nope. **There is no endorsement from Valve for anything in this project.** Just something I wrote for myself and decided to post online.

### This program deleted my steam library / self-destructed my computer / initiated a machine upraising. 
I'm sorry to hear that, but you're using this program at your own risk and I'm take **no** responsibility for **anything** it does. It works fine on my computer. Sometimes.

### You really take no responsibility for potential machine upraising caused by your software?
All praise our new machine overlords.

### Why python / python3?
Never written anything in python before. Seemed like a good place to start.

### Your code is really unpythonic. 
Never written anything at python before. Seemed like a good start.

But seriously feel free contribute and suggest improvements.

