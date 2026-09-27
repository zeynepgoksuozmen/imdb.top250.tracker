# IMDb Top 250 Film Takip Sistemi

PostgreSQL ile kurulmuş, IMDb Top 250 listesindeki filmleri tutan ve hangilerini izleyip hangilerini izlemediğimi takip etmemi sağlayan bir veritabanı projesi. SQL öğrenirken pratik yapmak için hazırladım.

## Proje ne yapıyor?

- IMDb Top 250 listesindeki 250 filmi (isim, yıl, puan, tür) veritabanında tutuyor
- Her filmi "izledim / izlemedim" olarak işaretleyebiliyorum
- Bu veri üzerinden anlamlı sorgular çıkarıyorum: en çok izlediğim tür, izlemediğim en yüksek puanlı filmler gibi

## Veritabanı şeması

Üç tablo var:

- **movies** — film bilgileri (isim, yıl, puan, izlenme durumu, izleme tarihi)
- **genres** — tür isimleri (Drama, Crime, Action, vb.)
- **movie_genres** — hangi filmin hangi türde olduğunu bağlayan köprü tablo

Bir film birden fazla türde olabildiği için (örneğin "The Godfather" hem Crime hem Drama), genre bilgisini ayrı bir tabloya ayırdım — tek tabloya "Crime, Drama" gibi tek hücrede yazmak yerine, her film-tür eşleşmesini kendi satırında tutuyorum. Bu, many-to-many ilişki kurmanın standart yolu.

```
movies ----< movie_genres >---- genres
```

## Dosyalar

| Dosya | Ne işe yarıyor |
|---|---|
| `schema.sql` | Tabloları oluşturan SQL kodu |
| `top250.csv` | IMDb Top 250 ham verisi (Kaggle) |
| `load_data.py` | CSV'yi okuyup veritabanına yükleyen Python betiği — genre kolonundaki virgülle ayrılmış değerleri otomatik ayırır |
| `queries.sql` | Projeden çıkardığım örnek/analiz sorguları |

## Nasıl çalıştırılır

1. PostgreSQL'de boş bir veritabanı oluştur: `createdb imdb_top250`
2. Şemayı yükle: `psql -d imdb_top250 -f schema.sql`
3. Gerekli Python kütüphanesini kur: `pip install psycopg2-binary`
4. `load_data.py` içindeki `DB_CONFIG` kısmını kendi PostgreSQL bilgilerine göre düzenle
5. Veriyi yükle: `python load_data.py`

## Benden çıkan istatistikler

250 filmden **65'ini** izlemişim (%26).

En çok izlediğim türler:

| Tür | İzlenen film sayısı |
|---|---|
| Drama | 39 |
| Adventure | 32 |
| Action | 20 |
| Animation | 16 |
| Comedy | 13 |

İzlemediğim ama en yüksek puanlı 10 film (bir sonraki "izleme listem"):

1. The Godfather Part II (1974) — 9.0
2. The Dark Knight (2008) — 9.0
3. The Good, the Bad and the Ugly (1966) — 8.8
4. Jai Bhim (2021) — 8.8
5. One Flew Over the Cuckoo's Nest (1975) — 8.7
6. City of God (2002) — 8.6
7. It's a Wonderful Life (1946) — 8.6
8. Seven Samurai (1954) — 8.6
9. Harakiri (1962) — 8.6
10. Terminator 2: Judgment Day (1991) — 8.6

## Öğrendiklerim

- Many-to-many ilişki kurma (köprü tablo ile)
- JOIN ile birden fazla tabloyu birleştirme
- GROUP BY ve STRING_AGG ile veriyi özetleme
- Python ile CSV verisini işleyip veritabanına aktarma
- UPDATE ile var olan kayıtları güncelleme
