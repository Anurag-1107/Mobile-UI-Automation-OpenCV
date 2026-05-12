# Android UI Automation using Python, ADB and OpenCV

## Overview
This project is a Python-based Android UI automation tool that uses Android Debug Bridge ADB and OpenCV template matching to detect UI elements on an Android device or emulator and perform automated tap actions.

## Features
- Captures Android screen using ADB
- Detects UI elements using OpenCV template matching
- Performs automated tap actions on detected elements
- Supports multiple template images
- Includes logging for workflow tracking
- Can repeat workflows for a user-defined number of cycles

## Technologies Used
- Python
- OpenCV
- NumPy
- Android Debug Bridge ADB
- Template Matching
- Mobile UI Automation

## How It Works
1. The script connects to an Android device using ADB.
2. It captures the current screen using adb screencap.
3. OpenCV compares the screenshot with predefined template images.
4. If a matching UI element is found, the script calculates its center coordinates.
5. ADB sends a tap command to interact with the detected UI element.
6. The workflow repeats for the selected number of cycles.

## Installation

```bash
pip install -r requirements.txt