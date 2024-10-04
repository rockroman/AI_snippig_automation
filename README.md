# SnippingTool-AI automation

## Overview

### This project is a Snipping Tool AI Automation that helps users capture specific areas of their screen and automatically extract and process text information from these screenshots using OpenAI's gpt-4o-mini model and pytesseract python library . The tool is built to extract specific data points from different screenshots and store the processed information into a Google Sheets document. This can be particularly useful for tasks that require frequent capturing and analysis of on-screen data, like monitoring metrics from dashboards or reports.

### Features

- Snip and Save: Capture specific screen regions with a snipping tool integrated into a PyQt5 GUI.
- Automated Text Extraction using OCR, pytesseract package
- Making API call :Extract text from the captured screenshots if relevant is passed to OpenAI's gpt-4o-mini model for further processing
- Specific Prompts: The tool adapts its text extraction based on the prompts and type of data expected from each screenshot.
- Google Sheets Integration: Automatically store extracted data into a predefined Google Sheets document.
- Dynamic Instructions: Provides users with dynamic instructions on what to capture next, based on the sequence of snips.

## Installation

### Clone the repository:

```
git clone https://github.com/rockroman/AI_snippig_automation.git

```

### Install required dependencies:

```
pip install -r requirements.txt
```

Setup Google Sheets API:

### Obtain a credentials.json file from the Google Cloud Console and place it in the project directory.

### Set up OpenAI API Key:

Replace the api_key variable in the helper_ai.py file with your OpenAI API key.
Usage

### Run the Application:

```
python tool_class.py
```

### Capture Screenshots:

Follow the on-screen instructions to capture specific areas of your screen. The instructions will guide you on what data to capture next.
The tool allows up to 4 snips in a single session.

### Automatic Processing:

After each snip, the tool automatically processes the image, extracts relevant data, and stores it in the connected Google Sheets document.

## Bundle code to desktop app(pyinstaller)

To bundle the project into a standalone desktop application, you can use PyInstaller.

1. Install PyInstaller:

```
 pip install pyinstaller
```

2. Create the Executable: Navigate to your project directory and run the following command

```
pyinstaller --onefile --windowed sinpping_tool.py
```

3. Include Additional Files: since project depends on external files like credentials.json, you need to include them using the --add-data flag

```
pyinstaller --onefile --windowed --add-data "credentials.json;." sinpping_tool.py
```

4. Running the Executable

- Once you've bundled your project using PyInstaller, you can run the generated executable directly from the dist directory

```

```

## Code Structure

- tool_class.py: Contains the main GUI logic and handles user interactions for capturing screenshots.
- ai_class.py: Handles image encoding, sends the image to the OpenAI API for text extraction, and processes the extracted data.
- worksheet_class.py: Manages the connection to Google Sheets and updates the spreadsheet with the extracted data.

### Notes

The tool currently supports capturing and processing up to 4 different types of screenshots.
The AI processing is tailored to extract specific metrics as defined in the process_image function. You may customize this function for different use cases.
Ensure your Google Sheets API credentials are correctly set up to avoid issues with data storage.

### Possible Future Enhancements

- Expand Supported Snips: Increase the number of supported snip types beyond the current limit of 4, depending on specific use case.
- Customizable Prompts: Allow users to customize the prompts for text extraction directly through the GUI.
