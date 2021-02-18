import sqlite3

# Context manager for SQLite database

class SQLiteCursor():
    def __init__(self, db):
        self.db = db
    def __enter__(self):
        self.conn = sqlite3.connect(self.db)
        self.conn.row_factory = sqlite3.Row
        self.curs = self.conn.cursor()
        return self.curs
    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()
        
# Context manager + modify pronouns db

class PronounDBCursor(SQLiteCursor):
    def __init__(self):
        super().__init__('euphy2.db')
        
    def __enter__(self):
        super().__enter__()
        self.curs.execute(
        '''
        CREATE TABLE IF NOT EXISTS pronouns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            obj TEXT NOT NULL,
            poss TEXT NOT NULL,
            posspro TEXT NOT NULL,
            ref TEXT NOT NULL,
            plural INTEGER DEFAULT 0
        );
        '''
        )
        return self

    def add_pronouns(self, *values):
        try:
            self.curs.execute(
            '''
            INSERT INTO pronouns(
                nom,
                obj,
                poss,
                posspro,
                ref,
                plural
            ) values ( ?, ?, ?, ?, ?, ? )
            ''', values
            )
        finally:
            pass
        return True
    
    def get_pronouns(self, *pronouns):

        pronouns = [{"p": pronoun} for pronoun in pronouns]

        values = list()
        ids = list()
        notFound = list()

        foundAll = True

        for pronoun in pronouns:
            self.curs.execute(
            '''
            SELECT * FROM pronouns WHERE
                nom=:p or obj=:p or poss=:p or posspro=:p or ref=:p
            LIMIT 1
            ''', pronoun
            )
            val = self.curs.fetchone()
            if val is None:
                foundAll = False
                notFound.append(pronoun["p"])
                continue

            if val['id'] not in ids:
                values.append(val)
                ids.append(val['id'])
        return values, foundAll, notFound

# Context manager + access sentences
class SentenceDBCursor(SQLiteCursor):
    def __init__(self):
        super().__init__('euphy2.db')
    def __enter__(self):
        super().__enter__()
        self.curs.execute(
        '''
        CREATE TABLE IF NOT EXISTS sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentence TEXT
        );
        '''
        )
        return self

    def get_random_sentence(self):
        self.curs.execute(
        '''
        SELECT sentence FROM sentences ORDER BY RANDOM() LIMIT 1; 
        '''
        )
        val = self.curs.fetchone()
        return val
    
    def add_sentences(self, sentences):

        self.curs.executemany(
        '''
        INSERT INTO sentences(sentence) VALUES(?)
        ''', sentences
        )
        

# Context manager + modify users db

class UserDBCursor(SQLiteCursor):
    def __init__(self):
        super().__init__('euphy2.db')
    
    def __enter__(self):
        super().__enter__()
        self.curs.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            names TEXT,
            pronouns TEXT
        );
        '''
        )
        return self
    
    # modify names or pronouns column for a user

    def set_field(self, id, params, field):

        if field not in ["names","pronouns"]: raise ValueError("Can only set names and pronouns via set_field")

        if params:
            paramlist = ";".join(params)
        else:
            paramlist = None

        self.curs.execute(
        '''
        SELECT * FROM users WHERE id=:id
        ''', {"id": id}
        )
        try:
            if self.curs.fetchone(): # update
                self.curs.execute(
                f'''
                UPDATE users SET {field}=? WHERE id=?
                ''', (paramlist, id)
                )
            else: # insert
                self.curs.execute(
                f'''
                INSERT INTO users(id,{field}) VALUES(?, ?)
                ''', (id, paramlist)
                )
        except:
            return False
        return True
    
    # get row of a user

    def get_row(self, id):
        self.curs.execute(
        '''
        SELECT * from users WHERE id=:id
        ''', {"id": id}
        )
        row = self.curs.fetchone()
        return row
    