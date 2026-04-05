# AI-Based Sentiment Analysis of Financial News Articles

This project performs sentiment analysis on financial news articles to predict market share impacts. It scrapes articles from [Google News](https://news.google.com/) and [Onvista.de](https://www.onvista.de/), analyzes them using a pre-trained FinBERT model (a BERT-based model fine-tuned for financial sentiment), and stores results in a MySQL database. A frontend application displays articles and sentiment results.

## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Project Description

This project consists of five main components:

- **Web Scraper**: Scrapes financial news articles from specified websites.
- **Sentiment Analysis**: Uses a pre-trained FinBERT model to analyze article sentiment (positive, negative, or neutral).
- **Backend**: Flask-based APIs for data fetching and user authentication.
- **Frontend**: Angular-based interface to display sentiment analysis results.
- **Database**: MySQL database storing scraped data and sentiment results.

## Installation

### Prerequisites

- Python 3.8 or higher
- MySQL database
- Node.js and Angular CLI for the frontend
- Required Python packages: `Flask`, `transformers`, `torch`, `mysql-connector-python`, etc. (see `requirements.txt` if available)

### Clone the Repository

```bash
git clone https://mygit.th-deg.de/ma16266/ai-based-sentiment-analysis-of-shares.git
```

### Backend Setup

1. Create and activate a virtual environment, then install required packages:

   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt  # Or manually: pip install Flask transformers torch mysql-connector-python
   ```

2. Configure the database settings in `db_config.py`:

   ```python
   db_config = {
       'user': 'your_db_user',
       'password': 'your_db_password',
       'host': 'your_db_host',
       'database': 'your_db_name'
   }
   ```

3. Run the Flask server:

   ```bash
   python flask-api.py
   ```

   The backend will start on http://127.0.0.1:5000.

4. Run the web scraper and sentiment analysis scripts (e.g., `google_scraper.py`, `finbert-for-google.py`).

### Frontend Setup

1. Navigate to the setup-app folder and install dependencies:

   ```bash
   cd setup-app
   npm install
   ```

2. Run the Angular application:
   ```bash
   ng serve
   ```
   The frontend will start on http://127.0.0.1:4200.

### Database Setup

Import the database tables into MySQL:

```bash
mysql -u your_db_user -p your_db_name < Database/sentiment_analysis_database/shares_google_news_articles.sql
mysql -u your_db_user -p your_db_name < Database/sentiment_analysis_database/shares_google_sentiment_results.sql
mysql -u your_db_user -p your_db_name < Database/sentiment_analysis_database/shares_onvista_articles.sql
mysql -u your_db_user -p your_db_name < Database/sentiment_analysis_database/shares_onvista_sentiment_results.sql
mysql -u your_db_user -p your_db_name < Database/sentiment_analysis_database/shares_user.sql
```

## Usage

1. Start the backend and frontend as described in Installation.
2. Access the frontend at http://127.0.0.1:4200 to view articles and sentiment results.
3. Use the backend APIs for data fetching (e.g., GET /articles for article lists).
4. Run scrapers manually or via scripts to update data.

For troubleshooting, check logs for database connection errors or missing dependencies.

## Contributing

Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request. Follow standard coding practices and include tests if applicable.
