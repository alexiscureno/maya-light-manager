# Lighting Manager Tool
### maya-light-manager

The Lighting Manager is a graphical user interface (GUI) tool for Maya that allows users to easily create, view, save, and import various types of lights to a scene. 
This README provides an overview of the features and functionality of the Lighting Manager tool, as well as instructions for how to use it.

## Getting Started

### Requirements
* Autodesk Maya 2023 or later
* PyQt5

## Installation
To install the Lighting Manager tool, follow these steps:

1. Download the "lighting_manager.py" file and the "light.ui" file from the repository.
2. Save these files to a directory of your choice.
3. Open Maya and go to the Script Editor (Window > General Editors > Script Editor).
4. In the Script Editor, go to File > Load Script... and select the "lighting_manager.py" file.
5. Once the script has loaded, run the following command in the Python console:

## Features
The Lighting Manager GUI provides the following features:

### Light creation
The user can create a new light by selecting the desired light type from the drop-down menu and clicking the "Create" button. The new light will appear in the list of lights in the GUI.

### Light viewing
The user can view all the lights in the scene in the list of lights in the GUI. The list displays the name of the light and its type.

### Light editing
The user can edit the properties of a light by clicking on the corresponding checkbox in the list of lights. This will open a window where the user can edit the properties of the light.

### Light saving
The user can save the properties of all the lights in the scene to a file by clicking the "Save" button. The file will be saved in a directory specified by the user.

### Light importing
The user can import the properties of lights from a file by clicking the "Import" button. The user will be prompted to select the file to import. Once the file is selected, the properties of the lights in the file will be added to the scene.

### Light solo mode
The user can enable solo mode for a light by clicking on the corresponding checkbox in the list of lights. When solo mode is enabled for a light, all other lights in the scene will be disabled.
