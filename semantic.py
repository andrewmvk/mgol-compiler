from scanner import Token, symbolsTable

file = []
t_number = 0

class Semantic:
	@staticmethod
	def rule5(token: Token, stack_semant: list[Token]):
		file.append("")
		file.append("")
		file.append("")

	@staticmethod
	def rule6(token: Token, stack_semant: list[Token]):
		# D → L TIPO ptv
		tipo_token = stack_semant[-2]  # TIPO
		l_token = stack_semant[-3]     # L
		# ids da lista L (deve ser uma lista de nomes de ids)
		ids = getattr(l_token, "ids", [])
		print("rule6 -> IDS: ", ids)
		print("rule6 -> TIPO: ", tipo_token.t_type)
		for id_name in ids:
			entry = symbolsTable.search(id_name)
			if entry:
				entry.t_type = tipo_token.t_type
		# Não precisa imprimir nada aqui

	@staticmethod
	def rule7(token: Token, stack_semant: list[Token]):
		# L → id vir L
		id_token = stack_semant[-3]  # id
		l_token = stack_semant[-1]   # L
		print("rule7 -> ID: ", id_token, "L: ", l_token)
		# Junta os ids da recursão à esquerda
		token.ids = [id_token.t_name] + getattr(l_token, "ids", [])
		# Imprime o lexema do id na ordem de declaração
		file.append(id_token.t_name)

	@staticmethod
	def rule8(token: Token, stack_semant: list[Token]):
		# L → id
		id_token = stack_semant[-1] 
		print("rule8 -> ID: ", id_token)
		token.ids = [id_token.t_name]
		# Imprime o lexema do id na ordem de declaração
		file.append(id_token.t_name)
    
	@staticmethod
	def rule9(token: Token, stack_semant: list[Token]):
		#TIPO→ inteiro | real | lit	
		print("rule9 -> ID: ", stack_semant)
		token.t_type = stack_semant[-1].t_class 
		file.append(token.t_type)

	@staticmethod
	def rule13(token: Token, stack_semant: list[Token]):
		id_token = stack_semant[-2] if len(stack_semant) >= 2 else None
		if id_token and id_token.t_type != "NULL":
			if id_token.t_type.lower() == "lit":
				file.append(f'scanf("%s", {id_token.t_name});')
			elif id_token.t_type.lower() == "inteiro":
				file.append(f'scanf("%d", {id_token.t_name});')
			elif id_token.t_type.lower() == "real":
				file.append(f'scanf("%lf", {id_token.t_name});')
			else:
				file.append(f'Tipo desconhecido para {id_token.t_name}')
		else:
			print(f"Erro: Variável não declarada - Linha: {id_token.line}, Coluna: {id_token.column}")
   
	@staticmethod
	def rule14(token: Token, stack_semant: list[Token]):
		arg = stack_semant[-2]
		if arg.t_type.lower() == "lit":
			file.append(f'printf("%s", {arg.t_name});')
		elif arg.t_type.lower() == "inteiro":
			file.append(f'printf("%d", {arg.t_name});')
		elif arg.t_type.lower() == "real":
			file.append(f'printf("%lf", {arg.t_name});')
		elif arg.t_type.lower() == "literal":
			file.append(f'printf({arg.t_name});')
		else:
			file.append(f'Tipo desconhecido para {arg.t_name}')
  
	@staticmethod
	def rule15(token: Token, stack_semant: list[Token]):
		generic_token = stack_semant[-1] if len(stack_semant) >= 1 else None
		token.t_type = generic_token.t_type
		token.t_name = generic_token.t_name

	@staticmethod
	def rule17(token: Token, stack_semant: list[Token]):
		id_token = stack_semant[-1] if len(stack_semant) >= 1 else None
		if id_token and id_token.t_type != "NULL":
			token.t_type = id_token.t_type
			token.t_name = id_token.t_name
		else:
			print(f"Erro: Variável não declarada - Linha: {id_token.line}, Coluna: {id_token.column}")
   
	@staticmethod
	def rule19(token: Token, stack_semant: list[Token]):
		id_token = stack_semant[-4] if len(stack_semant) >= 4 else None
		if id_token and id_token.t_type != "NULL":
			LD = stack_semant[-2] if len(stack_semant) >= 2 else None
			if LD.t_type == id_token.t_type:
				file.append(f"{id_token.t_name} = {LD.t_name};")
			else:
				print(f"Erro: Tipos diferentes para atribuição - Linha: {id_token.line}, Coluna: {id_token.column}")
		else:
			print(f"Erro: Variável não declarada - Linha: {id_token.line}, Coluna: {id_token.column}")
   
	@staticmethod
	def rule20(token: Token, stack_semant: list[Token]):
		global t_number
		oprd1 = stack_semant[-3] if len(stack_semant) >= 3 else None
		oprd2 = stack_semant[-1] if len(stack_semant) >= 1 else None
		print("rule20 -> ", oprd1, oprd2)
		if oprd1.t_type.lower() == oprd2.t_type.lower():
			opm_opr = stack_semant[-2] if len(stack_semant) >= 2 else None
			print("rule20 -> ", oprd1, oprd2, opm_opr)
			token.t_name = f"T{t_number}"
			t_number += 1
			file.append(f"{token.t_name} = {oprd1.t_name} {opm_opr.t_name} {oprd2.t_name};")
		else:
			print(f"Erro: Operandos com tipos incompatíveis - Linha: {stack_semant[-1].line}, Coluna: {stack_semant[-1].column}")

	@staticmethod
	def rule25(token: Token, stack_semant: list[Token]): #
		file.append("}")

	@staticmethod
	def rule26(token: Token, stack_semant: list[Token]): #
		exp_r = stack_semant[-3]
		print("rule26 -> ", exp_r)
		file.append(f"if ({exp_r.t_name}) " + "{")

	@staticmethod
	def rule33(token: Token, stack_semant: list[Token]): #
		exp_r = stack_semant[-3]
		file.append(f"while ({exp_r.t_name}) " + "{")

	@staticmethod
	def rule37(token: Token, stack_semant: list[Token]):
		file.append("}")	
  
	@staticmethod
	def print_file():
		for line in file:
			print(line)
  
	@staticmethod
	def default(token: Token, stack_semant: list[Token]):
		return None
