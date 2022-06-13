#!/usr/bin/python3
import sqlite3

class Mydb():
    def __init__(self):
        self.con = sqlite3.connect('file:clips.db?mode=rw', uri=True)
        self.cur = self.con.cursor()

    def create(self):
        self.cur.execute('''DROP table IF EXISTS clips''')
        self.cur.execute('''CREATE TABLE clips
                    (creator text, url text, duration integer, views integer, time text, published integer)''')
        self.con.commit()

    def is_url_in(self, url: str) -> bool:
        self.cur.execute("""SELECT url FROM clips WHERE url=?""", (url,))
        return True if self.cur.fetchone() else False
    
    def add(self, clip):
        url = self._url(url)
        if self.is_url_in(url):
            print(f'Duplicate not added:\n\t{url}')
            return
        self.cur.execute(
            f"INSERT INTO clips VALUES ('{clip.creator.name}','{clip.url}',"
            f"'{clip.duration}','{clip.views}','{clip.time}')"
        )
    
    def commit(self):
        self.con.commit()

if __name__ == '__main__':
    # Create table
    db = Mydb()
    db.create()
    print('Table created!')
