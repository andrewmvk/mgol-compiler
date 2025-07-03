class Token:
  def __init__(self, t_class, t_name="", t_type="NULL", line=-1, column=-1):
    self.t_class = t_class
    self.t_name = t_name
    self.t_type = t_type
    self.line = line
    self.column = column

  def __repr__(self):
    return f"CLASSE: {self.t_class} | LEXEMA: {self.t_name} | TIPO: {self.t_type}"

class SymbolsTable:
  def __init__(self):
    self.table = {}

  def insert(self, token):
    self.table[token.t_name] = token

  def search(self, t_name):
    return self.table.get(t_name)

  def update(self, t_class, t_name, t_type):
    token = self.search(t_name)
    if token:
      token.t_class = t_class
      token.t_name = t_name
      token.t_type = t_type

  def print_table(self):
    print("Tabela de Símbolos:")
    for token in self.table.values():
        print(f"  CLASSE: {token.t_class} | LEXEMA: {token.t_name} | TIPO: {token.t_type}")

  def pre_fetch(self, reservedWords):
    for word in reservedWords:
      token = Token(t_class=word, t_name=word, t_type=word)
      self.insert(token)

reserverdWords = ["inicio", "varinicio", "varfim", "escreva", "leia", "se", "entao", "fimse", "facaAte", "fimFaca", "fim", "inteiro", "lit", "real", "literal"]

symbolsTable = SymbolsTable()
symbolsTable.pre_fetch(reserverdWords)
# symbolsTable.print_table()

def error_handler(message, line=-1, column=-1, eof=False):
  if eof:
    print("ERROR:", message, f"- END OF FILE AT LINE: {line} and COLUMN: {column}")
  else:
    print("ERROR:", message, f"- AT LINE: {line} and COLUMN: {column}")

def is_letter(h):
  return (h >= 0x41 and h <= 0x5A) or (h >= 0x61 and h <= 0x7A)

def is_digit(h):
  return h >= 0x30 and h <= 0x39

def is_tsl(h): #is tab, space, line break
  return h == 0x09 or h == 0x20 or h == 0x0A

def is_valid(h):
  return is_letter(h) or is_tsl(h) or (h >= 0x27 and h <= 0x3F) or h in [0x21, 0x22, 0x5B, 0x5C, 0x5D, 0x5F, 0x7B, 0x7D]
	#                                                            ^ includes number

class Scanner:
	def __init__(self, f):
		self.f = f
		self.line = 1
		self.column = 0
		self.tokenBuffer = ""
  
	def scan(self):
		while True:
			c = self.f.read(1)
			if not c:
				return Token("$", "$", "$", self.line, self.column)

			hexValue = ord(c)
			self.column += 1

			if hexValue == 0x22: #literal, must start with a "
				self.tokenBuffer = ""
				while True:
					prev_pos = self.f.tell()
					c = self.f.read(1)
					if not c:
						error_handler("Literal incompleto", self.line, self.column, not c)
						break
					hexValue = ord(c)
					self.column += 1

					if hexValue == 0x22: #closing the literal
						return Token("lit", self.tokenBuffer, "lit", self.line, self.column)

					if not is_valid(hexValue):
						error_handler(f"Caractere inválido na linguagem '{c}'")
					else:
						self.tokenBuffer += c

			elif is_letter(hexValue): #possible id, must start with a letter
				self.tokenBuffer = c
				while True:
					prev_pos = self.f.tell()
					c = self.f.read(1)
					if not c:
						break
					hexValue = ord(c)
					self.column += 1

					if is_letter(hexValue) or is_digit(hexValue) or hexValue == 0x5F: #standard id token handling L|D|_
						self.tokenBuffer += c
						continue
					else:
						self.f.seek(prev_pos)
						break

				found_token = symbolsTable.search(self.tokenBuffer)
				if found_token:
					found_token.line = self.line
					found_token.column = self.column
					return found_token
				else:
					new_token = Token("id", self.tokenBuffer, line=self.line, column=self.column)
					symbolsTable.insert(new_token)
					return new_token

			elif is_digit(hexValue): #number, must start with a digit
				self.tokenBuffer = c
				current_state = "integer"
				num_type = "inteiro"
				prev_pos = self.f.tell()
				while True:
					prev_pos = self.f.tell()
					c = self.f.read(1)
					if not c:
						break
					hexValue = ord(c)
					self.column += 1

					if current_state in ["integer", "exponential_digit"] and hexValue == 0x2E: #decimal number .
						next_c = self.f.read(1)
						if not next_c or not is_digit(ord(next_c)):
							self.f.seek(prev_pos)
							break
						else:
							self.column += 1
							current_state = "float"
							num_type = "real"
							self.tokenBuffer += c + next_c #D* += .D

					elif current_state in ["float", "integer"] and hexValue in [0x45, 0x65]: #exponential number E or e
						next_c = self.f.read(1)
						hexValue = ord(next_c)
						if not next_c or not (is_digit(hexValue) or hexValue in [0x2B, 0x2D]): #it is not a digit nor a + or -
							self.f.seek(prev_pos) #backtrack
							break
						else:
							exponentialBuffer = next_c
							self.column += 1
							if hexValue in [0x2B, 0x2D]: #if it is a + or -, there must be a digit after it
								next_c = self.f.read(1)
								exponentialBuffer += next_c
								hexValue = ord(next_c)
								if not next_c or not is_digit(hexValue): #it is not a digit
									self.f.seek(prev_pos) #backtrack
									break
								column+= 1

							self.tokenBuffer += c + exponentialBuffer #D* += E(+|-)D
							current_state = "exponential"
							num_type = "real"

					elif is_digit(hexValue):
						self.tokenBuffer += c
					else:
						self.f.seek(prev_pos)
						break

				return Token("num", self.tokenBuffer, num_type, line=self.line, column=self.column)

			elif hexValue == 0x7B: #comment, must start with a {
				self.tokenBuffer = ""
				while True:
					prev_pos = self.f.tell()
					c = self.f.read(1)
					if not c:
						error_handler("Comentário Incompleto", self.line, self.column, not c)
						break
					hexValue = ord(c)
					self.column += 1

					if hexValue == 0x7D: #closing comment }
						break

					if not is_valid(hexValue):
						error_handler(f"Caractere inválido na linguagem '{c}'", self.line, self.column)
					else:
						self.tokenBuffer += c

			elif hexValue >= 0x3C and hexValue <= 0x3E: #relational operators or assignment, must start with < or = or >
				self.tokenBuffer = c
				current_state = "leg" #less equal or greater
				if hexValue == 0x3C:
					current_state = "less"
				elif hexValue == 0x3D:
					current_state = "equal"
				else:
					current_state = "greater"

				current_type = "opr"
				prev_pos = self.f.tell()
				c = self.f.read(1)
				if not c:
					print("End of File")
					return Token(current_type, self.tokenBuffer, line=self.line, column=self.column)
				hexValue = ord(c)
				self.column += 1

				if current_state == "less" and hexValue == 0x2D: # <-
					self.tokenBuffer += c
					current_type = "rcb"
				elif current_state == "less" and hexValue == 0x3E: # <>
					self.tokenBuffer += c
				elif current_state in ["greater", "less"] and hexValue == 0x3D: # >= or <=
					self.tokenBuffer += c
				else:
					self.f.seek(prev_pos)

				return Token(current_type, self.tokenBuffer, line=self.line, column=self.column)

			elif hexValue in [0x2B, 0x2D, 0x2F]: #arithmetic operators + or - or /
				self.tokenBuffer = c
				return Token("opm", self.tokenBuffer, line=self.line, column=self.column)
		
			elif hexValue == 0x28: #( open parenthesis
				self.tokenBuffer = c
				return Token("ab_p", self.tokenBuffer, line=self.line, column=self.column)
		
			elif hexValue == 0x29: #) close parenthesis
				self.tokenBuffer = c
				return Token("fc_p", self.tokenBuffer, line=self.line, column=self.column)
		
			elif hexValue == 0x3B: #; semicolon
				self.tokenBuffer = c
				return Token("ptv", self.tokenBuffer, line=self.line, column=self.column)
		
			elif hexValue == 0x2C: #, comma
				self.tokenBuffer = c
				return Token("vir", self.tokenBuffer, line=self.line, column=self.column)
		
			elif is_tsl(hexValue): #ignore tab, space and line breaks
				if hexValue == 0x0A: #\n
					self.line += 1
					self.column = 0
				continue

			elif is_valid(hexValue): #valid character, but not a valid token
				error_handler(f"Caractere sem padrão definido '{c}'", self.line, self.column)
		
			else:
				error_handler(f"Caractere inválido na linguagem '{c}'", self.line, self.column)

# symbolsTable.print_table()