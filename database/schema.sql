DROP TABLE IF EXISTS nominativi; -- Per questione TESTING

CREATE TABLE IF NOT EXISTS nominativi(
    nominativo VARCHAR(10) PRIMARY KEY UNIQUE
);

DROP TABLE IF EXISTS attivi; -- Testing
CREATE TABLE IF NOT EXISTS attivi(
    attiviId INTEGER PRIMARY KEY AUTOINCREMENT,
    nominativo VARCHAR(10), 
    banda VARCHAR(10),
    modo VARCHAR(10),
    operatore VARCHAR(32),
    ora TIME 
);
