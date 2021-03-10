from .. import sql_handler

sql = """
    SELECT * FROM clients;
"""

clients = sql_handler.retrieve(sql)

for c in clients:
    for l in c[:-1]:
        print(l, end=" – ")
    print(c[-1])

