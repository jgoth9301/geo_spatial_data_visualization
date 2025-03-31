# Scrape the Web

**Scrape the Web** is a Python-based project designed to automate the extraction of data from various online sources. It utilizes web scraping techniques to gather information, which can then be processed and analyzed for various applications.

## Features

- **Automated Data Extraction**: Seamlessly scrape data from specified websites.
- **Data Processing**: Clean and transform the extracted data for analysis.
- **Scheduled Execution**: Automate the scraping process to run at specified intervals.

## Prerequisites

Before setting up and running this project, ensure you have the following installed:

- **Python 3.10** or higher
- **pip** (Python package installer)
- **Git** (for cloning the repository)

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/jgoth9301/scrape_the_web.git
   ```

2. **Navigate to the Project Directory**:

   ```bash
   cd scrape_the_web
   ```

3. **Set Up a Virtual Environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

4. **Install Dependencies**:

   Ensure all required Python packages are installed:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Before running the scripts, configure the necessary settings:

1. **Environment Variables**:

   Create a `.env` file in the project root directory to store sensitive information such as API keys or database credentials. For example:

   ```env
   API_KEY=your_api_key_here
   DB_CONNECTION_STRING=your_database_connection_string_here
   ```

2. **Logging**:

   Configure logging settings in the `logging.conf` file to control the verbosity and format of log messages.

## Usage

The project contains several Python scripts that perform specific tasks. Execute them in the following order:

1. **news_finance_api.py**: Fetches financial news data from specified APIs.

   ```bash
   python news_finance_api.py
   ```

2. **news_general_api.py**: Retrieves general news data from various sources.

   ```bash
   python news_general_api.py
   ```

3. **x_api.py**: Interacts with the 'X' API to collect relevant data.

   ```bash
   python x_api.py
   ```

4. **share_price_api.py**: Gathers share price information from financial platforms.

   ```bash
   python share_price_api.py
   ```

5. **sentiment_analysis.py**: Performs sentiment analysis on the collected news data.

   ```bash
   python sentiment_analysis/sentiment_analysis.py
   ```

6. **data_mapping.py**: Maps and integrates the processed data into a unified format.

   ```bash
   python data_visualization/data_mapping.py
   ```

7. **download_preparation.py**: Prepares the final dataset for download or further analysis.

   ```bash
   python data_visualization/download_preparation.py
   ```

## Scheduling with GitHub Actions

To automate the execution of these scripts daily at 23:00 CET, set up a GitHub Actions workflow:

1. **Create a Workflow File**:

   In the `.github/workflows` directory, create a file named `ci.yaml` with the following content:

   ```yaml
   name: Daily Data Scraping

   on:
     schedule:
       - cron: '0 22 * * *'  # 23:00 CET (22:00 UTC)
     workflow_dispatch:

   jobs:
     run-scripts:
       runs-on: ubuntu-latest

       steps:
         - name: Checkout Repository
           uses: actions/checkout@v3

         - name: Set Up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.10'

         - name: Install Dependencies
           run: |
             python -m pip install --upgrade pip
             pip install -r requirements.txt

         - name: Execute Scripts
           run: |
             python news_finance_api.py
             python news_general_api.py
             python x_api.py
             python share_price_api.py
             python sentiment_analysis/sentiment_analysis.py
             python data_visualization/data_mapping.py
             python data_visualization/download_preparation.py
   ```

2. **Commit and Push**:

   Add, commit, and push the workflow file to your repository:

   ```bash
   git add .github/workflows/ci.yaml
   git commit -m "Add GitHub Actions workflow for daily data scraping"
   git push
   ```

This setup ensures that the scripts run automatically every day at 23:00 CET.

## Contributing

Contributions to **Scrape the Web** are welcome! If you have suggestions, improvements, or encounter issues, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

*Note: Ensure you have the necessary permissions and adhere to the terms of service of any websites or APIs you are scraping data from. Unauthorized scraping can violate legal and ethical guidelines.*