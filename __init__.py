import os, time, datetime, uuid

# Constant
HF_PATH = os.path.dirname(__file__)

class Kunde():

	def __init__(self, navn, org_nr, adresse):
		self.navn = navn
		self.org_nr = org_nr
		self.adresse = adresse


class Faktura():

	def __init__(self, client):

		# Customer data
		self.client = client
		
		# Invoice data
		self.invoice_number = self.make_invoice_number()
		dates = self.get_invoice_dates()
		self.dato = dates[0]
		self.forfall = dates[1]

		# The standard table row. Use it to populate the tr_elem_list
		self.tr_elem_mal = """
			<tr>
				<td align="left">{}</td>
				<td align="left">{}</td>
				<td align="left">{}</td>
				<td align="left">{}</td>
				<td align="right"><strong>{:.2f} {}</strong></td>
			</tr>"""
		self.tr_elem_list = ""
		self.total = 0

		# Stylesheet
		self.css = "/".join(["..", "hammer_faktura", "maler","faktura.css"])


	def generate_body(self):
		"""
		Returns the invoice body.
		"""
		with open(os.path.join(HF_PATH, "maler", "fakturamal.html")) as f:
			fakturamal = f.read()

		return fakturamal.format(self.css,
								self.client.navn,
								self.client.org_nr,
								self.client.adresse,
								self.invoice_number, 
								self.dato, 
								self.forfall, 
								self.generate_table())

	def add_to_tr_elem(self, id, navn, type, beløp, enhet, leveringsdato):
		"""
		Adds one tr_elem to the tr_elem_list with leveringsdato, id, name, type, beløp, enhet.
		I.e. it adds one row to the table.
		"""
		self.tr_elem_list += self.tr_elem_mal.format(leveringsdato, id, navn, type, beløp, enhet)
		self.total += beløp
		return

	def generate_table(self, vat=0.25):
		"""
		Generate the table.
		Presupposes the tr_elem_list has been populated.
		Keyword argument VAT=0.25
		"""
		with open(os.path.join(HF_PATH, "maler", "tabellmal.html")) as f:
			tabellmal = f.read()

		netto = self.total

		brutto = netto * (1 + vat)

		return tabellmal.format(self.tr_elem_list, netto, vat, brutto)
		

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

	




