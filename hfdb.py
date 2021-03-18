from . import sql_handler
from . import Invoice, Client, Bank, Generator, str_to_ts
import time, uuid

def makeGenerator(id):
	"""
	Returns all invoice information from database.
	Arguments: invoice id (str)
	Returns: (hammer_faktura.Generator)
	"""

	# INVOICE!
	values = {"invoice": id}

	sql = f"""
		SELECT id, dato, forfall, language
		FROM invoices
		WHERE id=:invoice;
	"""
	result = sql_handler.retrieve_muli_wvalue(sql, values)

	invoice = Invoice(result[0][0], result[0][1], result[0][2], result[0][3])
		
	# CLIENT!
	sql = f"""
		SELECT navn, org_nr, adresse, vat, valuta
		FROM clients
		WHERE pk=(SELECT client FROM invoices WHERE id=:invoice);
	"""
	result = sql_handler.retrieve_muli_wvalue(sql, values)

	client = Client(result[0][0], result[0][1], result[0][2], result[0][3], result[0][4])

	# BANK!
	sql = f"""
		SELECT konto, iban, bic, bank
		FROM banks
		WHERE pk=(SELECT bank FROM invoices WHERE id=:invoice);
	"""
	result = sql_handler.retrieve_muli_wvalue(sql, values)

	bank = Bank(result[0][0], result[0][1], result[0][2], result[0][3])

	# INVOICE ITEMS!
	sql = """
		SELECT dato, id, beskrivelse, netto, vat
		FROM invoice_items
		WHERE invoice=:invoice;
	"""
	result = sql_handler.retrieve_muli_wvalue(sql, values)

	invoice_items = []
	for jobb in result:
		invoice_items.append({
			"dato": jobb[0],
			"id": jobb[1],
			"beskrivelse": jobb[2],
			"netto": jobb[3],
			"vat": jobb[4]
		})

	return Generator(invoice, client, bank, invoice_items)

def addItem(values):
	"""
	Adds an invoice item to the database.
	Arguments: dict = {"dato": int, "id": str, "beskrivelse": str, "netto": float, "client": int}
	Optional = {"vat": float}
	Returns None
	"""
	values.setdefault("vat", None)

	sql = """
		INSERT INTO invoice_items (dato, id, beskrivelse, netto, vat, client)
		VALUES (:dato,:id,:beskrivelse,:netto,:vat,:client)

		"""
	sql_handler.execute(sql, values)

def createInvoice(client, bank, frist=30, language="NO"):
	"""
	Creates an empty invoice without any items.
	Arguments: client int, bank int, frist=30, language="NO"
	Returns invoice number
	"""

	values = {"client": client, "bank": bank, "language": language}

	values["id"] = uuid.uuid4().fields[1]
	
	values["dato"] = int(time.time())

	values["forfall"] = int(values["dato"] + (86400 * frist))

	sql = """
		INSERT INTO invoices
		VALUES (:id,:dato,:forfall,:language,:client,:bank)
		"""
	sql_handler.execute(sql, values)

	# Retrieve the new invoice number to return 
	sql = """
		SELECT id FROM invoices WHERE dato=(SELECT MAX(dato) FROM invoices) AND client=:client;
		"""
	
	return sql_handler.retrieve_one_wvalue(sql, {"client": client})

def assignItemsByDate(invoice, _from, to):
	"""
	Assigns all items matching the date range and client to the invoice.
	Arguments: invoice int, to str, from str. Format strings like this: "01.01.1990"
	"""

	# Turn strings into timestamps
	to_ts = str_to_ts(to)
	from_ts = str_to_ts(_from)

	# Retrieve the client from the invoice
	sql = """
		SELECT client
		FROM invoices
		WHERE id = ?;
		"""
	client = sql_handler.retrieve_one_wvalue(sql, (invoice,))
	
	# Assign all invoice items matching client and daterange to the invoice.
	values = {
		"invoice": invoice,
		"to": to_ts,
		"from": from_ts,
		"client": client
	}
	
	sql = """
	UPDATE invoice_items
	SET invoice = :invoice
	WHERE dato BETWEEN :from AND :to AND client = :client;
	"""
	sql_handler.execute(sql, values)

def quickGenerator(items, client, bank, _from, to):
	"""
	Create a fast generator"
	Arguments: items list, client int, bank int, from_date str, to_date str
	(dates as strings in this format = "01.01.2001")
	Returns 
	"""
	for i in items:
		addItem(i)
	invoice = createInvoice(1, 1)
	assignItemsByDate(invoice, _from, to)
	return makeGenerator(invoice)

	