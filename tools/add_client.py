import sys
from .. import sql_handler
"""
Adds a client to the database.
Arguments: tuple = (navn str, org_nr str, adresse str, vat float, valuta str)
Returns None
"""
    
if len(sys.argv) != 6:
    print("""
        WRONG USAGE
        Arguments: navn str, org_nr str, adresse str, vat float, valuta str
        Returns None""")

else:
    values = (sys.argv[1], sys.argv[2], sys.argv[3],float(sys.argv[4]),sys.argv[5])

sql = """
    INSERT INTO clients (navn, org_nr, adresse, vat, valuta)
    VALUES (?,?,?,?,?);
    """

sql_handler.execute(sql, values)