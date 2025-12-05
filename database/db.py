import sqlite3
import os
 
DB_FILE = os.path.join(os.path.dirname(__file__), "bot.db") # Database
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql") # Schema del DB

# Inizializzazione del database del bot
def initDatabase():

    '''
    Ci assicuriamo che il DB del bot esista
    '''

    if not os.path.exists(DB_FILE):
        with sqlite3.connect(DB_FILE) as conn,open(SCHEMA_FILE,'r') as dbSchema:
            conn.executescript(dbSchema.read())

