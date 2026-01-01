# basketballDB

A Python-based database system and utilities for storing, querying, and analyzing basketball league data.

This repository contains tools to initialize, populate, and interact with a basketball match database. It includes a CLI and a web interface for browsing records, Python modules for data access, and scripts for initialzing and populating the database.

Repository Structure

basketballDB/
├── basketball_league_web/ # Web UI for browsing league data

├── controller.py # Command-line controller (MAIN FILE)

├── db.py # Database connection and helper functions

├── init_db.py # Database initialization script

├── matchDB.sql # SQL schema & sample data

├── model.py # Data models and ORM definitions

├── populate_huge.py # Script to generate large dataset

├── view_cmd.py # Command-line view utilities

├── requirements.txt # Python dependencies

├── pyproject.toml # Build & metadata

├── .gitignore

└── .gitattributes

## Installation

1. Clone the repository:

git clone https://github.com/jimfil/basketballDB.git
cd basketballDB

2. Install dependencies:

pip install -r requirements.txt

3. Create a .env file with the following and your db credentials 

DB_HOST= {your host's name}
DB_USER= {your user's name}
DB_PASS= {your db's password}
DB_NAME= {your db's name}

FLASK_APP=run
FLASK_DEBUG=1
SECRET_KEY= {your secret key}

4. Initialize the database:

python init_db.py

5. Populate with fake data:

python populate_huge.py

6a. Run the Command Line Interface

python controller.py

6b. Run the Web Application
cd basketball_league_web
flask run
