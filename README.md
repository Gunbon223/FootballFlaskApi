## 📑 Overview

FootballFlaskApi is a  lightweight REST API built with Python Flask that provides comprehensive football (soccer) data. This API offers access to teams, players, matches, leagues, and statistics to help developers integrate football data into their applications.

## ✨ Features

- **Teams Data**: Access information about football teams, including history, squad, and statistics
- **Player Profiles**: Detailed player information including career stats, biography, and current form
- **Match Data**: Historical and upcoming matches with detailed statistics
- **League Information**: League tables, fixtures, and results
- **Live Scores**: Real-time score updates (where available)
- **Search Functionality**: Find specific teams, players, or matches
- **Authentication**: Secure API access with token-based authentication
- **Rate Limiting**: Fair usage policies to ensure service availability
- **Pagination**: Efficiently handle large data sets
- **Filtering**: Advanced query parameters for precise data retrieval

## 🛠️ Technologies Used

- **Python 3.9+**: Core programming language
- **Flask**: Web framework for building the API
- **Flask-RESTful**: Extension for creating REST APIs
- **SQLAlchemy**: ORM for database interactions
- **Redis**L Main database
- **MYSQL**: Database options (configurable)
- **Docker**: Containerization for easy deployment
- **pytest**: Comprehensive test suite

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- MySQL, Redis 5 or higher

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Gunbon223/FootballFlaskApi.git
   cd FootballFlaskApi
   ```
2. **Set up a virtual environment**
     ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
     ```
2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
2. **Setup database**
    ```bash
    # On config file
    Change Mysql port
    'SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://{database&port}"
    # On Appdb
    Change Redis port
    REDIS_URL = 'redis://localhost:{port}/0'
    ```
3. **Run project**
    ```bash
    flask run # or run run_app.py
    # API will be available at http://127.0.0.1:5000   
    ```

