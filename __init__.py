import os, time, datetime, uuid
from . import sql_handler

# Constant
HF_PATH = os.path.dirname(__file__)

def add_invoice_item(values):
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

def create_invoice(client, bank, frist=30, language="NO"):

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


def assign_invoice_items(invoice, to, _from):
	"""
	Assigns all items matching the date range and client to the invoice.
	Arguments: invoice int, to str, from str. Format strings like this: "01.01.1990"
	"""

	# Turn strings into timestamps
	to_ts = string_to_timestamp(to)
	from_ts = string_to_timestamp(_from)

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
	WHERE dato BETWEEN :to AND :from AND client = :client;
	"""
	sql_handler.execute(sql, values)

def timestamp_to_string(timestamp):
	"""
	Converts timestamp to string.
	"""
	return  datetime.datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y")

def string_to_timestamp(str):
	"""
	Converts string to timestamp.
	"""
	strlist = str.split(".")

	dobj = datetime.datetime(int(strlist[2]), int(strlist[1]), int(strlist[0]))

	return int(time.mktime(dobj.timetuple()))

	

class Generator():
	"""
	Generator takes two arguments, client (hammer_faktura.Kunde) and bank (hammer_faktura.Bank).
	Invoice data is generated automatically.
	"""

	def __init__(self, client, bank):

		# Customer data
		self.client = client
		
		# Invoice data
		#self.invoice = Faktura()

		# Bank
		self.bank = bank

		# The standard table row. Use it to populate the tr_elem_list
		with open(os.path.join(HF_PATH, "maler", "tr_elem_mal.html")) as f:
			self.tr_elem_mal = f.read()

		self.tr_elem_list = []
		self.netto_total = 0
		self.brutto_total = 0

		self.table = ""

		# Stylesheet
		self.css = "/".join(["..", "hammer_faktura", "maler","faktura.css"])


	def generate_body(self):
		"""
		Returns the invoice body.
		"""
		with open(os.path.join(HF_PATH, "maler", "fakturamal.html")) as f:
			fakturamal = f.read()

		with open(os.path.join(HF_PATH, "maler", "style.html")) as f:
			style = f.read()


		return fakturamal.format(
								# CSS
								style=style,
								# Client inforamsjon
								navn=self.client.navn,
								org_nr=self.client.org_nr,
								adresse=self.client.adresse,
								# Invoice information
								id=self.invoice.id, 
								dato=self.invoice.dato, 
								forfall=self.invoice.forfall, 
								# Table
								table=self.table,
								# Bank details
								konto=self.bank.konto,
								iban=self.bank.iban,
								bic=self.bank.bic,
								bank=self.bank.bank
								)

	def add_to_invoice(self, leveringsdato, id, beskrivelse, netto, vat=None):
		"""
		Adds one tr_elem to the tr_elem_list.
		Args: leveringsdato, id, beskrivelse, netto.
		Optional: vat (float) to override client-level VAT
		I.e. it adds one row to the table.
		"""
		if not vat:
			vat = self.client.vat

		brutto = netto * (vat + 1)

		self.tr_elem_list.append(self.tr_elem_mal.format(leveringsdato=leveringsdato, 
														id=id, 
														beskrivelse=beskrivelse, 
														netto=netto, 
														vat=vat, 
														brutto=brutto))
		self.netto_total += netto
		self.brutto_total += brutto
		return

	def generate_table(self):
		"""
		Generate the table.
		Presupposes the tr_elem_list has been populated.
		"""
		with open(os.path.join(HF_PATH, "maler", "tabellmal.html")) as f:
			tabellmal = f.read()

		tabell = "\n".join(self.tr_elem_list)

		totalMVA = self.brutto_total - self.netto_total

		self.table = tabellmal.format(tabell=tabell, 
									netto=self.netto_total, 
									totalMVA=totalMVA, 
									brutto=self.brutto_total,
									valuta=self.client.valuta)

		return
		


	




