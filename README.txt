================================================================================
                        MOVIE ANALYTICS DASHBOARD
================================================================================

Hi! This is my Movie Analytics project. It's a web dashboard that shows cool
charts and graphs about movies from TMDB (The Movie Database).


WHAT DOES IT DO?
--------------------------------------------------------------------------------
It's basically a website that runs on your computer and shows you interesting
stuff about movies like:

- Which movies made the most money
- What genres are most popular
- How ratings are distributed
- Which actors appear in the most movies
- How movie production changed over the decades

There are 6 different pages, each showing different charts. Some charts are 
simple bar graphs, others are more fancy like bubble charts and violin plots.


WHAT'S IN THE PROJECT?
--------------------------------------------------------------------------------
- app.py - This is the main file that runs the dashboard
- Movie_Analytics.ipynb - A notebook I used to clean up the data
- Movie_Analytics_csv/ - Folder with 6 CSV files containing all the movie data


THE DATA
--------------------------------------------------------------------------------
I'm using data from TMDB which includes:
- 2,503 movies
- 19 different genres
- 24,902 cast entries (actors and their roles)
- 7,289 crew entries (directors, producers, etc.)
- 41,681 keywords (themes like "superhero", "revenge", etc.)

The data goes from old movies (1916) all the way to 2026.


WHAT YOU NEED TO RUN THIS
--------------------------------------------------------------------------------
1. Python (I'm using Python 3.14)

2. Some Python packages:
   - streamlit (for making the web dashboard)
   - pandas (for working with data)
   - matplotlib (for making charts)
   - pymysql (for connecting to the database)

3. MySQL database running on your computer with all the movie data loaded


HOW TO INSTALL
--------------------------------------------------------------------------------
Step 1: Install the Python packages

Open Command Prompt or PowerShell and type:

    pip install streamlit pandas matplotlib pymysql

If that doesn't work, try:

    python -m pip install streamlit pandas matplotlib pymysql


Step 2: Set up the MySQL database

You need to have MySQL installed and running. Then use the notebook 
(Movie_Analytics.ipynb) to load all the data into MySQL. It creates a 
database called "Movie analytics" with 6 tables.


HOW TO RUN IT
--------------------------------------------------------------------------------
Method 1: From VS Code

1. Open VS Code
2. Open the Terminal (Ctrl + ` or go to Terminal menu → New Terminal)
3. Type:  cd "C:\Users\Chandrasekar A\Documents\Python_vs\Movie_Analytics"
4. Then type:  streamlit run app.py
5. Your browser should open automatically showing the dashboard!


Method 2: From Command Prompt

1. Press Win + R, type "cmd" and press Enter
2. Type:  cd "C:\Users\Chandrasekar A\Documents\Python_vs\Movie_Analytics"
3. Type:  python -m streamlit run app.py
4. Open your browser and go to http://localhost:8501


To stop it: Press Ctrl + C in the terminal


THE DASHBOARD PAGES
--------------------------------------------------------------------------------
Home - Overview and quick stats

Revenue - Shows which movies made the most money, profit breakdowns, and how
          budget relates to earnings

Genres - Shows genre distribution, which genres make the most money, and 
         rating patterns for different genres

Audience - Shows rating distributions, popularity patterns, and how many
           people voted for movies

Production - Shows how many movies were released each year, top revenue years,
             and how genres changed over decades

People - Shows top actors, top directors, and most common movie themes

Dashboard - A summary page with all the key charts in one place


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


COMMON PROBLEMS AND FIXES
--------------------------------------------------------------------------------
"streamlit is not recognized"
→ Python is not in your PATH. Use: python -m streamlit run app.py

"Database could not be loaded"
→ Make sure MySQL is running and you loaded the data using the notebook

"All wedge sizes are zero" error
→ Your filters are too strict. Try resetting them to see more movies

Port 8501 already in use
→ You already have it running. Close the other one first.


SOME NOTES
--------------------------------------------------------------------------------
- The first time you open it, it takes a few seconds to load from MySQL
- After that it's fast because Streamlit caches the data
- When you change filters, everything updates instantly
- There are 15+ different types of charts total
- Each chart tries to teach you how to read it


THAT'S IT!
--------------------------------------------------------------------------------
This was a learning project to practice data analysis and visualization.
The data comes from TMDB and I used it for educational purposes.

If you want to use this, just make sure you have MySQL set up with the data,
install the Python packages, and run it!


Author: Chandrasekar A
Year: 2026
