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
	
	values["dato"] = time.time()

	values["forfall"] = values["dato"] + (86400 * frist)

	sql = """
		INSERT INTO invoice
		VALUES (:id,:dato,:forfall,:language,:client,:bank)
		"""
	sql_handler.execute(sql, values)

def translate_timestamp(timestamp):
	"""
	Converts timestamp to string.
	"""
	return  datetime.datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y")

	

class Generator():
	"""
	Generator takes two arguments, client (hammer_faktura.Kunde) and bank (hammer_faktura.Bank).
	Invoice data is generated automatically.
	"""

	def __init__(self, client, bank):

		# Customer data
		self.client = client
		
		# Invoice data
		self.invoice = Faktura()

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
		


	




