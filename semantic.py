from scanner import Token, symbolsTable

file, declarations, tx, includes, global_declarations, final = [], [], [], [], [], []
t_number = 0

class Semantic:
	error = False
 
	@staticmethod
	def rule6(token: Token, stack_semant: list[Token]):
		# D → L TIPO ptv
		tipo_token, l_token = stack_semant[-2], stack_semant[-3]
		ids, token_type = getattr(l_token, "ids", []), tipo_token.t_type
		type_c = {"inteiro": "int", "real": "double", "literal": "literal"}.get(token_type)
		for id_name in ids:
			entry = symbolsTable.search(id_name)
			if entry and entry.t_type != "NULL":
				print(f"Erro Semântico: Variável '{id_name}' já declarada.");
				Semantic.error = True
			elif entry: 
				entry.t_type = token_type; 
				declarations.append(f"{type_c} {id_name};")
		
		if type_c == 'literal' and "typedef char literal[256];" not in global_declarations:
			global_declarations.append("typedef char literal[256];")

	@staticmethod
	def rule7(token: Token, stack_semant: list[Token]):
		# L → id vir L
		id_token, L = stack_semant[-3], stack_semant[-1]
		# Junta os ids da recursão à esquerda
		token.ids = [id_token.t_name] + getattr(L, "ids", [])

	@staticmethod
	def rule8(token: Token, stack_semant: list[Token]):
		# L → id
		id_token = stack_semant[-1] 
		token.ids = [id_token.t_name]
    
	@staticmethod
	def rule9(token: Token, stack_semant: list[Token]):
		#TIPO→ inteiro | real | lit	
		token.t_type = stack_semant[-1].t_type 

	@staticmethod
	def rule13(token: Token, stack_semant: list[Token]):
		if "#include<stdio.h>" not in includes:
			includes.append("#include<stdio.h>")
   
		# ES → leia id ptv
		id_token = stack_semant[-2]
		if id_token and id_token.t_type != "NULL":
			if id_token.t_type == "literal":
				file.append(f'scanf("%s", {id_token.t_name});')
			elif id_token.t_type == "inteiro":
				file.append(f'scanf("%d", &{id_token.t_name});')
			elif id_token.t_type == "real":
				file.append(f'scanf("%lf", &{id_token.t_name});')
			else:
				print(f"Erro Semântico: Tipo '{id_token.t_type}' inválido para 'leia'.");
				Semantic.error = True
		else:
			print(f"Erro: Variável não declarada - Linha: {id_token.line}, Coluna: {id_token.column}")
			Semantic.error = True
   
	@staticmethod
	def rule14(token: Token, stack_semant: list[Token]):
		# ES → escreva ARG ptv
		arg = stack_semant[-2]
		if arg.t_type == "lit":
			file.append(f'printf("%s", "{arg.t_name}");')
		elif arg.t_type == "literal":
			file.append(f'printf("%s", {arg.t_name});')
		elif arg.t_type == "inteiro":
			file.append(f'printf("%d", {arg.t_name});')
		elif arg.t_type == "real":
			file.append(f'printf("%lf", {arg.t_name});')
		else:
			print(f"Erro Semântico: Tipo '{arg.t_type}' inválido para 'escreva'.");
			Semantic.error = True
  
	@staticmethod
	def rule15(token: Token, stack_semant: list[Token]):
		# ARG→ literal | num
		# OPRD → num
		# LD → OPRD
		generic_token = stack_semant[-1]
		token.t_type = generic_token.t_type
		token.t_name = generic_token.t_name
		token.line = generic_token.line
		token.column = generic_token.column

	@staticmethod
	def rule17(token: Token, stack_semant: list[Token]):
		#ARG → id
		id_token = stack_semant[-1]
		if id_token and id_token.t_type != "NULL":
			token.t_type = id_token.t_type
			token.t_name = id_token.t_name
			token.line = id_token.line
			token.column = id_token.column
		else:
			print(f"Erro: Variável não declarada - Linha: {id_token.line}, Coluna: {id_token.column}")
			Semantic.error = True
   
	@staticmethod
	def rule19(token: Token, stack_semant: list[Token]):
		#CMD → id rcb LD ptv
		id_token, LD = stack_semant[-4], stack_semant[-2]
		if id_token and id_token.t_type != "NULL":
			if LD.t_type == id_token.t_type:
				file.append(f"{id_token.t_name} = {LD.t_name};")
			else:
				print(f"Erro: Tipos diferentes para atribuição - Linha: {id_token.line}, Coluna: {id_token.column}")
				Semantic.error = True
		else:
			print(f"Erro: Variável não declarada - Linha: {id_token.line}, Coluna: {id_token.column}")
			Semantic.error = True
   
	@staticmethod
	def rule20(token: Token, stack_semant: list[Token]):
		# LD → OPRD opm OPRD
		global t_number
		oprd1, oprd2, opm = stack_semant[-3], stack_semant[-1], stack_semant[-2]
		token_type = oprd1.t_type
		if oprd1.t_type != oprd2.t_type and (oprd1.t_type == 'lit' or oprd2.t_type == 'lit'):
			if {oprd1.t_type, oprd2.t_type} == {'inteiro', 'real'} and (oprd1.t_type != 'lit' or oprd2.t_type != 'lit'):
				token_type = 'real'
			else:
				print(f"Erro: Operandos com tipos incompatíveis - Linha: {stack_semant[-1].line}, Coluna: {stack_semant[-1].column}") 
				Semantic.error = True
				return
  
		token.t_type = token_type
		token.t_name = f"T{t_number}"
		t_number += 1
		type_c = {"inteiro": "int", "real": "double"}.get(token_type)
		tx.append(f"{type_c} {token.t_name};")
		file.append(f"{token.t_name} = {oprd1.t_name} {opm.t_name} {oprd2.t_name};")

	@staticmethod
	def rule25(token: Token, stack_semant: list[Token]):
		# COND → CAB CP
		file.append("}")

	@staticmethod
	def rule26(token: Token, stack_semant: list[Token]):
		# CAB → se (EXP_R) então
		exp_r = stack_semant[-3]
		file.append(f"if ({exp_r.t_name}) " + "{")

	@staticmethod
	def rule27(token: Token, stack_semant: list[Token]):
		# EXP_R→ OPRD opr OPRD
		global t_number
		oprd1, oprd2, opr = stack_semant[-3], stack_semant[-1], stack_semant[-2]
		if (oprd1.t_type in ['inteiro', 'real'] and oprd2.t_type in ['inteiro', 'real']) or {oprd1.t_type, oprd2.t_type} == {'lit', 'lit'}:
			token.t_name = f"T{t_number}"
			t_number += 1
			tx.append(f"int {token.t_name};")
			file.append(f"{token.t_name} = {oprd1.t_name} {opr.t_name} {oprd2.t_name};")
		else:
			print(f"Erro: Operandos com tipos incompatíveis - Linha: {stack_semant[-1].line}, Coluna: {stack_semant[-1].column}") 
			Semantic.error = True

	@staticmethod
	def rule33(token: Token, stack_semant: list[Token]):
		# R → facaAte (EXP_R) CP_R
		exp_r = stack_semant[-3]
		file.append("}"+f" while (!({exp_r.t_name}));")
  
	@staticmethod
	def rule37():
		file.append("do {")
  
	@staticmethod
	def write_file():
		if Semantic.error:
			print("Erro(s) encontrado(s). Arquivo não foi gerado.")
			return
 
		Semantic.formatter()
		with open("PROGRAMA.c", "w", encoding="utf-8") as f:
			for line in final:
				f.write(line + "\n")
    
		print("Arquivo PROGRAMA.c gerado com sucesso.")

	@staticmethod
	def formatter():
		nivel_indentacao = 0
  
		tx.insert(0, "/*----Variaveis temporarias----*/")
		tx.append("/*------------------------------*/")
		file[0:0] = tx + declarations
		file.insert(0, "{")
		file.insert(0, "void main(void)")
		file[0:0] = global_declarations
		file[0:0] = includes
		file.append("}")
  
		for line in file:
			line_limpa = line.strip()

			if "}" in line_limpa:
				nivel_indentacao -= 1
				nivel_indentacao = max(nivel_indentacao, 0)
    
			final.append("\t" * nivel_indentacao + line_limpa)
			if "{" in line_limpa:
				nivel_indentacao += 1

	@staticmethod
	def default(token: Token, stack_semant: list[Token]):
		pass