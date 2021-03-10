import sys
from .. import sql_handler
    
if len(sys.argv) != 5:
    print("""
        WRONG USAGE
        Arguments: konto str, iban str, bic str, bank str
        Returns None""")

else:
    values = (sys.argv[1], sys.argv[2], sys.argv[3],sys.argv[4])

sql = """
    INSERT INTO banks (konto, iban, bic, bank)
    VALUES (?,?,?,?);
    """

sql_handler.execute(sql, values)