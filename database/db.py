import sqlite3
import os
 
DB_FILE = os.path.join(os.path.dirname(__file__), "bot.db") # Database
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql") # Schema del DB

# Inizializzazione del database del bot
def initDatabase():

    '''
    Ci assicuriamo che il DB del bot esista
    '''

    # if not os.path.exists(DB_FILE): # Per questioni di testing tolgo questa condizione
    with sqlite3.connect(DB_FILE) as conn,open(SCHEMA_FILE,'r') as dbSchema:
        conn.executescript(dbSchema.read())

def getNominativi():
    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        curs.execute("SELECT * FROM nominativi")
        return curs.fetchall()

def selectNominativo(userId: str):
    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        curs.execute("SELECT * FROM nominativi where userId = ?",(userId,))
        return curs.fetchone()

def addNominativo(nominativo: str,userId: str,team:str):
    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        if selectNominativo(userId): # Se esiste modifico
            curs.execute("UPDATE nominativi SET nominativo = ? WHERE userId = ?",(nominativo,userId))
        else: # Altrimenti lo inserisco
            curs.execute("INSERT INTO nominativi (nominativo,userId,team) VALUES (?,?,?)",(nominativo,userId,team))
        conn.commit()


def getAttivi():
    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        curs.execute("SELECT * FROM attivi")
        return curs.fetchall()
    
  
def addAttivi(call: str, banda: str, modo: str, operatore: str, ora: str):
    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        curs.execute("INSERT INTO attivi (nominativo, banda, modo, operatore, ora) VALUES (?, ?, ?, ?, ?)", (call, banda, modo, operatore, ora))
        conn.commit()

def isAttivo(operatore: str):
    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        curs.execute("SELECT * FROM attivi WHERE operatore = ?", (operatore,))
        return curs.fetchone()
    
def getUtentiConcorrenti(nominativoSpeciale:str,banda:str):

    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        curs.execute("SELECT modo,operatore FROM attivi WHERE nominativo = ? AND banda = ?", (nominativoSpeciale,banda))
        return curs.fetchall()
    
