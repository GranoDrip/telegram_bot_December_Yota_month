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
    """Ritorna una tupla della forma (userId,NominativoPersonale,Team)"""
    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        curs.execute("SELECT * FROM nominativi where userId = ?",(userId,))
        return curs.fetchone()

def addNominativo(nominativo: str, userId: int, team: str):
    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()

        curs.execute("SELECT userId FROM nominativi WHERE userId = ?", (userId,))
        existing = curs.fetchone()

        if existing:
            curs.execute("UPDATE nominativi SET nominativo = ?, team = ? WHERE userId = ?", (nominativo, team, userId))
        else:
            print("INSERISCO NEL DB")
            curs.execute("INSERT INTO nominativi (userId, nominativo, team) VALUES (?, ?, ?)",(userId, nominativo, team))
        conn.commit()


    
def getAttivi(operatore:str = None):

    """ Ritorna una tupla della forma attiviId, nominativo, banda, modo, operatore, oraInizio) """

    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        if operatore is None:
            curs.execute("SELECT * FROM attivi")
            return curs.fetchall()
        else:
            curs.execute("SELECT * FROM attivi where operatore = ?",(operatore,))
            return curs.fetchone()
            
    
def addAttivi(call: str, banda: str, modo: str, operatore: str, ora: str):
    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        curs.execute("INSERT INTO attivi (nominativo, banda, modo, operatore, ora) VALUES (?, ?, ?, ?, ?)", (call, banda, modo, operatore, ora))
        conn.commit()

def isAttivo(operatore: str):
    """Ritorna una tupla della forma (id,nominativoSpeciale,banda,modo,operatore,ora) """
    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        curs.execute("SELECT * FROM attivi WHERE operatore = ?", (operatore,))
        return curs.fetchone()

def updateAttivi(operatore: str, nuova_banda: str, nuovo_modo: str):
    """ Aggiorna la banda e il modo di un operatore attivo."""
    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        curs.execute( "UPDATE attivi SET banda = ?, modo = ? WHERE operatore = ?",(nuova_banda, nuovo_modo, operatore))
        conn.commit()

def getUtentiConcorrenti(nominativoSpeciale:str,banda:str):

    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        curs.execute("SELECT modo,operatore FROM attivi WHERE nominativo = ? AND banda = ?", (nominativoSpeciale,banda))
        return curs.fetchall()
    
def addStorico(call: str, banda: str, modo: str, operatore: str, oraInizio: str,oraFine:str, withLog: bool = False):
   
    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        curs.execute(
        "INSERT INTO storicoAttivi (nominativo, banda, modo, operatore, oraInizio, oraFine, withLog) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (call,banda,modo,operatore,oraInizio,oraFine,withLog))
        conn.commit()
    
def removeAttivo(operatore:str):
        with sqlite3.connect(DB_FILE) as conn:
            curs = conn.cursor()
            curs.execute("DELETE FROM attivi WHERE operatore = ?",(operatore,))
            conn.commit()
