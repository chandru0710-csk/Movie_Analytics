import matplotlib.pyplot as plt
import pandas as pd
import pymysql
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title='Movie Analytics', page_icon='🎬', layout='wide')


@st.cache_data
def load_data():
    engine = create_engine('mysql+pymysql://root:1234@localhost/Movie analytics')
    movies = pd.read_sql('SELECT * FROM movies', engine)
    genres = pd.read_sql('SELECT * FROM genres', engine)
    movie_genres = pd.read_sql('SELECT * FROM movie_genres', engine)
    cast = pd.read_sql('SELECT * FROM `cast`', engine)
    crew = pd.read_sql('SELECT * FROM crew', engine)
    keywords = pd.read_sql('SELECT * FROM movie_keywords', engine)
    engine.dispose()
    movies['release_date'] = pd.to_datetime(movies['release_date'], errors='coerce')
    movies['release_year'] = movies['release_date'].dt.year
    movies['release_decade'] = (movies['release_year'] // 10 * 10).astype('Int64').astype(str) + 's'
    movies['profit'] = movies['revenue'] - movies['budget']
    genre_lookup = genres.set_index('genre_id')['genre_name'].to_dict()
    movie_genres['genre_name'] = movie_genres['genre_id'].map(genre_lookup)
    return movies, genres, movie_genres, cast, crew, keywords


def show_chart_definition(chart_type):
    definitions = {
        'Bar Chart': 'A bar chart represents data with rectangular bars where the length of each bar is proportional to the value it represents. Useful for comparing quantities across categories.',
        'Pie Chart': 'A pie chart is a circular graph divided into slices to illustrate numerical proportion. Each slice represents a category\'s contribution to the whole (100%).',
        'Donut Chart': 'A donut chart is similar to a pie chart but has a blank center, making it easier to read and compare values while maintaining the part-to-whole relationship.',
        'Scatter Plot': 'A scatter plot uses dots to represent values for two different variables, showing the relationship or correlation between them on X and Y axes.',
        'Area Chart': 'An area chart displays quantitative data graphically, with the area between axis and line filled with color, emphasizing the magnitude of change over time.',
        'Line Chart': 'A line chart connects individual data points with lines to show trends and changes over time or across categories in a continuous manner.',
        'Box Plot': 'A box plot (box-and-whisker plot) displays the distribution of data showing the median, quartiles, and outliers, useful for comparing distributions across groups.',
        'Histogram': 'A histogram represents the frequency distribution of continuous data using bars, where each bar groups numbers into ranges (bins).',
        'Hexbin Chart': 'A hexbin chart divides the plot into hexagonal bins and colors them based on the count of observations, useful for visualizing density in large datasets.',
        'Violin Plot': 'A violin plot combines a box plot with a kernel density plot, showing the distribution shape, median, and quartiles in a single visualization.',
        'Stem Plot': 'A stem plot displays data as lines (stems) extending from a baseline to a marker, useful for discrete sequences and emphasizing individual values.',
        'Bubble Chart': 'A bubble chart is a scatter plot where a third dimension is represented by the size of the markers (bubbles), allowing three variables to be shown.',
        'Stacked Area Chart': 'A stacked area chart displays multiple data series stacked on top of each other, showing both individual values and cumulative totals over time.'
    }
    if chart_type in definitions:
        st.info(f"**📊 {chart_type} Definition:** {definitions[chart_type]}")


def show_enhanced_insights(chart_name, data, chart_type, color_meaning=''):
    st.markdown(f'**📈 Insights for {chart_name}**')
    
    if not data.empty:
        if chart_type == 'bar':
            highest = data.idxmax()
            lowest = data.idxmin()
            st.markdown(f"- **Highest:** {highest} with value {data[highest]:,.0f}")
            st.markdown(f"- **Lowest:** {lowest} with value {data[lowest]:,.0f}")
            st.markdown(f"- **Inference:** {highest} significantly outperforms other categories, suggesting dominance in this metric.")
        
        elif chart_type == 'pie':
            highest = data.idxmax()
            st.markdown(f"- **Largest Share:** {highest} ({data[highest]:,.0f} - {(data[highest]/data.sum()*100):.1f}%)")
            st.markdown(f"- **Total:** {data.sum():,.0f} across all categories")
            st.markdown(f"- **Inference:** {highest} dominates the distribution, indicating concentrated performance.")
        
        elif chart_type == 'revenue':
            highest_idx = data.idxmax()
            st.markdown(f"- **Top Performer:** {highest_idx} with revenue {money(data[highest_idx])}")
            st.markdown(f"- **Average Revenue:** {money(data.mean())}")
            st.markdown(f"- **Inference:** High-revenue performers show the commercial potential in this category.")
    
    if color_meaning:
        st.markdown(f"- **🎨 Color Meaning:** {color_meaning}")


def money(value):
    if pd.isna(value):
        return 'N/A'
    if abs(value) >= 1_000_000_000:
        return f'${value / 1_000_000_000:.2f}B'
    if abs(value) >= 1_000_000:
        return f'${value / 1_000_000:.1f}M'
    return f'${value:,.0f}'


def show_kpis(filtered_movies, filtered_genres, filtered_cast):
    columns = st.columns(4)
    columns[0].metric('Total movies', f'{len(filtered_movies):,}')
    columns[1].metric('Genres represented', f'{filtered_genres["genre_id"].nunique():,}')
    columns[2].metric('Actors represented', f'{filtered_cast["person_id"].nunique():,}')
    rating = filtered_movies['vote_average'].mean()
    columns[3].metric('Average rating', f'{rating:.2f}' if pd.notna(rating) else 'N/A')


try:
    movies, genres, movie_genres, cast, crew, keywords = load_data()
except Exception as error:
    st.error('The Movie analytics MySQL database could not be loaded.')
    st.code(str(error))
    st.stop()

if movies.empty:
    st.warning('No movie records were found in MySQL.')
    st.stop()

st.markdown('''<style>
.block-container{padding-top:2rem}
.hero{background:#14213d;color:white;padding:2rem;border-radius:12px}
.hero h1{margin-bottom:.4rem}
.hero p{color:#dbe4f0;font-size:1.05rem}
[data-testid="stMetric"]{background:#f7f9fc;border:1px solid #dfe5ec;padding:1rem}
</style>''', unsafe_allow_html=True)

years = sorted(movies['release_year'].dropna().astype(int).unique())
genres_available = sorted(movie_genres['genre_name'].dropna().unique())
languages = sorted(movies['original_language'].dropna().unique())

st.sidebar.title('Movie Analytics')
page = st.sidebar.radio('Menu', ['Home', 'Revenue', 'Genres', 'Audience', 'Production', 'People', 'Dashboard', 'Query'])
st.sidebar.markdown('---')
st.sidebar.subheader('Shared filters')
selected_genres = st.sidebar.multiselect('Genres', genres_available)
selected_years = st.sidebar.slider('Release year', min(years), max(years), (min(years), max(years)))
minimum_rating = st.sidebar.slider('Minimum rating', 0.0, 10.0, 0.0, 0.1)
selected_language = st.sidebar.selectbox('Language', ['All languages'] + languages)

filtered_movies = movies[movies['release_year'].between(selected_years[0], selected_years[1])].copy()
filtered_movies = filtered_movies[filtered_movies['vote_average'] >= minimum_rating]
if selected_language != 'All languages':
    filtered_movies = filtered_movies[filtered_movies['original_language'] == selected_language]
if selected_genres:
    matching_ids = movie_genres[movie_genres['genre_name'].isin(selected_genres)]['movie_id'].unique()
    filtered_movies = filtered_movies[filtered_movies['movie_id'].isin(matching_ids)]

movie_ids = filtered_movies['movie_id'].tolist()
filtered_genres = movie_genres[movie_genres['movie_id'].isin(movie_ids)].copy()
filtered_cast = cast[cast['movie_id'].isin(movie_ids)].copy()
filtered_crew = crew[crew['movie_id'].isin(movie_ids)].copy()
filtered_keywords = keywords[keywords['movie_id'].isin(movie_ids)].copy()
st.sidebar.metric('Matching movies', f'{len(filtered_movies):,}')

if page == 'Home':
    st.markdown('<div class="hero"><h1>Movie Analytics</h1><p>Explore commercial, audience, genre, production, and talent patterns in the TMDB movie catalogue.</p></div>', unsafe_allow_html=True)
    show_kpis(filtered_movies, filtered_genres, filtered_cast)
    st.subheader('Project introduction')
    st.write('This dashboard reads the cleaned relational tables from the Movie analytics MySQL database. Each analysis page contains three different chart forms, giving 15 charts in total.')
    st.markdown('**Home overview | Insights**')
    st.markdown('- Use the shared filters to update every page.\n- Open the five analysis pages to see three visuals on each page.\n- The final Dashboard page gives the executive summary without repeating the 15 analysis charts.')

elif page == 'Revenue':
    st.title('Revenue Analysis')
    st.caption('Commercial performance through three distinct visual forms.')
    
    if filtered_movies.empty:
        st.error('⚠️ No movies match the current filter criteria. Please adjust your filters (especially the minimum rating) to see data.')
        st.stop()
    
    # Chart 1: Bar Chart
    st.subheader('1. Top 10 Movies by Revenue (Bar Chart)')
    show_chart_definition('Bar Chart')
    top_revenue = filtered_movies.nlargest(10, 'revenue').set_index('title')['revenue'].sort_values()
    figure, axis = plt.subplots(figsize=(10, 6))
    bars = axis.barh(top_revenue.index, top_revenue.values, color='#277da1')
    axis.set_title('Top 10 Movies by Revenue (Bar Chart)', fontsize=14, fontweight='bold')
    axis.set_xlabel('Revenue ($)', fontsize=11)
    axis.set_ylabel('Movie Title', fontsize=11)
    # Add value labels
    for i, (idx, val) in enumerate(top_revenue.items()):
        axis.text(val, i, f' {money(val)}', va='center', fontsize=9)
    st.pyplot(figure, width='stretch')
    plt.close(figure)
    show_enhanced_insights('Top 10 Movies by Revenue', top_revenue, 'revenue', 
                          'Blue bars represent high box-office performers')
    
    # Chart 2: Pie Chart
    st.subheader('2. Profit Composition (Pie Chart)')
    show_chart_definition('Pie Chart')
    profit_data = filtered_movies[filtered_movies['profit'] > 0].nlargest(12, 'profit').set_index('title')['profit']
    figure, axis = plt.subplots(figsize=(10, 6))
    wedges, texts, autotexts = axis.pie(profit_data, labels=profit_data.index, startangle=90, 
                                         autopct='%1.1f%%', pctdistance=0.85,
                                         textprops={'fontsize': 9})
    axis.set_title('Profit Composition (Pie Chart)', fontsize=14, fontweight='bold')
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    st.pyplot(figure, width='stretch')
    plt.close(figure)
    show_enhanced_insights('Profit Composition', profit_data, 'pie',
                          'Each color represents a different high-profit movie, percentages show relative contribution')
    
    # Chart 3: Scatter Plot
    st.subheader('3. Budget versus Revenue (Scatter Plot)')
    show_chart_definition('Scatter Plot')
    financials = filtered_movies[(filtered_movies['budget'] > 0) & (filtered_movies['revenue'] > 0)]
    figure, axis = plt.subplots(figsize=(12, 7))
    scatter = axis.scatter(financials['budget'], financials['revenue'], 
                          c=financials['vote_average'], cmap='viridis', 
                          alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
    axis.set_xlabel('Budget (Money Spent to Make Movie)', fontsize=11, weight='bold')
    axis.set_ylabel('Revenue (Money Earned at Box Office)', fontsize=11, weight='bold')
    axis.set_title('Budget versus Revenue (Scatter Plot) - Each dot is a movie', fontsize=14, fontweight='bold')
    axis.grid(alpha=0.3, linestyle='--')
    cbar = figure.colorbar(scatter, ax=axis)
    cbar.set_label('Audience Rating (Yellow=High, Purple=Low)', fontsize=10)
    
    # Add diagonal reference line
    max_val = max(financials['budget'].max(), financials['revenue'].max())
    axis.plot([0, max_val], [0, max_val], 'r--', alpha=0.5, linewidth=2, label='Break-even line')
    
    # Add annotations - positioned carefully to avoid overlap
    axis.text(0.02, 0.98, '📍 Each DOT = One Movie\n🟡 High up = Made lots $\n◀ Far right = Cost a lot\n🟡 Yellow = Well-rated\n🟣 Purple = Poorly-rated', 
             transform=axis.transAxes, fontsize=9, verticalalignment='top', horizontalalignment='left',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.95, edgecolor='black', linewidth=2))
    
    axis.text(0.98, 0.35, '↑ Above red line\n= Profitable\n\n↓ Below red line\n= Lost money', 
             transform=axis.transAxes, fontsize=9, verticalalignment='center', horizontalalignment='right',
             color='darkred', weight='bold',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='red', linewidth=2))
    
    st.pyplot(figure, width='stretch')
    plt.close(figure)
    st.markdown('**📈 Insights for Budget vs Revenue**')
    st.markdown(f'- **Total Movies Analyzed:** {len(financials):,}')
    st.markdown(f'- **Average Budget:** {money(financials["budget"].mean())}')
    st.markdown(f'- **Average Revenue:** {money(financials["revenue"].mean())}')
    st.markdown('- **🎨 How to Read:** Dots going upward-right = higher budget usually means higher revenue')
    st.markdown('- **Key Patterns:** Yellow dots at top-left = low-budget hits! | Purple dots at bottom-right = expensive flops!')

elif page == 'Genres':
    st.title('Genre Analysis')
    st.caption('Genre volume, revenue, and audience reception.')
    
    if filtered_movies.empty:
        st.error('⚠️ No movies match the current filter criteria. Please adjust your filters (especially the minimum rating) to see data.')
        st.stop()
    
    # Chart 1: Donut Chart
    st.subheader('1. Genre Share (Donut Chart)')
    show_chart_definition('Donut Chart')
    genre_counts = filtered_genres.groupby('genre_name')['movie_id'].nunique().sort_values(ascending=False).head(10)
    
    if genre_counts.empty or len(genre_counts) == 0:
        st.warning('⚠️ No genre data available for the selected filters. Please adjust your filters.')
    else:
        figure, axis = plt.subplots(figsize=(10, 6))
        wedges, texts, autotexts = axis.pie(genre_counts, labels=genre_counts.index, 
                                             wedgeprops={'width': 0.4}, startangle=90,
                                             autopct='%1.1f%%', pctdistance=0.85,
                                             textprops={'fontsize': 10})
        axis.set_title('Genre Share (Donut Chart)', fontsize=14, fontweight='bold')
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        st.pyplot(figure, width='stretch')
        plt.close(figure)
        show_enhanced_insights('Genre Share', genre_counts, 'pie',
                              'Each colored segment represents a genre, with percentage showing market share')
    
    # Chart 2: Area Chart
    st.subheader('2. Average Revenue by Genre (Area Chart)')
    show_chart_definition('Area Chart')
    genre_revenue = filtered_movies.merge(filtered_genres[['movie_id', 'genre_name']], 
                                         on='movie_id').groupby('genre_name')['revenue'].mean().sort_values(ascending=False).head(10)
    
    if genre_revenue.empty or len(genre_revenue) == 0:
        st.warning('⚠️ No revenue data available for the selected filters. Please adjust your filters.')
    else:
        figure, axis = plt.subplots(figsize=(10, 6))
        axis.fill_between(range(len(genre_revenue)), genre_revenue.values, alpha=0.5, color='#43aa8b')
        axis.plot(range(len(genre_revenue)), genre_revenue.values, marker='o', 
                 color='#277da1', linewidth=2, markersize=8)
        axis.set_xticks(range(len(genre_revenue)))
        axis.set_xticklabels(genre_revenue.index, rotation=45, ha='right')
        axis.set_title('Average Revenue by Genre (Area Chart)', fontsize=14, fontweight='bold')
        axis.set_ylabel('Average Revenue ($)', fontsize=11)
        axis.grid(alpha=0.3, axis='y')
        # Add value labels
        for i, val in enumerate(genre_revenue.values):
            axis.text(i, val, f'{money(val)}', ha='center', va='bottom', fontsize=8)
        st.pyplot(figure, width='stretch')
        plt.close(figure)
        show_enhanced_insights('Average Revenue by Genre', genre_revenue, 'revenue',
                              'Green shaded area shows revenue magnitude, blue line traces the trend across genres')
    
    # Chart 3: Box Plot
    st.subheader('3. Rating Spread by Genre (Box Plot)')
    show_chart_definition('Box Plot')
    genre_rating = filtered_movies.merge(filtered_genres[['movie_id', 'genre_name']], 
                                        on='movie_id').groupby('genre_name')['vote_average'].apply(list)
    
    if genre_rating.empty or len(genre_rating) == 0:
        st.warning('⚠️ No rating data available for the selected filters. Please adjust your filters.')
    else:
        figure, axis = plt.subplots(figsize=(12, 7))
        bp = axis.boxplot([genre_rating[name] for name in genre_rating.index], 
                          tick_labels=genre_rating.index, showfliers=True, patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('#43aa8b')
            patch.set_alpha(0.6)
        axis.tick_params(axis='x', rotation=45)
        axis.set_title('Rating Spread by Genre (Box Plot) - How to Read', fontsize=14, fontweight='bold')
        axis.set_ylabel('Vote Average', fontsize=11)
        axis.grid(alpha=0.3, axis='y')
        
        # Add annotations to explain box plot elements (on first box)
        if len(genre_rating) > 0:
            first_genre = list(genre_rating.index)[0]
            first_data = genre_rating[first_genre]
            q1, median, q3 = pd.Series(first_data).quantile([0.25, 0.5, 0.75])
            
            # Annotate median
            axis.annotate('← Median (middle value)', xy=(1, median), xytext=(1.5, median),
                         fontsize=9, color='red', weight='bold',
                         arrowprops=dict(arrowstyle='->', color='red', lw=2))
            
            # Annotate box
            axis.annotate('Box = Middle 50%\nof ratings', xy=(1, q1), xytext=(2, q1-0.5),
                         fontsize=9, color='darkgreen', weight='bold',
                         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
            
            # Annotate outlier if exists
            axis.text(0.5, axis.get_ylim()[1]-0.3, '• = Outliers\n(unusual ratings)', 
                     fontsize=9, color='blue', weight='bold',
                     bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        st.pyplot(figure, width='stretch')
        plt.close(figure)
        
        st.markdown('**📈 Insights for Rating Spread**')
        for genre in genre_rating.index[:5]:
            ratings = genre_rating[genre]
            st.markdown(f"- **{genre}:** Median={pd.Series(ratings).median():.2f}, Range={min(ratings):.1f}-{max(ratings):.1f}")
        st.markdown('- **🎨 How to Read:** Taller boxes = more variation in quality. Short boxes = consistent quality.')

elif page == 'Audience':
    st.title('Audience Analysis')
    st.caption('Ratings, popularity, and voting activity.')
    
    if filtered_movies.empty:
        st.error('⚠️ No movies match the current filter criteria. Please adjust your filters (especially the minimum rating) to see data.')
        st.stop()
    
    # Chart 1: Histogram
    st.subheader('1. Rating Distribution (Histogram)')
    show_chart_definition('Histogram')
    figure, axis = plt.subplots(figsize=(10, 6))
    counts, bins, patches = axis.hist(filtered_movies['vote_average'].dropna(), bins=20, 
                                      color='#fca311', edgecolor='white', linewidth=1.2)
    axis.set_title('Rating Distribution (Histogram)', fontsize=14, fontweight='bold')
    axis.set_xlabel('Vote Average', fontsize=11)
    axis.set_ylabel('Number of Movies', fontsize=11)
    axis.grid(alpha=0.3, axis='y')
    # Add count labels on top of bars
    for i in range(len(patches)):
        if counts[i] > 0:
            axis.text(patches[i].get_x() + patches[i].get_width()/2, counts[i], 
                     int(counts[i]), ha='center', va='bottom', fontsize=8)
    st.pyplot(figure, width='stretch')
    plt.close(figure)
    ratings = filtered_movies['vote_average'].dropna()
    st.markdown('**📈 Insights for Rating Distribution**')
    st.markdown(f'- **Most Common Rating Range:** {ratings.mode().values[0]:.1f} (peak of distribution)')
    st.markdown(f'- **Average Rating:** {ratings.mean():.2f}')
    st.markdown(f'- **Median Rating:** {ratings.median():.2f}')
    st.markdown('- **Inference:** Distribution shows where most movies cluster in terms of audience ratings')
    st.markdown('- **🎨 Color Meaning:** Orange bars represent frequency counts, taller bars = more movies in that rating range')
    
    # Chart 2: Hexbin Chart
    st.subheader('2. Popularity and Vote Density (Hexbin Chart)')
    show_chart_definition('Hexbin Chart')
    popularity_votes = filtered_movies[['popularity', 'vote_count']].dropna()
    figure, axis = plt.subplots(figsize=(12, 7))
    hb = axis.hexbin(popularity_votes['vote_count'], popularity_votes['popularity'], 
                     gridsize=25, cmap='magma', mincnt=1)
    cbar = figure.colorbar(hb, ax=axis, label='Number of Movies (Density)')
    axis.set_xlabel('Vote Count (How many people rated)', fontsize=11, weight='bold')
    axis.set_ylabel('Popularity Score', fontsize=11, weight='bold')
    axis.set_title('Popularity and Vote Density (Hexbin Chart) - Color shows movie concentration', 
                   fontsize=14, fontweight='bold')
    
    # Add annotations to explain the chart - positioned in top-left
    axis.text(0.02, 0.98, '🔶 Each hexagon = a group of movies\n🟡 Bright = MANY movies here\n🟣 Dark = FEW movies here', 
             transform=axis.transAxes, fontsize=10, verticalalignment='top', horizontalalignment='left',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.95, edgecolor='black', linewidth=2))
    
    st.pyplot(figure, width='stretch')
    plt.close(figure)
    st.markdown('**📈 Insights for Popularity & Votes**')
    st.markdown(f'- **Highest Vote Count:** {popularity_votes["vote_count"].max():,.0f} (most reviewed movie)')
    st.markdown(f'- **Highest Popularity:** {popularity_votes["popularity"].max():.1f} (most popular movie)')
    st.markdown(f'- **Average Votes:** {popularity_votes["vote_count"].mean():,.0f}')
    st.markdown('- **🎨 How to Read:** Look for bright clusters - they show common patterns (e.g., most movies have low votes + low popularity)')
    st.markdown('- **Key Pattern:** Bottom-left cluster = typical indie films | Top-right cluster = blockbusters')
    
    # Chart 3: Violin Plot
    st.subheader('3. Rating Distribution Shape (Violin Plot)')
    show_chart_definition('Violin Plot')
    figure, axis = plt.subplots(figsize=(10, 7))
    parts = axis.violinplot(filtered_movies['vote_average'].dropna(), showmeans=True, 
                           showmedians=True, showextrema=True)
    for pc in parts['bodies']:
        pc.set_facecolor('#43aa8b')
        pc.set_alpha(0.7)
    axis.set_title('Rating Distribution Shape (Violin Plot) - Width shows concentration', 
                   fontsize=14, fontweight='bold')
    axis.set_ylabel('Vote Average (Rating)', fontsize=11, weight='bold')
    axis.set_xticks([1])
    axis.set_xticklabels(['All Movies'])
    axis.grid(alpha=0.3, axis='y')
    
    # Add annotations
    mean_val = filtered_movies['vote_average'].mean()
    median_val = filtered_movies['vote_average'].median()
    
    axis.annotate('← WIDER = More movies\nrated at this score', 
                 xy=(1.15, mean_val), xytext=(1.3, mean_val+1),
                 fontsize=10, color='darkgreen', weight='bold',
                 bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9),
                 arrowprops=dict(arrowstyle='->', color='darkgreen', lw=2))
    
    axis.annotate(f'Blue = Mean ({mean_val:.2f})', 
                 xy=(1, mean_val), xytext=(0.5, mean_val),
                 fontsize=9, color='blue', weight='bold')
    
    axis.annotate(f'Red = Median ({median_val:.2f})', 
                 xy=(1, median_val), xytext=(0.5, median_val-0.5),
                 fontsize=9, color='red', weight='bold')
    
    st.pyplot(figure, width='stretch')
    plt.close(figure)
    st.markdown('**📈 Insights for Rating Shape**')
    st.markdown(f'- **Mean (Average):** {mean_val:.2f}')
    st.markdown(f'- **Median (Middle value):** {median_val:.2f}')
    st.markdown('- **🎨 How to Read:** The fatter the violin at a rating, the more movies have that rating')
    st.markdown('- **Key Insight:** Peak width shows the most common rating range in your database')

elif page == 'Production':
    st.title('Production Trends')
    st.caption('Release volume, commercial periods, and genre mix.')
    
    if filtered_movies.empty:
        st.error('⚠️ No movies match the current filter criteria. Please adjust your filters (especially the minimum rating) to see data.')
        st.stop()
    
    # Chart 1: Line Chart
    st.subheader('1. Movies Released by Year (Line Chart)')
    show_chart_definition('Line Chart')
    yearly_output = filtered_movies.groupby('release_year').size().sort_index()
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.plot(yearly_output.index, yearly_output.values, marker='o', color='#277da1', 
             linewidth=2, markersize=6)
    axis.set_title('Movies Released by Year (Line Chart)', fontsize=14, fontweight='bold')
    axis.set_xlabel('Release Year', fontsize=11)
    axis.set_ylabel('Number of Movies', fontsize=11)
    axis.grid(alpha=0.3, linestyle='--')
    # Add value labels at peaks
    max_idx = yearly_output.idxmax()
    axis.annotate(f'{yearly_output[max_idx]}', xy=(max_idx, yearly_output[max_idx]),
                 xytext=(10, 10), textcoords='offset points', fontsize=9,
                 bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    st.pyplot(figure, width='stretch')
    plt.close(figure)
    st.markdown('**📈 Insights for Movies by Year**')
    st.markdown(f'- **Peak Year:** {int(yearly_output.idxmax())} with {yearly_output.max()} movies')
    st.markdown(f'- **Lowest Year:** {int(yearly_output.idxmin())} with {yearly_output.min()} movies')
    st.markdown('- **Inference:** Trend shows industry production volume changes over time')
    st.markdown('- **🎨 Color Meaning:** Blue line traces the production trend, dots mark individual years')
    
    # Chart 2: Horizontal Bar Chart
    st.subheader('2. Highest Average-Revenue Years (Bar Chart)')
    show_chart_definition('Bar Chart')
    yearly_revenue = filtered_movies.groupby('release_year')['revenue'].mean().dropna().sort_values(ascending=False).head(10)
    figure, axis = plt.subplots(figsize=(10, 6))
    bars = axis.barh(yearly_revenue.index.astype(str), yearly_revenue.values, color='#f9844a')
    axis.invert_yaxis()
    axis.set_title('Highest Average-Revenue Years (Bar Chart)', fontsize=14, fontweight='bold')
    axis.set_xlabel('Average Revenue ($)', fontsize=11)
    axis.set_ylabel('Year', fontsize=11)
    axis.grid(alpha=0.3, axis='x')
    # Add value labels
    for i, (idx, val) in enumerate(yearly_revenue.items()):
        axis.text(val, i, f' {money(val)}', va='center', fontsize=9)
    st.pyplot(figure, width='stretch')
    plt.close(figure)
    show_enhanced_insights('Top Revenue Years', yearly_revenue, 'revenue',
                          'Orange bars = revenue strength, longer bars = higher average revenue for that year')
    
    # Chart 3: Stacked Area Chart
    st.subheader('3. Genre Mix by Decade (Stacked Area Chart)')
    show_chart_definition('Stacked Area Chart')
    decade_genres = filtered_movies.merge(filtered_genres[['movie_id', 'genre_name']], 
                                         on='movie_id').pivot_table(index='release_decade', 
                                         columns='genre_name', values='movie_id', 
                                         aggfunc='count', fill_value=0)
    figure, axis = plt.subplots(figsize=(14, 7))
    decade_genres.plot.area(ax=axis, alpha=0.8, linewidth=0)
    axis.set_title('Genre Mix by Decade (Stacked Area Chart) - Each color is a genre', fontsize=14, fontweight='bold')
    axis.set_xlabel('Release Decade', fontsize=11, weight='bold')
    axis.set_ylabel('Number of Movies', fontsize=11, weight='bold')
    axis.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=8, title='Genres')
    axis.grid(alpha=0.3, axis='y')
    
    # Add annotations - positioned in upper left away from the areas
    axis.text(0.02, 0.98, '📚 Each colored layer = One genre\n📈 Total height = All movies\n🎨 Growing area = Popular\n📉 Shrinking = Declining', 
             transform=axis.transAxes, fontsize=9, verticalalignment='top', horizontalalignment='left',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.95, edgecolor='black', linewidth=2))
    
    st.pyplot(figure, width='stretch')
    plt.close(figure)
    st.markdown('**📈 Insights for Genre Mix**')
    top_genre_per_decade = decade_genres.idxmax(axis=1)
    for decade in decade_genres.index[-3:]:
        st.markdown(f'- **{decade}:** {top_genre_per_decade[decade]} dominated ({decade_genres.loc[decade, top_genre_per_decade[decade]]} movies)')
    st.markdown('- **🎨 How to Read:** Follow one color across time - if it grows wider, that genre is becoming more popular')
    st.markdown('- **Key Insight:** Total height shows overall movie production volume per decade')

elif page == 'People':
    st.title('People and Keywords')
    st.caption('Recurring talent and themes.')
    
    if filtered_movies.empty:
        st.error('⚠️ No movies match the current filter criteria. Please adjust your filters (especially the minimum rating) to see data.')
        st.stop()
    
    # Chart 1: Horizontal Bar Chart
    st.subheader('1. Top Actors by Appearances (Bar Chart)')
    show_chart_definition('Bar Chart')
    actor_counts = filtered_cast.groupby('actor_name').size().sort_values(ascending=False).head(12)
    figure, axis = plt.subplots(figsize=(10, 6))
    bars = axis.barh(actor_counts.index[::-1], actor_counts.values[::-1], color='#577590')
    axis.set_title('Top Actors by Appearances (Bar Chart)', fontsize=14, fontweight='bold')
    axis.set_xlabel('Number of Appearances', fontsize=11)
    axis.set_ylabel('Actor Name', fontsize=11)
    axis.grid(alpha=0.3, axis='x')
    # Add value labels
    for i, (idx, val) in enumerate(actor_counts[::-1].items()):
        axis.text(val, i, f' {val}', va='center', fontsize=9)
    st.pyplot(figure, width='stretch')
    plt.close(figure)
    show_enhanced_insights('Top Actors', actor_counts, 'bar',
                          'Dark blue bars show actor frequency, longer bars = more movie appearances')
    
    # Chart 2: Stem Plot
    st.subheader('2. Director Credits (Stem Plot)')
    show_chart_definition('Stem Plot')
    directors = filtered_crew[filtered_crew['job'].str.lower() == 'director']
    director_counts = directors.groupby('person_name').size().sort_values(ascending=False).head(12)
    figure, axis = plt.subplots(figsize=(10, 6))
    markerline, stemlines, baseline = axis.stem(director_counts.index, director_counts.values, 
                                                linefmt='#f94144', markerfmt='o', basefmt=' ')
    markerline.set_markerfacecolor('#f94144')
    markerline.set_markersize(8)
    stemlines.set_linewidth(2)
    axis.tick_params(axis='x', rotation=60)
    axis.set_title('Director Credits (Stem Plot)', fontsize=14, fontweight='bold')
    axis.set_ylabel('Number of Movies Directed', fontsize=11)
    axis.grid(alpha=0.3, axis='y')
    # Add value labels
    for i, (idx, val) in enumerate(director_counts.items()):
        axis.text(i, val, f'{val}', ha='center', va='bottom', fontsize=9)
    st.pyplot(figure, width='stretch')
    plt.close(figure)
    show_enhanced_insights('Top Directors', director_counts, 'bar',
                          'Red stems show director productivity, taller stems = more movies directed')
    
    # Chart 3: Bubble Chart
    st.subheader('3. Keyword Frequency (Bubble Chart)')
    show_chart_definition('Bubble Chart')
    keyword_counts = filtered_keywords.groupby('keyword_name').size().sort_values(ascending=False).head(15)
    figure, axis = plt.subplots(figsize=(14, 7))
    sizes = keyword_counts.values * 30
    scatter = axis.scatter(range(len(keyword_counts)), keyword_counts.values, s=sizes, 
                          c=keyword_counts.values, cmap='plasma', alpha=0.7, edgecolors='black', linewidth=1)
    axis.set_xticks(range(len(keyword_counts)))
    axis.set_xticklabels(keyword_counts.index, rotation=60, ha='right')
    axis.set_title('Keyword Frequency (Bubble Chart) - Bubble size shows frequency', fontsize=14, fontweight='bold')
    axis.set_ylabel('Frequency (Number of Movies)', fontsize=11, weight='bold')
    axis.set_xlabel('Keyword/Theme', fontsize=11, weight='bold')
    axis.grid(alpha=0.3, axis='y')
    
    # Set y-axis limit to give more space at top
    axis.set_ylim(0, keyword_counts.max() * 1.15)
    
    cbar = figure.colorbar(scatter, ax=axis)
    cbar.set_label('Frequency (Yellow=Most common)', fontsize=10)
    
    # Add value labels on bubbles
    for i, (idx, val) in enumerate(keyword_counts.items()):
        axis.text(i, val + keyword_counts.max()*0.02, f'{val}', ha='center', va='bottom', fontsize=9, weight='bold')
    
    # Add annotations in bottom right (away from bubbles)
    axis.text(0.98, 0.05, '⚫ Bubble SIZE = How common\n🟡 Yellow = Most popular theme\n🟣 Purple = Less common theme\n📊 Number above = Exact count', 
             transform=axis.transAxes, fontsize=10, verticalalignment='bottom', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.95, edgecolor='black', linewidth=2))
    
    st.pyplot(figure, width='stretch')
    plt.close(figure)
    show_enhanced_insights('Top Keywords', keyword_counts, 'bar',
                          'Bigger bubbles = more movies use this theme. Colors add visual emphasis (yellow=trending, purple=niche)')

elif page == 'Dashboard':
    st.title('Movie Analytics Dashboard')
    st.caption('Executive overview with all key metrics.')
    show_kpis(filtered_movies, filtered_genres, filtered_cast)

    if filtered_movies.empty:
        st.warning('No movies match the current filters.')
    else:
        dashboard_column_1, dashboard_column_2, dashboard_column_3 = st.columns(3)

        with dashboard_column_1:
            yearly_output = filtered_movies.groupby('release_year').size().sort_index()
            figure, axis = plt.subplots(figsize=(5, 3))
            axis.plot(yearly_output.index, yearly_output.values, color='#2878d0', linewidth=2)
            axis.fill_between(yearly_output.index, yearly_output.values, color='#2878d0', alpha=.2)
            axis.set_title('Movies Over Time (Line)', fontsize=10, fontweight='bold')
            axis.set_xlabel('Year', fontsize=8)
            axis.set_ylabel('Movies', fontsize=8)
            axis.grid(alpha=.2)
            st.pyplot(figure, width='stretch')
            plt.close(figure)

        with dashboard_column_2:
            genre_counts = filtered_genres.groupby('genre_name')['movie_id'].nunique().sort_values(ascending=False).head(8)
            figure, axis = plt.subplots(figsize=(5, 3))
            wedges, texts, autotexts = axis.pie(genre_counts, labels=genre_counts.index, autopct='%1.0f%%', 
                    startangle=90, wedgeprops={'width': .4}, pctdistance=0.75,
                    textprops={'fontsize': 7})
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(7)
            axis.set_title('Genre Share (Donut)', fontsize=10, fontweight='bold')
            st.pyplot(figure, width='stretch')
            plt.close(figure)

        with dashboard_column_3:
            revenue_leaders = filtered_movies.nlargest(10, 'revenue').set_index('title')['revenue'].sort_values()
            figure, axis = plt.subplots(figsize=(5, 3))
            axis.barh(revenue_leaders.index, revenue_leaders.values, color='#2878d0')
            axis.set_title('Top Revenue (Bar)', fontsize=10, fontweight='bold')
            axis.set_xlabel('Revenue', fontsize=8)
            axis.tick_params(axis='y', labelsize=7)
            st.pyplot(figure, width='stretch')
            plt.close(figure)

        dashboard_column_4, dashboard_column_5, dashboard_column_6 = st.columns(3)

        with dashboard_column_4:
            figure, axis = plt.subplots(figsize=(5, 3))
            axis.hist(filtered_movies['vote_average'].dropna(), bins=10, 
                     color='#7754c8', edgecolor='white')
            axis.set_title('Rating Distribution (Histogram)', fontsize=10, fontweight='bold')
            axis.set_xlabel('Rating', fontsize=8)
            axis.set_ylabel('Count', fontsize=8)
            st.pyplot(figure, width='stretch')
            plt.close(figure)

        with dashboard_column_5:
            decade_counts = filtered_movies.groupby('release_decade').size().sort_values()
            figure, axis = plt.subplots(figsize=(5, 3))
            axis.barh(decade_counts.index, decade_counts.values, color='#37a24a')
            axis.set_title('Movies by Decade (Bar)', fontsize=10, fontweight='bold')
            axis.set_xlabel('Count', fontsize=8)
            axis.tick_params(axis='y', labelsize=8)
            st.pyplot(figure, width='stretch')
            plt.close(figure)

        with dashboard_column_6:
            directors = filtered_crew[filtered_crew['job'].str.lower() == 'director']
            director_counts = directors.groupby('person_name').size().sort_values(ascending=True).tail(5)
            figure, axis = plt.subplots(figsize=(5, 3))
            axis.barh(director_counts.index, director_counts.values, color='#26a69a')
            axis.set_title('Top Directors (Bar)', fontsize=10, fontweight='bold')
            axis.set_xlabel('Movies', fontsize=8)
            axis.tick_params(axis='y', labelsize=7)
            st.pyplot(figure, width='stretch')
            plt.close(figure)

        dashboard_column_7, dashboard_column_8, dashboard_column_9 = st.columns(3)

        with dashboard_column_7:
            actor_counts = filtered_cast.groupby('actor_name').size().sort_values(ascending=True).tail(5)
            figure, axis = plt.subplots(figsize=(5, 3))
            axis.barh(actor_counts.index, actor_counts.values, color='#f5b400')
            axis.set_title('Top Actors (Bar)', fontsize=10, fontweight='bold')
            axis.set_xlabel('Appearances', fontsize=8)
            axis.tick_params(axis='y', labelsize=7)
            st.pyplot(figure, width='stretch')
            plt.close(figure)

        with dashboard_column_8:
            budget_data = filtered_movies[filtered_movies['budget'] > 0].copy()
            budget_bands = pd.cut(budget_data['budget'], 
                                bins=[0, 10_000_000, 50_000_000, 100_000_000, 200_000_000, float('inf')], 
                                labels=['$0-10M', '$10-50M', '$50-100M', '$100-200M', '$200M+']).value_counts().sort_index()
            figure, axis = plt.subplots(figsize=(5, 3))
            wedges, texts, autotexts = axis.pie(budget_bands, labels=budget_bands.index, autopct='%1.0f%%', 
                    startangle=90, wedgeprops={'width': .4}, pctdistance=0.75,
                    textprops={'fontsize': 7})
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(7)
            axis.set_title('Budget Ranges (Donut)', fontsize=10, fontweight='bold')
            st.pyplot(figure, width='stretch')
            plt.close(figure)

        with dashboard_column_9:
            average_revenue = filtered_movies['revenue'].mean()
            median_rating = filtered_movies['vote_average'].median()
            st.metric('Avg Revenue', money(average_revenue))
            st.metric('Median Rating', f'{median_rating:.2f}' if pd.notna(median_rating) else 'N/A')

        st.markdown('---')
        st.subheader('📊 Dashboard Summary')
        top_movie = filtered_movies.loc[filtered_movies['revenue'].idxmax(), 'title']
        top_genre = filtered_genres.groupby('genre_name')['movie_id'].nunique().sort_values(ascending=False)
        top_actor = filtered_cast.groupby('actor_name').size().sort_values(ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'**🎬 Total Movies:** {len(filtered_movies):,}')
            st.markdown(f'**💰 Top Revenue Movie:** {top_movie}')
            st.markdown(f'**🎭 Leading Genre:** {top_genre.index[0]}' if not top_genre.empty else '**🎭 Leading Genre:** N/A')
        with col2:
            st.markdown(f'**⭐ Average Rating:** {filtered_movies["vote_average"].mean():.2f}')
            st.markdown(f'**🎥 Most Featured Actor:** {top_actor.index[0]}' if not top_actor.empty else '**🎥 Most Featured Actor:** N/A')
            st.markdown(f'**📅 Year Range:** {int(filtered_movies["release_year"].min())}-{int(filtered_movies["release_year"].max())}')

elif page == 'Query':
    st.title('Query Explorer')
    st.caption('Pick a saved SQL query, run it against the Movie analytics database, and view the result.')

    # Pre-written queries (the 10 SQL analysis questions)
    SAVED_QUERIES = {
        'Q1 - Action movies released after 2015': {
            'sql': """SELECT m.title, m.release_date
FROM movies m
JOIN movie_genres mg ON mg.movie_id = m.movie_id
JOIN genres g        ON g.genre_id  = mg.genre_id
WHERE g.genre_name = 'Action'
  AND m.release_date > '2015-12-31'
ORDER BY m.release_date;""",
            'insight': 'Action remains one of the most consistently produced genres after 2015.'
        },
        'Q2 - Top 10 highest-grossing movies with genre(s)': {
            'sql': """SELECT m.title, m.revenue,
       GROUP_CONCAT(g.genre_name ORDER BY g.genre_name SEPARATOR ', ') AS genres
FROM movies m
JOIN movie_genres mg ON mg.movie_id = m.movie_id
JOIN genres g        ON g.genre_id  = mg.genre_id
GROUP BY m.movie_id, m.title, m.revenue
ORDER BY m.revenue DESC
LIMIT 10;""",
            'insight': 'The box-office leaders are franchise and effects-driven Action/Adventure titles.'
        },
        'Q3 - Average budget & revenue per genre': {
            'sql': """SELECT g.genre_name,
       ROUND(AVG(m.budget))  AS avg_budget,
       ROUND(AVG(m.revenue)) AS avg_revenue
FROM genres g
JOIN movie_genres mg ON mg.genre_id = g.genre_id
JOIN movies m        ON m.movie_id  = mg.movie_id
GROUP BY g.genre_name
ORDER BY avg_revenue DESC;""",
            'insight': 'High-budget genres (Adventure, Fantasy, Science Fiction) also earn the most on average.'
        },
        'Q4 - Top 10 actors by number of movies': {
            'sql': """SELECT actor_name, COUNT(DISTINCT movie_id) AS movie_count
FROM `cast`
GROUP BY actor_name
ORDER BY movie_count DESC
LIMIT 10;""",
            'insight': 'The leaderboard is dominated by prolific supporting/character actors.'
        },
        'Q5 - Directors with more than 3 movies': {
            'sql': """SELECT person_name AS director, COUNT(DISTINCT movie_id) AS movie_count
FROM crew
WHERE job = 'Director'
GROUP BY person_name
HAVING COUNT(DISTINCT movie_id) > 3
ORDER BY movie_count DESC;""",
            'insight': 'Only a small group of directors have more than three films in the dataset.'
        },
        'Q6 - Top 10 most frequently used keywords': {
            'sql': """SELECT keyword_name, COUNT(*) AS times_used
FROM movie_keywords
GROUP BY keyword_name
ORDER BY times_used DESC
LIMIT 10;""",
            'insight': 'Frequent keywords describe recurring themes - the basis of content-similarity recommendations.'
        },
        'Q7 - Above-average budget but below-average revenue': {
            'sql': """SELECT title, budget, revenue
FROM movies
WHERE budget  > (SELECT AVG(budget)  FROM movies WHERE budget  > 0)
  AND revenue < (SELECT AVG(revenue) FROM movies WHERE revenue > 0)
  AND budget > 0 AND revenue > 0
ORDER BY budget DESC;""",
            'insight': 'These are likely commercial under-performers worth a closer risk review.'
        },
        'Q8 - Actors in a Christopher Nolan movie': {
            'sql': """SELECT DISTINCT c.actor_name
FROM `cast` c
JOIN crew cr ON cr.movie_id = c.movie_id
WHERE cr.job = 'Director'
  AND cr.person_name = 'Christopher Nolan'
ORDER BY c.actor_name;""",
            'insight': 'Reflects the recurring ensemble cast across Nolan-directed films.'
        },
        'Q9 - Highest average-rated genre (>= 20 movies)': {
            'sql': """SELECT g.genre_name,
       ROUND(AVG(m.vote_average), 2) AS avg_rating,
       COUNT(*) AS movie_count
FROM genres g
JOIN movie_genres mg ON mg.genre_id = g.genre_id
JOIN movies m        ON m.movie_id  = mg.movie_id
GROUP BY g.genre_name
HAVING COUNT(*) >= 20
ORDER BY avg_rating DESC;""",
            'insight': 'Audience-favourite genres are not always the highest-grossing ones.'
        },
        'Q10 - Top 10 movies by number of keywords': {
            'sql': """SELECT m.title, COUNT(mk.keyword_id) AS keyword_count
FROM movies m
JOIN movie_keywords mk ON mk.movie_id = m.movie_id
GROUP BY m.movie_id, m.title
ORDER BY keyword_count DESC
LIMIT 10;""",
            'insight': 'Richly tagged movies give recommendation engines more signal to match on.'
        },
    }

    @st.cache_data
    def run_saved_query(sql_text):
        engine = create_engine('mysql+pymysql://root:1234@localhost/Movie analytics')
        try:
            return pd.read_sql(sql_text, engine)
        finally:
            engine.dispose()

    choice = st.selectbox('Choose a saved query', list(SAVED_QUERIES.keys()))
    selected = SAVED_QUERIES[choice]

    with st.expander('Show SQL', expanded=False):
        st.code(selected['sql'], language='sql')

    try:
        result = run_saved_query(selected['sql'])
    except Exception as error:
        st.error('The query could not be executed against the Movie analytics database.')
        st.code(str(error))
        st.stop()

    st.markdown(f'**Rows returned:** {len(result):,}')
    st.dataframe(result, width='stretch')

    # Simple auto-chart: numeric column plotted against the first text/label column
    text_cols = [c for c in result.columns if result[c].dtype == object]
    numeric_cols = [c for c in result.columns if pd.api.types.is_numeric_dtype(result[c])]
    if text_cols and numeric_cols and not result.empty:
        label_col = text_cols[0]
        value_col = numeric_cols[0]
        chart_df = result.head(10).set_index(label_col)[value_col].sort_values()
        figure, axis = plt.subplots(figsize=(10, 5))
        axis.barh(chart_df.index.astype(str), chart_df.values, color='#277da1')
        axis.set_title(f'{value_col} by {label_col} (top rows)', fontsize=12, fontweight='bold')
        axis.set_xlabel(value_col)
        for i, val in enumerate(chart_df.values):
            axis.text(val, i, f' {val:,.0f}', va='center', fontsize=8)
        st.pyplot(figure, width='stretch')
        plt.close(figure)

    st.info(f"**Insight:** {selected['insight']}")
    st.download_button('Download result as CSV',
                       result.to_csv(index=False).encode('utf-8'),
                       file_name=f"{choice.split(' - ')[0]}_result.csv",
                       mime='text/csv')
