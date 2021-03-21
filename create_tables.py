import sqlite3

connection = sqlite3.connect("hammer_faktura.db")

cursor = connection.cursor()

try: 
    # CREATE STATEMENT CLIENTS TABLE
    cursor.execute("""
        CREATE TABLE clients (
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            navn VARCHAR,
            org_nr VARCHAR UNIQUE,
            adresse VARCHAR,
            vat FLOAT,
            valuta VARCHAR
            );""")

    # CREATE STATEMENT INVOICE_ITEMS TABLE
    cursor.execute("""
        CREATE TABLE invoice_items (
            dato INTEGER,
            id VARCHAR,
            beskrivelse VARCHAR NOT NULL,
            netto FLOAT NOT NULL,
            vat FLOAT,
            client INTEGER NOT NULL,
            invoice INTEGER,
            UNIQUE (dato,id),
            FOREIGN KEY (client) REFERENCES clients (pk),
            FOREIGN KEY (invoice) REFERENCES invoices (id)
            );""")

    # CREATE STATEMENT BANKS TABLE
    cursor.execute("""
        CREATE TABLE banks (
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            konto VARCHAR,
            iban VARCHAR,
            bic VARCHAR,
            bank VARCHAR
        );""")

    # CREATE STATEMENT INVOICES TABLE
    cursor.execute("""
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY,
            dato INTEGER NOT NULL,
            forfall INTEGER NOT NULL,
            language VARCHAR NOT NULL,
            client INTEGER NOT NULL,
            bank INTEGER NOT NULL,
            FOREIGN KEY (client) REFERENCES clients (pk),
            FOREIGN KEY (bank) REFERENCES banks (pk)
        );""")

    connection.commit()
    print("hammer_faktura.db created")
except sqlite3.OperationalError:
    print("database hammer_faktura.db already exists")

cursor.close()
connection.close()