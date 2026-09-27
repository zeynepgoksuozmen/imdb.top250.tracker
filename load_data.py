"""
IMDb Top 250 -> PostgreSQL yükleme betiği

Ne yapar:
1. top250.csv dosyasını okur (kolonlar: rank,name,year,rating,genre,...)
2. genre kolonundaki "Crime,Drama" gibi değerleri ayırıp benzersiz tür listesi çıkarır
3. genres tablosuna türleri ekler
4. movies tablosuna filmleri ekler (watched=False, watched_date=NULL olarak başlar)
5. movie_genres tablosuna film-tür eşleşmelerini ekler

Kullanım:
    pip install psycopg2-binary --break-system-packages
    python load_data.py

Notlar:
- Veritabanı bağlantı bilgilerini kendi ortamına göre DB_CONFIG içinde düzenle.
- Betik iki kere çalıştırılırsa veriyi tekrar eklemez (TRUNCATE ile temizleyip baştan yükler),
  bu yüzden denemeler yaparken rahatça tekrar çalıştırabilirsin.
"""

import csv
import psycopg2

# --- Kendi ayarlarına göre düzenle ---
DB_CONFIG = {
    "dbname": "imdb_top250",
    "user": "postgres",       # kendi kullanıcı adın
    "password": getpass.getpass("PostgreSQL şifreni gir: "),           # şifren varsa buraya yaz
    "host": "localhost",
    "port": 5432,
}

CSV_PATH = "top250.csv"


def parse_year(value):
    """'1994' -> 1994. Bazı veri setlerinde yıl karışık gelebilir, temizle."""
    digits = "".join(ch for ch in value if ch.isdigit())
    return int(digits[:4]) if digits else None


def parse_rating(value):
    try:
        return float(value)
    except ValueError:
        return None


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Baştan temiz başlamak için (tekrar tekrar deneme yapmak isteyebilirsin)
    cur.execute("TRUNCATE movie_genres, movies, genres RESTART IDENTITY CASCADE;")

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # 1) Benzersiz türleri topla
    all_genres = set()
    for row in rows:
        genre_field = row.get("genre", "")
        for g in genre_field.split(","):
            g = g.strip()
            if g:
                all_genres.add(g)

    genre_id_map = {}
    for genre_name in sorted(all_genres):
        cur.execute(
            "INSERT INTO genres (name) VALUES (%s) RETURNING id;",
            (genre_name,),
        )
        genre_id_map[genre_name] = cur.fetchone()[0]

    print(f"{len(genre_id_map)} tür eklendi.")

    # 2) Filmleri ekle
    movie_id_map = {}
    inserted = 0
    for row in rows:
        title = row.get("name", "").strip()
        year = parse_year(row.get("year", ""))
        rating = parse_rating(row.get("rating", ""))

        if not title or year is None or rating is None:
            print(f"Atlandı (eksik veri): {row}")
            continue

        cur.execute(
            """
            INSERT INTO movies (title, release_year, rating, watched, watched_date)
            VALUES (%s, %s, %s, FALSE, NULL)
            RETURNING id;
            """,
            (title, year, rating),
        )
        movie_id = cur.fetchone()[0]
        movie_id_map[row["rank"]] = movie_id  # rank'a göre eşleştir (aynı isim tekrar edebilir)
        inserted += 1

        # 3) Bu filmin türlerini movie_genres'e ekle
        genre_field = row.get("genre", "")
        for g in genre_field.split(","):
            g = g.strip()
            if g and g in genre_id_map:
                cur.execute(
                    "INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s);",
                    (movie_id, genre_id_map[g]),
                )

    print(f"{inserted} film eklendi.")

    conn.commit()
    cur.close()
    conn.close()
    print("Tamamlandı.")


if __name__ == "__main__":
    main()
