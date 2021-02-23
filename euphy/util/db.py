from os import getenv
import psycopg2

# Context manager for PostgreSQL database

class PostgreCursor():
    def __init__(self, db):
        self.db = db
    def __enter__(self):
        self.conn = psycopg2.connect(self.db)
        self.curs = self.conn.cursor()
        return self.curs
    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()
        
# Context manager + modify pronouns db

class PronounDBCursor(PostgreCursor):
    def __init__(self):
        super().__init__(getenv("PSYCOPG2_CONNECT_STRING"))
        
    def __enter__(self):
        super().__enter__()
        self.curs.execute(
        '''
        CREATE TABLE IF NOT EXISTS pronouns (
            id SERIAL PRIMARY KEY,
            nom TEXT NOT NULL,
            obj TEXT NOT NULL,
            poss TEXT NOT NULL,
            posspro TEXT NOT NULL,
            ref TEXT NOT NULL,
            plural BINARY DEFAULT FALSE
        );
        '''
        )
        return self

    # add pronouns to db
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
            ) values ( %s, %s, %s, %s, %s, %s )
            ''', values
            )
        except:
            return False
        return True

    # get a list of all pronoun sets
    def get_all_pronouns(self, **kwargs):
        as_tuple = kwargs.get("as_tuple", False)

        self.curs.execute(
        '''
        SELECT * FROM pronouns;
        '''
        )
        try:
            results = self.curs.fetchall()
            if not as_tuple:
                results = [{key:val for key,val in zip(("id","nom","obj","poss","posspro","ref","plural"), result)} for result in results]
            return results
        except:
            return False
    
    # get a list of certain pronoun sets (will return all found along with a flag if doesn't find every pronoun requested)
    def get_pronouns(self, *pronouns,**kwargs):

        as_tuple = kwargs.get("as_tuple", False)
        fuzzy_search = kwargs.get("fuzzy_search", False)

        pronouns = [{"p": pronoun if not fuzzy_search else f"%{pronoun}%"} for pronoun in pronouns]

        values = list()
        ids = list()
        notFound = list()

        foundAll = True

        for pronoun in pronouns:

            if fuzzy_search:
                query = '''
                SELECT * FROM PRONOUNS WHERE 
                    nom like(%(p)s) or obj like(%(p)s) or poss like(%(p)s) or posspro like(%(p)s) or ref like(%(p)s)
                '''
            else:
                query = '''
                SELECT * FROM pronouns WHERE
                    nom=%(p)s or obj=%(p)s or poss=%(p)s or posspro=%(p)s or ref=%(p)s
                '''

            self.curs.execute(query, pronoun)
            try:
                if not fuzzy_search:
                    result = self.curs.fetchall()
                else:
                    [values.append(pset) for pset in self.curs.fetchall() if not pset in values]
                    continue

                if not as_tuple:
                    results = [{key:val for key,val in zip(("id","nom","obj","poss","posspro","ref","plural"), pset)} for pset in result]
                else:
                    assert bool(result)
            except:
                result = None
            if result is None:
                foundAll = False
                notFound.append(pronoun["p"])
                continue
            if not as_tuple:
                for result in results:
                    if result['id'] not in ids:
                        values.append(result)
                        ids.append(result['id'])
            else:
                if result[0] not in ids:
                    values.append(result)
                    ids.append(result[0])
        return values, foundAll, notFound

# Context manager + access sentences
class SentenceDBCursor(PostgreCursor):
    def __init__(self):
        super().__init__(getenv("PSYCOPG2_CONNECT_STRING"))
    def __enter__(self):
        super().__enter__()
        self.curs.execute(
        '''
        CREATE TABLE IF NOT EXISTS sentences (
            id SERIAL PRIMARY KEY,
            sentence TEXT
        );
        '''
        )
        return self

    def get_random_sentence(self):
        self.curs.execute(
        '''
        SELECT * FROM sentences ORDER BY RANDOM() LIMIT 1; 
        '''
        )
        result = self.curs.fetchone()
        return {key:val for key,val in zip(("id","sentence"), result)}
    
    def add_sentences(self, sentences):

        self.curs.executemany(
        '''
        INSERT INTO sentences(sentence) VALUES(%s)
        ''', sentences
        )
        

# Context manager + modify users db

class UserDBCursor(PostgreCursor):
    def __init__(self):
        super().__init__(getenv("PSYCOPG2_CONNECT_STRING"))
    
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
        SELECT * FROM users WHERE id=%(id)s
        ''', {"id": id}
        )
        try:
            if self.curs.fetchone(): # update
                self.curs.execute(
                f'''
                UPDATE users SET {field}=%s WHERE id=%s
                ''', (paramlist, id)
                )
            else: # insert
                self.curs.execute(
                f'''
                INSERT INTO users(id,{field}) VALUES(%s, %s)
                ''', (id, paramlist)
                )
        except:
            return False
        return True
    
    # get row of a user

    def get_row(self, id):
        self.curs.execute(
        '''
        SELECT * from users WHERE id=%(id)s
        ''', {"id": id}
        )
        row = self.curs.fetchone()
        return {key: val for key,val in zip(("id", "names", "pronouns"), row)}
    