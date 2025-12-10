
-- Handler Call
CREATE TABLE IF NOT EXISTS nominativi(
    userId VARCHAR(20) PRIMARY KEY UNIQUE,
    nominativo VARCHAR(10)  UNIQUE, -- Nominativo personale
    team VARCHAR(10) -- Nominativo speciale
);

CREATE TABLE IF NOT EXISTS attivi(
    attiviId INTEGER PRIMARY KEY AUTOINCREMENT,
    nominativo VARCHAR(10), -- Nominativo speciale
    banda VARCHAR(10),
    modo VARCHAR(10),
    operatore VARCHAR(32), -- Nominativo dell'Operatore
    ora TIME 
);

CREATE TABLE IF NOT EXISTS storicoAttivi(
    attiviId INTEGER PRIMARY KEY AUTOINCREMENT,
    nominativo VARCHAR(10), -- Nominativo speciale
    banda VARCHAR(10),
    modo VARCHAR(10),
    operatore VARCHAR(32), -- Nominativo dell'Operatore
    oraInizio TIME,
    oraFine TIME,
    withLog boolean
);

