import psycopg2
import pandas
import numpy

class Database:
    """ ... """

    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
        self.cur = None
        self.Connect()
    
    def Connect(self):
        try:
            # https://www.postgresqltutorial.com/postgresql-python/connect/

            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            
            self.cur = self.conn.cursor()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    
    def Disconnect(self):
        try:
            self.cur.close()
            self.conn.close()

        except Exception as error:
            print(type(error), error)
    
    def Reconnect(self):
        self.Disconnect()
        self.Connect()

    def Insert(self, sql):
        try:
            self.cur.execute(sql)
            return True
        except Exception as error:
            print(type(error), error)
            return False

    def Read(self, sql):
        try:
            return pandas.io.sql.read_sql(sql, self.conn)
        except Exception as error:
            print(type(error), error)
            return None

    def Commit(self):
        try:
            self.conn.commit()
        except Exception as error:
            print(type(error), error)
