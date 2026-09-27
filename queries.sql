-- En çok izlediğim türler / genel tür dağılımı
SELECT m.title, m.release_year, m.rating, 
       STRING_AGG(g.name, ', ') AS genres
FROM movies m
JOIN movie_genres mg ON m.id = mg.movie_id
JOIN genres g ON g.id = mg.genre_id
GROUP BY m.id, m.title, m.release_year, m.rating
ORDER BY m.id;

SELECT g.name AS genre, COUNT(*) AS izlenen_film_sayisi
FROM movies m
JOIN movie_genres mg ON m.id = mg.movie_id
JOIN genres g ON g.id = mg.genre_id
WHERE m.watched = TRUE
GROUP BY g.name
ORDER BY izlenen_film_sayisi DESC;


-- İzlemediğim en yüksek puanlı 10 film ("watchlist")
SELECT title, release_year, rating
FROM movies
WHERE watched = FALSE
ORDER BY rating DESC
LIMIT 10;