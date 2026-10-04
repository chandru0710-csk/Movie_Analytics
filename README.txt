================================================================================
                        MOVIE ANALYTICS DASHBOARD
================================================================================

Hi! This is my Movie Analytics project. It's an end-to-end data analysis project
built on movie data from TMDB (The Movie Database). It covers the whole flow:
cleaning the data, loading it into a MySQL database, answering analysis questions
with SQL and pandas, and showing everything in an interactive web dashboard.


WHAT DOES IT DO?
--------------------------------------------------------------------------------
It takes raw movie CSV files, cleans them, stores them in a database, and then
explores interesting things about movies like:

- Which movies made the most money
- What genres are most popular
- How ratings are distributed
- Which actors appear in the most movies
- Which directors have the most films
- How movie production changed over the decades
- Profit and return on investment (ROI) for each movie

The dashboard is a website that runs on your own computer, with several pages of
charts plus a page where you can run saved SQL queries.


WHAT'S IN THE PROJECT?
--------------------------------------------------------------------------------
- app.py                   - The main file that runs the dashboard
- Movie_Analytics.ipynb    - Notebook that cleans the data and loads it into MySQL
- 02_sql_analysis.ipynb    - Answers the 10 SQL analysis questions
- 03_pandas_analysis.ipynb - Answers the 10 pandas analysis questions
- Movie_Analytics_csv/     - Folder with the 6 CSV files (the raw data)


THE DATA
--------------------------------------------------------------------------------
The data comes from TMDB and is split across 6 linked tables:

- movies         - 2,503 movies (title, budget, revenue, rating, etc.)
- genres         - 19 different genres
- movie_genres   - links each movie to its genre(s)
- cast           - 24,902 cast entries (actors and their roles)
- crew           - 7,289 crew entries (directors, writers, etc.)
- movie_keywords - 41,681 keywords (themes like "superhero", "revenge", etc.)

The movies range from old classics (1916) all the way to 2026.

IMPORTANT: TMDB stores a 0 for budget or revenue when the real figure is unknown
(it does NOT mean the movie was free). So all the money-based analysis (profit,
ROI, averages) ignores rows where budget or revenue is 0.


WHAT YOU NEED TO RUN THIS
--------------------------------------------------------------------------------
1. Python (I'm using Python 3.14)

2. Some Python packages:
   - streamlit  (for making the web dashboard)
   - pandas     (for working with data)
   - numpy      (for the calculations)
   - matplotlib (for making charts)
   - pymysql    (the MySQL driver)
   - sqlalchemy (how pandas talks to MySQL)

3. MySQL database running on your computer with all the movie data loaded into a
   database called "Movie analytics".


HOW TO INSTALL
--------------------------------------------------------------------------------
Step 1: Install the Python packages

Open Command Prompt or PowerShell and type:

    pip install streamlit pandas numpy matplotlib pymysql sqlalchemy

If that doesn't work, try:

    python -m pip install streamlit pandas numpy matplotlib pymysql sqlalchemy


Step 2: Set up the MySQL database

You need MySQL installed and running. Then run the notebook
(Movie_Analytics.ipynb) from top to bottom. It will:
   - read the 6 CSV files,
   - clean them (fix dates, remove duplicates, trim long text), and
   - create a database called "Movie analytics" with 6 tables.

The database connection uses these settings (fill in your own):

    host:     localhost
    user:     <your_mysql_user>
    password: <your_mysql_password>
    database: Movie analytics

Update those values in the notebooks and in app.py (the create_engine(...) line)
to match your own MySQL login.


HOW TO RUN IT
--------------------------------------------------------------------------------
Method 1: From VS Code

1. Open VS Code
2. Open the Terminal (Ctrl + ` or Terminal menu -> New Terminal)
3. Type:  cd "<path_to_project_folder>"
4. Then type:  streamlit run app.py
5. Your browser should open automatically showing the dashboard!


Method 2: From Command Prompt

1. Press Win + R, type "cmd" and press Enter
2. Type:  cd "<path_to_project_folder>"
3. Type:  python -m streamlit run app.py
4. Open your browser and go to http://localhost:8501


To stop it: Press Ctrl + C in the terminal


THE DASHBOARD PAGES
--------------------------------------------------------------------------------
Home       - Overview and quick stats

Revenue    - Shows which movies made the most money, profit breakdowns, and how
             budget relates to earnings

Genres     - Shows genre distribution, which genres make the most money, and
             rating patterns for different genres

Audience   - Shows rating distributions, popularity patterns, and how many
             people voted for movies

Production - Shows how many movies were released each year, top revenue years,
             and how genres changed over decades

People     - Shows top actors, top directors, and most common movie themes

Dashboard  - A summary page with all the key charts in one place

Query      - NEW. Pick a saved SQL query from a dropdown and see its result. It
             shows the SQL, the result table, a quick chart, a short note, and a
             button to download the result as a CSV.


THE ANALYSIS NOTEBOOKS
--------------------------------------------------------------------------------
02_sql_analysis.ipynb - answers 10 SQL questions, for example:
   1. Action movies released after 2015
   2. Top 10 highest-grossing movies with their genres
   3. Average budget and revenue per genre
   4. Top 10 actors by number of movies
   5. Directors with more than 3 movies
   6. Top 10 most-used keywords
   7. Above-average budget but below-average revenue
   8. Actors in a Christopher Nolan movie
   9. Highest average-rated genre (at least 20 movies)
   10. Top 10 movies by number of keywords

03_pandas_analysis.ipynb - answers 10 pandas questions, for example:
   unique counts, missing budget/revenue handling, profit and ROI, ROI leaders,
   movies per year, runtime outliers (IQR), primary-genre popularity, prolific
   actors, duplicate titles, and popularity vs vote-count anomalies.

Both notebooks connect to MySQL using a SQLAlchemy engine.


COOL FEATURES
--------------------------------------------------------------------------------
Every chart has:
- A box explaining what type of chart it is
- Labels showing the actual values
- Colors that mean something (explained on the chart)
- Arrows and annotations pointing to important parts
- A summary telling you what's high, what's low, and what it means

You can also filter everything using the sidebar:
- Pick specific genres
- Choose a year range
- Set a minimum rating
- Select a language

A live count shows how many movies match your current selection.


COMMON PROBLEMS AND FIXES
--------------------------------------------------------------------------------
"streamlit is not recognized"
-> Python is not in your PATH. Use: python -m streamlit run app.py

"Database could not be loaded"
-> Make sure MySQL is running and you loaded the data using the notebook

"All wedge sizes are zero" error
-> Your filters are too strict. Try resetting them to see more movies

Port 8501 already in use
-> You already have it running. Close the other one first.


SOME NOTES
--------------------------------------------------------------------------------
- The first time you open it, it takes a few seconds to load from MySQL
- After that it's fast because Streamlit caches the data
- When you change filters, everything updates instantly
- There are 15+ different types of charts total
- Each chart tries to teach you how to read it


THAT'S IT!
--------------------------------------------------------------------------------
This was a learning project to practice the full data-analysis workflow -
cleaning, SQL, pandas, visualization, and dashboarding. The data comes from TMDB
and I used it for educational purposes.

If you want to use this, just make sure you have MySQL set up with the data,
install the Python packages, run the cleaning notebook, and run it!


Author: Chandrasekar A
Year: 2026
