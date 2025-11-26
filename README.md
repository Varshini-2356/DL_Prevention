#  File Monitoring & SMS Alert System using Twilio

This project monitors selected text files for any real-time changes.  
Whenever a file is modified, the program detects inserts, deletes, and replacements, and sends an SMS notification using the **Twilio API**.

##  Project Overview

This Python automation script:

- Monitors specific files continuously  
- Detects modifications using the `watchdog` library  
- Identifies the exact text changes using `difflib`  
- Sends an SMS alert through Twilio API  
- Includes error handling and retry logic  

##  Technologies Used

| Technology | Purpose |
|-----------|---------|
| **Python** | Programming language |
| **Twilio API** | SMS delivery |
| **Watchdog** | File change monitoring |
| **Difflib** | Compare text differences |
| **OS, Time, Socket** | System functions |

## Installation

Install all required packages:
bash
pip install -r requirements.txt
