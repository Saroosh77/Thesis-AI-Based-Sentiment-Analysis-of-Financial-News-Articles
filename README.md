# Semantic Analysis of News Articles using Artificial Intelligence (AI) for Prediction of Market Shares

This project aims to perform sentiment analysis on financial news articles about companies. The workflow includes scraping list of articles from [Google News](https://news.google.com/) and [Onvista.de](https://www.onvista.de/), processing the articles using a pre-trained FinBERT model, and storing the results in a MySQL database. A frontend application displays the list of articles and sentiment results.

## Project Description
This project consists of four main components:

- **Web Scraper:** Scrapes financial news articles from specified websites.
- **Sentiment Analysis:** Uses a pre-trained FinBERT model to analyze the sentiment of the articles.
- **Backend:** Flask-based APIs to handle data fetching and user authentication.
- **Frontend:** Displays the sentiment analysis results in a user-friendly interface.


## Installation

### Prerequisites

- Python 3.8+
- MySQL database
- Node.js and Angular CLI for the frontend

#### Clone the Repository

```
git clone https://mygit.th-deg.de/ma16266/ai-based-semantic-analysis-of-shares.git
```

#### Backend Setup

1. Create a virtual environment and activate it and install all relevant packages from pip.

```
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install Flask and other packages
```

2. Configure the database settings in **db_config.py**:

```
db_config = {
    'user': 'your_db_user',
    'password': 'your_db_password',
    'host': 'your_db_host',
    'database': 'your_db_name'
}
```

3. Run the Flask server on http://127.0.0.1:5000 to start the backend.

4. Run the web scraper and sentiment analysis python files to obtain results.

#### Frontend Setup

1. Navigate to Setup App folder and install the required node packages.

```
cd setup-app
npm install
```

2. Run the Angular application on http://127.0.0.1:4200.

```
ng serve
```

#### Database

Import the database tables from the folder sentiment_analysis_database in Database folder in MySQL database.