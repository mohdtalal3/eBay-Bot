# eBay Bot

A desktop application that automates eBay product search and viewing using proxy connections.

## Features

- Automated eBay product search and viewing
- Proxy support for anonymized connections
- Configurable search parameters:
  - Custom search keywords
  - Specific product selection from search results
  - Multiple run scheduling
- User-friendly GUI interface built with PyQt5
- Real-time status updates

## Requirements

- Python 3.6+
- SeleniumBase
- PyQt5
- Internet connection
- Valid proxy credentials (required)

## Installation

1. Clone this repository or download the ZIP file
2. Create a virtual environment (recommended):
   ```
   python -m venv myenv
   ```
3. Activate the virtual environment:
   - Windows: `myenv\Scripts\activate`
   - macOS/Linux: `source myenv/bin/activate`
4. Install the required dependencies:
   ```
   pip install seleniumbase PyQt5
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```
2. Enter your proxy information in the format `username:password@host:port`
3. Set your search parameters:
   - Enter a search keyword
   - Select the product index (position in search results)
   - Choose the number of runs
4. Click "Start Bot" to begin the automation
5. Monitor the status in the log window
6. Use "Stop Bot" to interrupt the process

## How It Works

The bot uses SeleniumBase to automate a browser session that:
1. Connects through your specified proxy
2. Navigates to eBay.com
3. Searches for your specified keyword
4. Selects a product based on your index preference
5. Views the product details page
6. Repeats the process for your configured number of runs



## License

This project is available under the MIT License. 