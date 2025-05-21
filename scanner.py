class Token:
  def __init__(self, t_class, t_name="", t_type="NULL", line= -1, column= -1):
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

reserverdWords = ["inicio", "varinicio", "varfim", "escreva", "leia", "se", "entao", "fimse", "facaAte", "fimFaca", "fim", "inteiro", "literal", "real"]

symbolsTable = SymbolsTable()
symbolsTable.pre_fetch(reserverdWords)
symbolsTable.print_table()

tokenBuffer = ""

line = 1
column = 0

def error_handler(message, eof=False):
  global line
  global column
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

def scanner(f):
	global column
	global line
  
	while True:
		c = f.read(1)
		if not c:
			return Token("EOF", "$", "EOF", line, column)

		hexValue = ord(c)
		column += 1

		if hexValue == 0x22: #literal, must start with a "
			tokenBuffer = ""
			while True:
				prev_pos = f.tell()
				c = f.read(1)
				if not c:
					error_handler("Literal incompleto", not c)
					break
				hexValue = ord(c)
				column += 1

				if hexValue == 0x22: #closing the literal
					return Token("LIT", tokenBuffer, "LITERAL", line, column)

				if not is_valid(hexValue):
					error_handler(f"Caractere inválido na linguagem '{c}'")
				else:
					tokenBuffer += c

		elif is_letter(hexValue): #possible id, must start with a letter
			tokenBuffer = c
			while True:
				prev_pos = f.tell()
				c = f.read(1)
				if not c:
					break
				hexValue = ord(c)
				column += 1

				if is_letter(hexValue) or is_digit(hexValue) or hexValue == 0x5F: #standard id token handling L|D|_
					tokenBuffer += c
					continue
				else:
					f.seek(prev_pos)
					break

			found_token = symbolsTable.search(tokenBuffer)
			if found_token:
				return found_token
			else:
				new_token = Token("ID", tokenBuffer, "NULO", line, column)
				symbolsTable.insert(new_token)
				return new_token

		elif is_digit(hexValue): #number, must start with a digit
			tokenBuffer = c
			current_state = "integer"
			num_type = "INTEIRO"
			prev_pos = f.tell()
			while True:
				prev_pos = f.tell()
				c = f.read(1)
				if not c:
					break
				hexValue = ord(c)
				column += 1

				if current_state in ["integer", "exponential_digit"] and hexValue == 0x2E: #decimal number .
					next_c = f.read(1)
					if not next_c or not is_digit(ord(next_c)):
						f.seek(prev_pos)
						break
					else:
						column += 1
						current_state = "float"
						num_type = "REAL"
						tokenBuffer += c + next_c #D* += .D

				elif current_state in ["float", "integer"] and hexValue in [0x45, 0x65]: #exponential number E or e
					next_c = f.read(1)
					hexValue = ord(next_c)
					if not next_c or not (is_digit(hexValue) or hexValue in [0x2B, 0x2D]): #it is not a digit nor a + or -
						f.seek(prev_pos) #backtrack
						break
					else:
						exponentialBuffer = next_c
						column += 1
						if hexValue in [0x2B, 0x2D]: #if it is a + or -, there must be a digit after it
							next_c = f.read(1)
							exponentialBuffer += next_c
							hexValue = ord(next_c)
							if not next_c or not is_digit(hexValue): #it is not a digit
								f.seek(prev_pos) #backtrack
								break
							column+= 1

						tokenBuffer += c + exponentialBuffer #D* += E(+|-)D
						current_state = "exponential"
						num_type = "REAL"

				elif is_digit(hexValue):
					tokenBuffer += c
				else:
					f.seek(prev_pos)
					break

			return Token("NUM", tokenBuffer, num_type, line, column)

		elif hexValue == 0x7B: #comment, must start with a {
			tokenBuffer = ""
			while True:
				prev_pos = f.tell()
				c = f.read(1)
				if not c:
						error_handler("Comentário Incompleto", not c)
						break
				hexValue = ord(c)
				column+=1

				if hexValue == 0x7D: #closing comment }
					#ignored
					break

				if not is_valid(hexValue):
					error_handler(f"Caractere inválido na linguagem '{c}'")
				else:
					tokenBuffer += c

		elif hexValue >= 0x3C and hexValue <= 0x3E: #relational operators or assignment, must start with < or = or >
			tokenBuffer = c
			current_state = "leg" #less equal or greater
			if hexValue == 0x3C:
				current_state = "less"
			elif hexValue == 0x3D:
				current_state = "equal"
			else:
				current_state = "greater"

			current_type = "OPR"
			prev_pos = f.tell()
			c = f.read(1)
			if not c:
				print("End of File")
				return Token(current_type, tokenBuffer, line, column)
			hexValue = ord(c)
			column += 1

			if current_state == "less" and hexValue == 0x2D: # <-
				tokenBuffer += c
				current_type = "RCB"
			elif current_state == "less" and hexValue == 0x3E: # <>
				tokenBuffer += c
			elif current_state in ["greater", "less"] and hexValue == 0x3D: # >= or <=
				tokenBuffer += c
			else:
				f.seek(prev_pos)

			return Token(current_type, tokenBuffer, line, column)

		elif hexValue in [0x2B, 0x2D, 0x2F]: #arithmetic operators + or - or /
			tokenBuffer = c
			return Token("OPM", tokenBuffer, line, column)
	
		elif hexValue == 0x28: #( open parenthesis
			tokenBuffer = c
			return Token("AB_P", tokenBuffer, line, column)
	
		elif hexValue == 0x29: #) close parenthesis
			tokenBuffer = c
			return Token("FC_P", tokenBuffer, line, column)
	
		elif hexValue == 0x3B: #; semicolon
			tokenBuffer = c
			return Token("PT_V", tokenBuffer, line, column)
	
		elif hexValue == 0x2C: #, comma
			tokenBuffer = c
			return Token("Vir", tokenBuffer, line, column)
	
		elif is_tsl(hexValue): #ignore tab, space and line breaks
			if hexValue == 0x0A: #\n
				line += 1
				column = 0
			continue

		elif is_valid(hexValue): #valid character, but not a valid token
			error_handler(f"Caractere sem padrão definido '{c}'")
	
		else:
			error_handler(f"Caractere inválido na linguagem '{c}'")

symbolsTable.print_table()