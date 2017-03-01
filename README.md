# Categories Backup Tool

Categories Backup Tool is a tool to.. you guessed it, backup your categories. On Steam. Those things:

![Categories](https://raw.githubusercontent.com/DanielZa2/CategoriesBackupTool/master/Images/Im1.png)

## What does the tool do?

With the tool you can backup, restore and export your categories. Backup and restore are self explanatory. When backuping you create a file containing all the information on your current categories. You can restore your categories to the state they were before the backup. It is worth noting that restoring does not permanently delete anything and can be reversed if something gone wrong. Finally by exporting you creates a human readable (nicely looking) file containing all the above mentioned information.

![Export output](https://raw.githubusercontent.com/DanielZa2/CategoriesBackupTool/master/Images/Im2.png)

## How does it work?

The tool reads a file in the steam directory called *sharedconfig.vdf*. This file contains all the information about your categories (together with other stuff). Specifically the file contain the application id numbers of your games and  the different categories to which they belong. The backup option copy the "tags" key for each game and stores it as a JSON file. The restore option writes this data back into the file while preserving any other changes that happen since the backup. The original *sharedconfig.vdf*, just before the restore, is not deleted. It is stored on the same folder under a different name so that the restore process could be reversed at any time. The export option reads *sharedconfig.vdf*, extracts all the relevant information, matches the ids with names pulled either from a local file or from the net and presents it in a nice format.

## Does it support Mac / Linux?
It should work but I don't have a machine to test it on, so you tell me.

## There are two versions available  out there to download. Which one should I get?
You have the cross-platform python version and the 64bit Windows executable version.

1. Getting the python version will require having python installed on your system, but it (probably) will run on any platform that runs python. You can get python from:  https://www.python.org/ 
2. If you're using 64bit windows, you can get the ready-to-be-used executable file. This version was automatically generated from the python code using pyinstaller. It should be possible to do the same on any other platform, given a machine that runs it. Contributions are welcome.

## FAQ

### Something went wrong, the tool displays too many games as (AppID: \<id_number\>).
Seems that it can't find the right name for this steam application. It is possible that the game was added to steam after Applist.txt was generated. You can delete the file and a new one will be pulled from the web. If the issue happens with older games that weren't removed from steam... it shouldn't. File a bug report.

### Is it an official tool? Does it somehow related to Steam or Valve?
No! **There is no endorsement whatsoever from Valve for anything in this project.** Just something I wrote for myself and decided to post online.

### This program deleted my steam library / self-destructed my computer / initiated a machine upraising. 
I'm sorry to hear that, but you're using this program at your own risk and I'm take **no responsibility for anything it does**. It works fine on my computer. Sometimes.

### You really take no responsibility for potential machine upraising caused by your software?
All praise our new machine overlords.

### Why python / python3?
Never written anything in python before. Seemed like a good place to start.

### Your code is really unpythonic. 
Never written anything at python before. Seemed like a good start.

But seriously feel free contribute and suggest improvements.

