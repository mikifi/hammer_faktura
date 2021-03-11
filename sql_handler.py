import sqlite3

def execute(sql, values):
    connection = sqlite3.connect("hammer_faktura.db")

    with connection:
        cursor = connection.cursor()
        cursor.execute(sql, values)

    return

def retrieve(sql):
    connection = sqlite3.connect("hammer_faktura.db")

    with connection:
        cursor = connection.cursor()
        cursor.execute(sql)
    
    return cursor.fetchall()

def retrieve_one_wvalue(sql, values):
    connection = sqlite3.connect("hammer_faktura.db")

    with connection:
        cursor = connection.cursor()
        cursor.execute(sql, values)
    
    result = cursor.fetchall()

    return result[0][0]


