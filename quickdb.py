#  MIT License
#  
#  Copyright (c) 2021 Jamsson
#  
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#  
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.




import sqlite3
from sqlite3.dbapi2 import Cursor
from typing import Any

class MONGODB:

    def __init__(self, mongouri: str = None, *settings):
        if mongouri == None:
            raise TypeError('Не указан URI для подключения к MongoDB')

        from pymongo import MongoClient

        if 'mongodb://localhost' not in mongouri:
            db = mongouri.split('//')[1].split('/')[1].split('?')[0]

            conn = MongoClient(mongouri)
            seldb = conn[db]
            self.db = seldb[settings[0]]
            try:
                if settings[1] == True:
                    print('Подключено к MongoDB')
            except:
                pass
        else:
            db = settings[0]

            conn = MongoClient(mongouri)
            seldb = conn[db]
            self.db = seldb[settings[1]]
            try:
                if settings[2] == True:
                    print('Подключено к MongoDB')
            except:
                pass


    def set(self, query: str = None, value = None) -> Any:
        if query == None or value == None:
            raise TypeError('Параметры для set должны быть настроеными')
        
        x = self.db.find_one({
            '_id': query
        })

        if x == None:
            self.db.insert_one({
                '_id': query,
                'value': value
            })
            return True
        else:
            self.db.replace_one({
                '_id': query
            },
            {
                'value': value
            })
            return True

    def add(self, query: str = None, value = None) -> Any:
        if query == None or value == None:
            raise TypeError('Параметры для add должны быть настроеными')

        x = self.db.find_one({
            '_id': query
        })

        if isinstance(value, int) == False:
            raise TypeError('Значение для добавления должно быть числом')

        if x == None:
            self.db.insert_one({
                '_id': query,
                'value': value
            })
            return True
        else:
            if isinstance(x['value'], int) == False:
                raise TypeError('Текущее значение не числовое для добавления к нему')

            self.db.replace_one({
                '_id': query
            },
            {
                'value': x['value'] + value
            })
            return True

    def get(self, query: str = None) -> Any or None:
        if query == None:
            raise TypeError('Параметры для get должны быть настроеными')

        x = self.db.find_one({
            '_id': query
        })

        if x == None:
            return None
        else:
            return x['value']

    def fetch(self, query: str = None) -> Any or None:
        if query == None:
            raise TypeError('Параметры для fetch должны быть настроеными')

        x = self.db.find_one({
            '_id': query
        })

        if x == None:
            return None
        else:
            return x['value']

    def has(self, query: str = None) -> bool:
        if query == None:
            raise TypeError('Параметры для has должны быть настроеными')

        x = self.db.find_one({
            '_id': query
        })

        if x == None:
            return False
        else:
            return True

    def subtract(self, query: str = None, value = None) -> Any:
        if query == None or value == None:
            raise TypeError('Параметры для subtract должны быть настроеными')

        x = self.db.find_one({
            '_id': query
        })

        if isinstance(value, int) == False:
            raise TypeError('Значение для добавления должно быть числом')

        if x == None:
            self.db.insert_one({
                '_id': query,
                'value': value
            })
            return True
        else:
            if isinstance(x['value'], int) == False:
                raise TypeError('Текущее значение не числовое для добавления к нему')

            self.db.replace_one({
                '_id': query
            },
            {
                'value': x['value'] - value
            })
            return True

    def delete(self, query: str = None) -> Any:
        if query == None:
            raise TypeError('Параметры для delete должны быть настроеными')

        x = self.db.find_one({
            '_id': query
        })

        if x == None:
            raise TypeError('Нельзя удалить не существующие данные')
        else:
            self.db.delete_one({
                '_id': query
            })
            return True

    def all(self) -> list:
        arr = []

        for x in self.db.find():
            arr.append(x)

        return arr

class SQLITE:

    def __init__(self, dbname: str = None):
        if dbname == None:
            dbname = 'database.db'

        self.sqlite = sqlite3.connect(dbname)

        self.db = self.sqlite.cursor()

        self.db.execute('CREATE TABLE IF NOT EXISTS json (id TEXT, value TEXT)')
        self.sqlite.commit()


    def add(self, query: str = None, value = None) -> Cursor:
        """Увеличить значение в БД"""
        if query == None or value == None:
            raise TypeError('Параметры в add должны быть настроеными')

        if isinstance(value, int) == False:
            raise TypeError('Значение для добавления должно быть числом')

        self.db.execute("SELECT value FROM json WHERE id = ?", [query])
        if self.db.fetchone() == None:
            self.db.execute("INSERT INTO json VALUES (?, ?)", [query, value])
            self.sqlite.commit()
            return True
        else:
            try:
                self.db.execute("SELECT value FROM json WHERE id = ?", [query])
                int(self.db.fetchone()[0])
            except:
                raise TypeError('Текущие значение столба не число для добавления к нему')
            


            
            self.db.execute("SELECT value FROM json WHERE id = ?", [query])
            self.db.execute("UPDATE json SET value = ? WHERE id = ?", [str(int(self.db.fetchone()[0]) + value), query])
            self.sqlite.commit()
            return True


    def set(self, query: str = None, value = None) -> Cursor:
        """Установить значение в БД"""
        if query == None or value == None:
            raise TypeError('Параметры для set должны быть настроеными')

        self.db.execute("SELECT value FROM json WHERE id = ?", [query])
        if self.db.fetchone() == None:
            if isinstance(value, int) == True:
                self.db.execute("INSERT INTO json VALUES (?, ?)", [query, value])
                self.sqlite.commit()
            else:
                self.db.execute("INSERT INTO json VALUES (?, ?)", [query, value])
                self.sqlite.commit()
            return True
        else:
            if isinstance(value, int) == True:
                self.db.execute("UPDATE json SET value = ? WHERE id = ?", [value, query])
                self.sqlite.commit()
            else:
                self.db.execute("UPDATE json SET value = ? WHERE id = ?", [value, query])
                self.sqlite.commit()
            return True


    def get(self, query: str = None) -> Any or None:
        """Получить данные по ключу из БД"""
        if query == None:
            raise TypeError('Параметры get должны быть настроеными')

        self.db.execute("SELECT value FROM json WHERE id = ?", [query])
        if self.db.fetchone() == None:
            return None
        else:
            self.db.execute("SELECT value FROM json WHERE id = ?", [query])
            return self.db.fetchone()[0]

    def subtract(self, query: str = None, value = None) -> Cursor:
        """Убавить значение в БД"""
        if query == None or value == None:
            raise TypeError('Параметры для subtract должны быть настроеными')

        if isinstance(value, int) == False:
            raise TypeError('Значение для убавления должно быть числом')

        self.db.execute("SELECT value FROM json WHERE id = ?", [query])
        if self.db.fetchone() == None:
            self.db.execute("INSERT INTO json VALUES (?, ?)", [query, value])
            self.sqlite.commit()
            return True
        else:
            try:
                self.db.execute("SELECT value FROM json WHERE id = ?", [query])
                int(self.db.fetchone()[0])
            except:
                raise TypeError('Значение столба должно быть числом для убавления')
            


            
            self.db.execute("SELECT value FROM json WHERE id = ?", [query])
            self.db.execute("UPDATE json SET value = ? WHERE id = ?", [str(int(self.db.fetchone()[0]) - value), query])
            self.sqlite.commit()
            return True


    def fetch(self, query: str = None) -> Any or None:
        """Получить данные из БД по ключу"""
        if query == None:
            raise TypeError('Параметры для fetch должны быть настроеными')

        self.db.execute("SELECT value FROM json WHERE id = ?", [query])
        if self.db.fetchone() == None:
            return None
        else:
            self.db.execute("SELECT value FROM json WHERE id = ?", [query])
            return self.db.fetchone()[0]

    def has(self, query: str = None) -> bool:
        """Проверить на наличие данные в БД"""

        if query == None:
            raise TypeError('Параметры для has должны быть настроеными')
        
        self.db.execute("SELECT value FROM json WHERE id = ?", [query])
        if self.db.fetchone() == None:
            return False
        else:
            return True

    def all(self) -> list:
        """Получить все данные из БД в массиве"""
        arr = []
        self.db.execute("SELECT * FROM json")
        if self.db.execute("SELECT * FROM json") == None:
            return []


        self.db.execute("SELECT * FROM json")
        for a in self.db.fetchall():
            arr.append(a)

        return arr
    
    def delete(self, query: str = None) -> Cursor:
        """Удалить данные по ключу из БД"""

        self.db.execute("SELECT value FROM json WHERE id = ?", [query])
        if self.db.fetchone() is None:
            raise TypeError('Нельзя удалить не существующие данные из БД')
        else:
            self.db.execute("DELETE FROM json WHERE id = ?", [query])
            self.sqlite.commit()
            return True