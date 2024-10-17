# imageCLX - README

## Overview

imageCLX is a tool designed to automate clicking on specified graphical elements within your main monitor by using image recognition. It helps automate repetitive tasks by identifying GUI elements and clicking on them for you.

## Download
https://github.com/VOWSI/imageCLX/releases/tag/v1.0

  Virus Total (does flag unsure how to resolve):
  https://www.virustotal.com/gui/file/ef9489dbcb919c1c6c9e20fa94b3f355326e9004e80024db5cf4fe03ca84d3da/behavior

## Features

- **Upload Target Image**: Allows you to upload an image of the target element to click.
- **Adjustable Detection Threshold**: Set a detection threshold to control the sensitivity of image matching.
- **Toggle Scanning**: Start and stop scanning with a button or F1 key.
- **Visual Detection Feedback**: Shows the area detected, highlighted in red.

## Installation

### Requirements

- Python 3.x
- Required Python libraries:
  - `opencv-python`
  - `numpy`
  - `pyautogui`
  - `pydirectinput`
  - `keyboard`
  - `Pillow`
  - `tkinter` (usually included with Python on Windows)

## How to Use

1. **Upload Image**: Click the "Upload Image" button to select an image of the target element. This image will be used to identify and click the matching area in Roblox.
2. **Set Threshold**: Enter a threshold value (default is 0.8) to control how closely the target matches. A higher value (closer to 1) increases accuracy but may miss valid matches.
3. **Start Scan**: Click "Start Scan" or press F1 to begin scanning. The tool will look for the target image in real-time and click it when found.
4. **Stop Scan**: Press F1 again to stop scanning.
5. **Quit**: Press F2 or click the close button to exit the program.

## Notes

- The **threshold value** should be between 0.0 and 1.0. A value below 0.8 may produce false positives, while a higher value increases accuracy but may miss valid matches.
- While scanning is active, the threshold cannot be adjusted.
- Scuffed project with CHATGPT

## Disclaimer

Use this tool responsibly and in accordance with the terms of service of the platforms you interact with. Misuse of automation tools can lead to account restrictions or bans.
