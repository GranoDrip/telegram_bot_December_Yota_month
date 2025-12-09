DROP TABLE IF EXISTS nominativi; -- Per questione TESTING

-- Handler Call
CREATE TABLE IF NOT EXISTS nominativi(
    nominativo VARCHAR(10) PRIMARY KEY UNIQUE, -- Nominativo personale
    userId VARCHAR(20),
    team VARCHAR(10) -- Nominativo speciale
);

DROP TABLE IF EXISTS attivi; -- Testing
CREATE TABLE IF NOT EXISTS attivi(
    attiviId INTEGER PRIMARY KEY AUTOINCREMENT,
    nominativo VARCHAR(10), -- Nominativo speciale
    banda VARCHAR(10),
    modo VARCHAR(10),
    operatore VARCHAR(32), -- Nominativo dell'Operatore
    ora TIME 
);
