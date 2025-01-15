import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar los datos
st.title("Análisis de Popularidad de Anime y Manga")
st.markdown("Una herramienta interactiva para explorar datos de anime y manga.")

# Cargar archivos en local y eliminar duplicados en base a Title
anime_data = pd.read_csv('anime.csv').drop_duplicates(subset='Title')
manga_data = pd.read_csv('manga.csv').drop_duplicates(subset='Title')

# Primera pregunta: ¿Cuáles son los 10 series más populares en este momento?
st.header("Top 10 Series Más Populares")

# Filtrar las 10 series con menor valor en la columna Popularity
top_10_popular = anime_data.sort_values(by="Popularity", ascending=True).head(10)

# Ordenar las series explícitamente por Popularity de manera descendente
top_10_popular = top_10_popular.sort_values(by="Popularity", ascending=False)

# Gráfico interactivo - Barras horizontales con Score en el eje x y Vote en el hover
fig = px.bar(
    top_10_popular,
    x="Score",
    y="Title",
    orientation='h',
    text="Score",
    title="Top 10 Series Más Populares",
    labels={"Score": "Puntuación", "Title": "Título"},
    hover_data={"Vote": True, "Score": False, "Popularity": False},
    color="Title"
)
fig.update_traces(texttemplate="<b>%{y}</b> (%{text})", textposition="inside")
fig.update_layout(
    legend_visible=False,
    margin=dict(l=150, r=50, t=50, b=50),
    yaxis=dict(categoryorder="array", categoryarray=top_10_popular["Title"].tolist()),
    height=800,  # Ajustar la altura del lienzo para mayor visibilidad
    width=1000   # Ajustar el ancho del lienzo para mayor visibilidad
)

# Centrar el gráfico
st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=False)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("En este gráfico, las series están ordenadas por su popularidad (10 es la menos popular y 1 es la más popular). Cada barra tiene un color único y representa una serie, con el número dentro de la barra indicando su puntuación (Score). Al pasar el cursor sobre una barra, puedes ver el número de votos (Vote).")

# Segunda pregunta: ¿Cuáles son los géneros con más espectadores?
st.header("Géneros con Más Espectadores")

# Procesar los datos de manga para considerar todos los géneros como independientes
manga_data_expanded = manga_data.dropna(subset=["Genres"]).copy()
manga_data_expanded = manga_data_expanded.assign(
    Genre=manga_data_expanded["Genres"].str.replace("[\[\]]", "", regex=True).str.split(", ")
)
manga_data_expanded = manga_data_expanded.explode("Genre")

# Agrupar por género y calcular total de votos y puntuación media
manga_data_expanded = manga_data_expanded.rename(columns={"Votes": "Vote", "Rating": "Score"})

genre_stats = manga_data_expanded.groupby("Genre").agg({"Vote": "sum", "Score": "mean"}).reset_index()

# Ordenar por cantidad de votos
genre_stats = genre_stats.sort_values(by="Vote", ascending=False)

# Filtrar los 10 géneros más populares por defecto
top_10_genres = genre_stats.head(10)

# Filtros interactivos
st.sidebar.header("Filtros de Géneros")
selected_genres = st.sidebar.multiselect(
    "Selecciona los géneros a visualizar:", 
    genre_stats["Genre"].unique().tolist(), 
    default=top_10_genres["Genre"].tolist()
)
filtered_genre_stats = genre_stats[genre_stats["Genre"].isin(selected_genres)]

# Gráfico de barras verticales
fig_genre = px.bar(
    filtered_genre_stats,
    x="Genre",
    y="Vote",
    text="Vote",
    title="Géneros con Más Espectadores",
    labels={"Genre": "Género", "Vote": "Número de Votos"},
    hover_data={"Score": True, "Vote": False},
    color="Genre"
)
fig_genre.update_traces(textposition="outside")
fig_genre.update_layout(
    xaxis=dict(categoryorder="total descending"),
    height=600,
    width=900
)

# Centrar el gráfico
st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
st.plotly_chart(fig_genre, use_container_width=False)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("Este gráfico muestra los géneros con más espectadores, considerando cada género de forma independiente. Por defecto, se muestran los 10 géneros más populares, pero puedes utilizar los filtros a la izquierda para explorar otros géneros. En el hover, se muestra la puntuación promedio (Score) de cada género.")

# Obtener los géneros de los Top 10 animes
st.header("Géneros de los Top 10 Animes")

# Unir anime y manga para obtener géneros de los Top 10 animes
top_10_titles = top_10_popular["Title"].tolist()
manga_data_expanded = manga_data_expanded.rename(columns={"Title": "Manga_Title"})
anime_genres = top_10_popular.merge(manga_data_expanded, left_on="Title", right_on="Manga_Title", how="left")
anime_genres_top_10 = anime_genres[["Genre", "Title"]].drop_duplicates()

# Crear una columna que agrupe los nombres de los animes por género
anime_genres_top_10_grouped = anime_genres_top_10.groupby("Genre").agg(
    Count=("Title", "size"),
    Titles=("Title", lambda x: ', '.join(x))
).reset_index()

# Mostrar géneros en un gráfico de barras
fig_anime_genres = px.bar(
    anime_genres_top_10_grouped,
    x="Genre",
    y="Count",
    text="Count",
    title="Distribución de Géneros en los Top 10 Animes",
    labels={"Genre": "Género", "Count": "Cantidad"},
    hover_data={"Titles": True},
    color="Genre"
)
fig_anime_genres.update_traces(textposition="outside")
fig_anime_genres.update_layout(
    xaxis=dict(categoryorder="total descending"),
    height=600,
    width=900
)

# Centrar el gráfico
st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
st.plotly_chart(fig_anime_genres, use_container_width=False)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("Este gráfico muestra la distribución de géneros en los Top 10 animes. Los géneros se obtienen de la combinación de los datos de anime y manga. En el hover, se muestran los nombres de los animes asociados a cada género.")

# Pregunta 3: ¿Cómo se relaciona la popularidad con la puntuación de los usuarios?
st.header("Relación entre Popularidad y Puntuación")

# Filtro interactivo para seleccionar un anime
anime_titles = anime_data['Title'].tolist()
selected_anime = st.selectbox("Selecciona un anime para destacar:", options=["Ninguno"] + anime_titles)

# Gráfico de dispersión para mostrar la relación entre Popularity y Score
anime_data['Highlight'] = anime_data['Title'].apply(lambda x: x == selected_anime)
fig_corr = px.scatter(
    anime_data,
    x="Popularity",
    y="Score",
    title="Relación entre Popularidad y Puntuación",
    labels={"Popularity": "Popularidad", "Score": "Puntuación"},
    hover_data={"Title": True},
    color="Highlight",
    color_discrete_map={True: "red", False: "blue"},
    size="Score",
    size_max=20
)

# Añadir líneas de referencia para promedio de Popularidad y Score
mean_popularity = anime_data["Popularity"].mean()
mean_score = anime_data["Score"].mean()
fig_corr.add_shape(
    type="line", x0=mean_popularity, x1=mean_popularity, y0=anime_data["Score"].min(), y1=anime_data["Score"].max(),
    line=dict(color="yellow", dash="dash"),
    xref="x", yref="y"
)
fig_corr.add_shape(
    type="line", x0=anime_data["Popularity"].min(), x1=anime_data["Popularity"].max(), y0=mean_score, y1=mean_score,
    line=dict(color="yellow", dash="dash"),
    xref="x", yref="y"
)

fig_corr.update_layout(
    showlegend=False,
    height=700,
    width=900,
    margin=dict(l=50, r=50, t=50, b=50)
)

# Centrar el gráfico
st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
st.plotly_chart(fig_corr, use_container_width=False)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("Este gráfico muestra cómo se relaciona la popularidad con la puntuación de los usuarios. Puedes seleccionar un anime para destacarlo en rojo. Las líneas de referencia indican los valores promedio de popularidad y puntuación.")

anime_data['Episodes'] = pd.to_numeric(anime_data['Episodes'], errors='coerce')

# Filtrar valores nulos o no válidos
anime_data = anime_data.dropna(subset=['Episodes'])

# Definir la duración promedio por episodio en minutos (24 minutos es un valor estándar aproximado)
minutes_per_episode = 24

# Calcular la duración promedio en horas
anime_data['Total_duration_minutes'] = anime_data['Episodes'] * minutes_per_episode
average_duration_hours = anime_data['Total_duration_minutes'].mean() / 60

# Mostrar el indicador en Streamlit
st.header("Duración Promedio de los Animes")
st.metric("Duración Promedio (en horas)", f"{average_duration_hours:.2f} horas")
# Asegurarse de que la columna Episodes esté en formato numérico y omitir valores no válidos
anime_data['Episodes'] = pd.to_numeric(anime_data['Episodes'], errors='coerce')

# Filtrar valores nulos o no válidos
anime_data = anime_data.dropna(subset=['Episodes'])

# Ordenar por el número de episodios de mayor a menor y tomar los 10 primeros
anime_data_sorted = anime_data.sort_values(by="Episodes", ascending=False).head(10)

# Filtro interactivo para seleccionar más animes
st.sidebar.header("Filtros de Animes")
all_animes = anime_data_sorted['Title'].tolist()
selected_animes = st.sidebar.multiselect(
    "Selecciona los animes a visualizar:", 
    options=all_animes, 
    default=all_animes
)

# Filtrar según los animes seleccionados
filtered_animes = anime_data_sorted[anime_data_sorted['Title'].isin(selected_animes)]

# Crear gráfico de barras verticales
fig_duration = px.bar(
    filtered_animes,
    x="Title", 
    y="Episodes",
    title="Número de Episodios de los Animes",
    labels={"Title": "Anime", "Episodes": "Número de Episodios"},
    color="Title",
    text="Episodes"
)

# Personalizar el gráfico
fig_duration.update_layout(
    xaxis=dict(categoryorder="total descending"),
    height=600,
    width=1000,
    margin=dict(l=150, r=50, t=50, b=50)
)

# Centrar el gráfico en Streamlit
st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
st.plotly_chart(fig_duration, use_container_width=False)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("Este gráfico muestra el número de episodios de los animes. Los animes están ordenados de mayor a menor número de episodios. Puedes usar el filtro de la barra lateral para añadir más animes.")

# Filtrar los valores de la columna Premiered que contienen 'Summer', 'Winter', 'Fall', 'Spring' seguidos de un año mayor a 2000
anime_data['Premiered'] = anime_data['Premiered'].astype(str)

# Usamos str.extract para obtener solo las estaciones y años válidos
anime_data[['Season', 'Year']] = anime_data['Premiered'].str.extract(r'(Summer|Winter|Fall|Spring)\s(\d{4})')

# Filtrar solo los años mayores a 2000
# Reemplazar NaN con 0 en una columna específica
anime_data['Year'] = anime_data['Year'].fillna(0)
anime_data_filtered = anime_data[anime_data['Year'].astype(int, errors='ignore') > 2020]

# Agrupar por Premiered (estación y año) y seleccionar el anime con mayor popularidad
max_popularity_per_season = anime_data_filtered.loc[anime_data_filtered.groupby('Premiered')['Popularity'].idxmax()]

# Crear gráfico de barras verticales con la altura de las barras dada por la puntuación (Score)
fig = px.bar(
    max_popularity_per_season,
    x="Premiered", 
    y="Score",
    color="Title",  # El color se puede asignar por el anime
    title="Anime con Mayor Popularidad por Estación y Año",
    labels={"Premiered": "Estación y Año", "Score": "Puntuación", "Title": "Anime"},
    text="Title"
)

# Personalizar el gráfico
fig.update_layout(
    height=600,
    width=1000,
    xaxis_title="Estación y Año",
    yaxis_title="Puntuación",
    xaxis=dict(tickmode='linear', tick0=0, dtick=1),
    margin=dict(l=150, r=50, t=50, b=50)
)

# Centrar el gráfico en Streamlit
st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=False)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("Este gráfico muestra el anime con la mayor popularidad por cada estación y año (solo años > 2000). La altura de las barras refleja la puntuación (Score) de los animes más populares por temporada.")

anime_data['Studios'] = anime_data['Studios'].astype(str)

# Extraer solo el primer estudio si hay más de uno separado por comas
anime_data['Primary_Studio'] = anime_data['Studios'].str.split(',').str[0]

# Agrupar por estudio principal y calcular cuántas series tiene y su puntuación media
studio_stats = anime_data.groupby('Primary_Studio').agg(
    Series_Count=('Title', 'size'),
    Average_Score=('Score', 'mean')
).reset_index()

# Filtro interactivo para seleccionar estudios
st.sidebar.header("Filtrar por Estudio")
selected_studio = st.sidebar.selectbox(
    "Selecciona un estudio para ver detalles:",
    options=studio_stats['Primary_Studio'].unique()
)

# Filtrar los datos según el estudio seleccionado
filtered_studio_data = studio_stats[studio_stats['Primary_Studio'] == selected_studio]

# Mostrar las estadísticas del estudio seleccionado
st.header(f"Estadísticas para el Estudio: {selected_studio}")
st.write(filtered_studio_data)

# Mostrar un gráfico de barras para todos los estudios
fig = px.bar(
    studio_stats,
    x='Primary_Studio',
    y='Series_Count',
    text='Average_Score',
    title="Número de Series y Puntuación Media por Estudio",
    labels={'Primary_Studio': 'Estudio', 'Series_Count': 'Número de Series'},
    color='Average_Score'
)

# Personalizar el gráfico
fig.update_traces(texttemplate="Puntuación Media: %{text:.2f}", textposition="outside")
fig.update_layout(
    height=600,
    width=1000,
    xaxis_title="Estudio",
    yaxis_title="Número de Series",
    xaxis=dict(categoryorder="total descending")
)

# Centrar el gráfico en Streamlit
st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=False)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("Este gráfico muestra el número de series producidas por cada estudio y su puntuación media.")