import os, time, datetime, uuid
from . import sql_handler

# Constant
HF_PATH = os.path.dirname(__file__)

def add_client(values):
    """
    Adds a client to the database.
    Arguments: tuple = (navn str, org_nr str, adresse str, vat float, valuta str)
    Returns None
    """
    
    sql = """
        INSERT INTO clients
        VALUES (?,?,?,?,?);
        """

    sql_handler.execute(sql, values)

    return

def add_invoice_item(values):
	"""
	Adds an invoice item to the database.
	Arguments: dict = {"dato": int, "id": str, "beskrivelse": str, "netto": float, "client": int}
	Optional = {"vat": float}
	Returns None
	"""

	values.setdefault("vat", None)

	sql = """
		INSERT INTO invoice_items
		VALUES (?,?,?,?,?,?,?,?)

		"""

	sql_handler.execute(sql, values)


            
            

class Kunde():

	def __init__(self, navn, org_nr, adresse, vat=0.25, valuta="NOK"):
		self.navn = navn
		self.org_nr = org_nr
		self.adresse = adresse
		self.vat = vat
		self.valuta = valuta

	def __str__(self):
		return self.navn

class Bank():

	def __init__(self, konto, iban, bic, bank):
		self.konto = konto
		self.iban = iban
		self.bic = bic
		self.bank = bank

class Faktura():

	def __init__(self):
		self.id = self.make_invoice_number()
		dates = self.get_invoice_dates()
		self.dato = dates[0]
		self.forfall = dates[1]

	def make_invoice_number(self):
		"""
		Returns a random invoice number.
		"""
		UUID = uuid.uuid4()
		return UUID.fields[1]

	def get_invoice_dates(self):
		"""
		Returns the current date and date in 30 months.
		"""
		current_time = time.time()
		dato = datetime.datetime.fromtimestamp(current_time).strftime("%d.%m.%Y")
		next_month = current_time + 2592000 #30 dager
		forfall = datetime.datetime.fromtimestamp(next_month).strftime("%d.%m.%Y")

		return (dato, forfall)

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
		


	




