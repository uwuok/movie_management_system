import sqlite3
import json

DB_PATH = 'movies.db'
JSON_IN_PATH = 'movies.json'
JSON_OUT_PATH = 'exported.json'

def print_movie_row(row: dict) -> None:
    """格式化輸出 movie 的 row

    Args:
        row (dict): 獲取到的 movie 的字典類型
    """
    print(
        f"{row['title']:{chr(12288)}<10}"
        f"{row['director']:{chr(12288)}<12}"
        f"{row['genre']:{chr(12288)}<5}"
        f"{row['year']:{chr(12288)}<8}"
        f"{row['rating']:{chr(12288)}<10}"
    )

def list_rpt() -> None:
    """格式化輸出
    """
    header = (
        f"{'電影名稱'}{chr(12288) * 6}"
        f"{'導演'}{chr(12288) * 10}"
        f"{'類型'}{chr(12288) * 3}"
        f"{'上映年份'}{chr(12288) * 2}"
        f"{'評分'}{chr(12288) * 2}"
    )
    separator = '─' * 80
    print()
    print(header)
    print(separator)

def create_table() -> None:
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                director TEXT NOT NULL,
                genre TEXT NOT NULL,
                year INTEGER NOT NULL,
                rating REAL CHECK(rating >= 1.0 AND rating <= 10.0)
                )
            ''')
        except sqlite3.DatabaseError as e:
            print(f'資料庫操作發生錯誤： {e}')
        except Exception as e:
            print(f'發生其它錯誤 {e}')

def import_movies() -> None:
    """從 Json 檔案導入至資料庫
    """
    try:
        with open(JSON_IN_PATH, 'r', encoding='UTF-8') as f:
            movies = json.load(f)
    except FileNotFoundError:
        print(f"檔案 {JSON_IN_PATH} 未找到！")
        return
    except json.JSONDecodeError:
        print(f"檔案 {JSON_IN_PATH} 內容格式錯誤！")
        return
    except Exception as e:
        print(f'發生其它錯誤 {e}')
        return

    with connect_db() as conn:
        cursor = conn.cursor()
        for movie in movies:
            try:
                cursor.execute("""
                    INSERT INTO movies(title, director, genre, year, rating)
                    VALUES (?, ?, ?, ?, ?)
                """, (movie['title'], movie['director'], movie['genre'], movie['year'], movie['rating']))
            except sqlite3.IntegrityError:
                print(f"電影 {movie['title']} 已存在，跳過匯入")
            except sqlite3.DatabaseError as e:
                print(f'資料庫操作發生錯誤： {e}')
            except Exception as e:
                print(f'發生其它錯誤 {e}')
        conn.commit()
    print('電影已匯入')

def search_movie() -> None:
    """查詢電影操作
    """
    y_n = input('查詢全部電影嗎？(y/n): ')
    
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            if y_n.lower() == 'y':
                cursor.execute('SELECT * FROM movies')
            else:
                title = input('請輸入電影名稱： ')
                cursor.execute('SELECT * FROM movies WHERE title LIKE ?', (f'%{title}%',))
            results = cursor.fetchall()

            if results:
                list_rpt()
                for row in results:
                    print_movie_row(row)
            else:
                print("找不到符合條件的電影")
        except sqlite3.DatabaseError as e:
            print(f'資料庫操作發生錯誤： {e}')
        except Exception as e:
            print(f'發生其它錯誤 {e}')

def add_movie() -> None:
    """新增電影操作
    """
    try:
        title = input('電影名稱： ')
        director = input('導演： ')
        genre = input('類型： ')
        year = int(input('上映年份： '))
        rating = float(input('評分 (1.0 - 10.0)： '))

        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO movies (title, director, genre, year, rating)
                VALUES (?, ?, ?, ?, ?)
            """, (title, director, genre, year, rating))
        print('電影已新增')
    except sqlite3.DatabaseError as e:
        print(f'資料庫操作發生錯誤： {e}')
    except ValueError:
        print("請確認輸入的年份和評分是有效的數值！")
    except Exception as e:
        print(f'發生其它錯誤 {e}')

def modify_movies() -> None:
    """修改電影操作
    """
    title = input('請輸入要修改的電影名稱： ')
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM movies WHERE title LIKE ?', (f'%{title}%',))
            result = cursor.fetchall()
        except sqlite3.DatabaseError as e:
            print(f'資料庫操作發生錯誤： {e}')
            return
        except Exception as e:
            print(f'發生其它錯誤 {e}')
            return

    if not result:
        print('找不到符合條件的電影')
        return

    list_rpt()
    for row in result:
        print_movie_row(row)
    print()

    new_title = input('請輸入新的電影名稱 (若不修改請直接按 Enter): ') or row['title']
    new_director = input('請輸入新的導演 (若不修改請直接按 Enter): ') or row['director']
    new_genre = input('請輸入新的類型 (若不修改請直接按 Enter): ') or row['genre']
    new_year = input('請輸入新的上映年份 (若不修改請直接按 Enter): ') or row['year']
    new_rating = input('請輸入新的評分 (1.0 - 10.0) (若不修改請直接按 Enter): ') or row['rating']

    try: 
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE movies 
                SET title = ?, director = ?, genre = ?, year = ?, rating = ? 
                WHERE title LIKE ?
            ''', (new_title, new_director, new_genre, new_year, new_rating, f'%{title}'))
            conn.commit()
            print('資料已修改')
    except sqlite3.DatabaseError as e:
        print(f'資料庫操作發生錯誤： {e}')
    except Exception as e:
        print(f'發生其它錯誤 {e}')

def delete_movies() -> None:
    y_n = input('刪除全部電影嗎？(y/n)： ')
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            if y_n.lower() == 'y':
                cursor.execute('DELETE FROM movies')
                print(f'一共刪除了 {cursor.rowcount} 筆記錄')
                return
            else:
            # elif y_n.lower() == 'n':
                rm_title = input('請輸入要刪除的電影名稱：')
                cursor.execute('SELECT * FROM movies WHERE title LIKE ?', (f'%{rm_title}%',))
                result = cursor.fetchall()
                list_rpt()
                for row in result:
                    print_movie_row(row)
                yn = input('是否要刪除？(y/n)： ')
                if yn.lower() == 'y':
                    cursor.execute('DELETE FROM movies WHERE title LIKE ?', (f'%{rm_title}%',))
                    print('電影已刪除')
        except sqlite3.DatabaseError as e:
            print(f'資料庫操作發生錯誤： {e}')
        except Exception as e:
            print(f'發生其它錯誤 {e}')

def export_movies() -> None:
    """從資料庫導出電影檔案(json)
    """
    y_n = input('匯出全部電影嗎？(y_n)： ')
    
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            if y_n.lower() == 'y':
                cursor.execute('SELECT * FROM movies')
                result = cursor.fetchall()
            else:
                ex_title = input('請輸入要匯出的電影名稱： ')
                cursor.execute('SELECT * FROM movies WHERE title LIKE ?', (f'%{ex_title}%',))
                result = cursor.fetchall()

            if not result:
                print('找不到符合條件的電影')
                return

            movie_data = []
            for row in result:
                movie_data.append({
                    'title': row['title'],
                    'director': row['director'],
                    'genre': row['genre'],
                    'year': row['year'],
                    'rating': row['rating']
                })

            with open(JSON_OUT_PATH, 'w', encoding='UTF-8') as f:
                json.dump(movie_data, f, ensure_ascii=False, indent=4)
            print('電影資料已匯出至 exported.json')
        except sqlite3.DatabaseError as e:
            print(f'資料庫操作發生錯誤： {e}')
        except Exception as e:
            print(f'發生其它錯誤 {e}')

def connect_db() -> sqlite3.Connection:
    """建立資料庫連線與相關設定

    Returns:
        sqlite3.Connection: sqlite3 所建立的連線
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 使用字典型別的 cursor
        return conn
    except sqlite3.OperationalError as e:
        print(f'資料庫連接錯誤： {e}')
        raise
    except Exception as e:
        print(f'發生其它錯誤 {e}')
        raise
