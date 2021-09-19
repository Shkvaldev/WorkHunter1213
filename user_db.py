import sqlite3

class Users_db:

    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname)
        self.cur = self.conn.cursor()

    def lookup_user(self, user_id):
        try:
            data = self.cur.execute(f"SELECT * FROM users WHERE user_id = {user_id}").fetchone()
            if data != None:
                return data
            else:
                return None
        except Exception as e:
            print(e)
            return e

    def add_user(self, user):
        try:
            self.cur.execute(f"INSERT INTO users (user_id, lang) values ({user[0]}, '{user[1]}')")
            self.conn.commit()
            return "Ok"
        except Exception as e:
            print(e)
            return e

    def delete_user(self, user_id):
        try:
            self.cur.execute(f"DELETE FROM users WHERE user_id = {user_id}")
            return "Ok"
        except Exception as e:
            print(e)
            return e
    

    def change_lang(self, user_id):
        try:
            lang = self.cur.execute(f"SELECT lang FROM users WHERE user_id = {user_id}").fetchone()
            if lang[0] == "ru":
                self.cur.execute(f"UPDATE users SET lang = 'en' WHERE user_id = {user_id}")
                self.conn.commit()
                return {'lang': 'en'}
            elif lang[0] == "en":
                self.cur.execute(f"UPDATE users SET lang = 'ru' WHERE user_id = {user_id}")
                self.conn.commit()
                return {'lang': 'ru'}
        except Exception as e:
            print(e)
            return e

    def edit_opt(self, user_id, op_name, op_data):
        try:
            self.conn.cur.execute(f"UPDATE users SET {op_name} = '{op_data}' WHERE user_id = {user_id}")
            self.conn.commit()
            return "Ok"
        except Exception as e:
            print(e)
            return e 
