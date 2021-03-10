import sqlite3

connection = sqlite3.connect("hammer_faktura.db")

cursor = connection.cursor()

# CREATE STATEMENT CLIENT TABLE
cursor.execute("""
    CREATE TABLE clients (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        navn VARCHAR,
        org_nr VARCHAR UNIQUE,
        adresse VARCHAR,
        vat FLOAT,
        valuta VARCHAR
        );""")

# CREATE STATEMENT INVOICE ITEM TABLE
cursor.execute("""
    CREATE TABLE invoice_items (
        dato INTEGER,
        id VARCHAR,
        beskrivelse VARCHAR NOT NULL,
        netto FLOAT NOT NULL,
        vat FLOAT NOT NULL,
        client INTEGER NOT NULL,
        UNIQUE (dato,id),
        FOREIGN KEY (client) REFERENCES clients (pk)
        );""")

connection.commit()
connection.close()