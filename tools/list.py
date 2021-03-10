from .. import sql_handler
import sys

if len(sys.argv) != 2:
    print("Usage: hammer_faktura.tools.list <table>\n(clients, banks, invoice_items)")

else:
    table = sys.argv[1]

    sql = f"""
    SELECT * FROM {table};
    """

    clients = sql_handler.retrieve(sql)

    for c in clients:
        for l in c[:-1]:
            print(l, end=" – ")
        print(c[-1])

