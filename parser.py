# parser.py

from scanner import Scanner, symbolsTable
from table_transform import table_transform
from semantic import Semantic
from scanner import Token

grammar = [
	(Token("P'"), ["P"], Semantic.default), (Token("P"), ["inicio", "V", "A"], Semantic.default),
	(Token("V"), ["varinicio", "LV"], Semantic.default), (Token("LV"), ["D", "LV"], Semantic.default),
	(Token("LV"), ["varfim", "ptv"], Semantic.rule5), (Token("D"), ["L", "TIPO", "ptv"], Semantic.rule6),
	(Token("L"), ["id", "vir", "L"], Semantic.rule7), (Token("L"), ["id"], Semantic.rule8),
	(Token("TIPO"), ["inteiro"], Semantic.rule9), (Token("TIPO"), ["real"] , Semantic.rule9),
	(Token("TIPO"), ["lit"], Semantic.rule9), (Token("A"), ["ES", "A"], Semantic.default),
	(Token("ES"), ["leia", "id", "ptv"], Semantic.rule13), (Token("ES"), ["escreva", "ARG", "ptv"], Semantic.rule14),
	(Token("ARG"), ["lit"], Semantic.rule15), (Token("ARG"), ["num"], Semantic.rule15),
	(Token("ARG"), ["id"], Semantic.rule15), (Token("A"), ["CMD", "A"], Semantic.default),
	(Token("CMD"), ["id", "rcb", "LD", "ptv"], Semantic.rule19), (Token("LD"), ["OPRD", "opm", "OPRD"], Semantic.rule20),
	(Token("LD"), ["OPRD"] , Semantic.rule15), (Token("OPRD"), ["id"] , Semantic.rule17),
	(Token("OPRD"), ["num"], Semantic.rule15), (Token("A"), ["COND", "A"], Semantic.default),
	(Token("COND"), ["CAB", "CP"], Semantic.rule25), (Token("CAB"), ["se", "ab_p", "EXP_R", "fc_p", "entao"], Semantic.rule26),
	(Token("EXP_R"), ["OPRD", "opr", "OPRD"], Semantic.rule20), (Token("CP"), ["ES", "CP"], Semantic.default),
	(Token("CP"), ["CMD", "CP"], Semantic.default), (Token("CP"), ["COND", "CP"], Semantic.default),
	(Token("CP"), ["fimse"], Semantic.default), (Token("A"), ["R", "A"], Semantic.default),
	(Token("R"), ["facaAte", "ab_p", "EXP_R", "fc_p", "CP_R"], Semantic.rule33), (Token("CP_R"), ["ES", "CP_R"], Semantic.default),
	(Token("CP_R"), ["CMD", "CP_R"], Semantic.default), (Token("CP_R"), ["COND", "CP_R"], Semantic.default),
	(Token("CP_R"), ["fimFaca"], Semantic.rule37), (Token("A"), ["fim"], Semantic.default),
]
errors = { "E1": "Esperado 'inicio'", "E2": "Esperado 'varinicio'", "E3": "Comando inválido", "E4": "Esperado 'varfim' ou 'id'", "E5": "Esperado fim de arquivo '$'", "E7": "Esperado ';'", "E9": "Esperado tipo", "E10": "Esperado ',' ou tipo", "E11": "Esperado 'id'", "E17": "Comando inválido", "E18": "Esperado '('", "E19": "Esperado '<-'", "E24": "Comando inválido", "E29": "Argumento inválido", "E30": "Operando inválido", "E31": "Esperado ';', operador ou ')'", "E33": "Esperado operador relacional", "E34": "Esperado ')'", "E35": "Esperado 'entao'", "E51": "Esperado ';' ou operador aritmético", "E55": "Comando inválido no laço"}
ACTION, GOTO = table_transform()

def parser():
	with open("model.txt", "r") as f:
		scanner = Scanner(f)
		all_tokens = scanner.tokens
		symbolsTable.print_table(); print() # Primeira impressão
		symbolsTable.print_table() # Segunda impressão
		token_iterator = iter(all_tokens)
		a = next(token_iterator, None)
		stack_sint, stack_semant = [0], []
		while True:
			if not a: break
			s = int(stack_sint[-1])
			if a.t_class not in ACTION:
				print(f"\nErro Crítico: Token com classe desconhecida '{a.t_class}'."); Semantic.houve_erro = True; a = next(token_iterator, None); continue
			action = ACTION[a.t_class][s]
			if (action.startswith("S")):
				stack_sint.append(int(action[1:])); stack_semant.append(a)
				if a.t_class == 'facaAte': Semantic.start_faca_loop()
				a = next(token_iterator, None)
			elif (action.startswith("R")):
				t = int(action[1:])
				left, right, rule = grammar[t-1]
				# --- IMPRIME A REGRA DA GRAMÁTICA ---
				print(f"{left.t_class} → {' '.join(right)}")
				num_to_pop = len(right)
				rule(token=left, stack_semant=stack_semant[-num_to_pop:])
				for _ in range(num_to_pop): stack_sint.pop(); stack_semant.pop()
				t = int(stack_sint[-1]); stack_sint.append(GOTO[left.t_class][t]); stack_semant.append(left)
			elif (action == "Acc"):
				print("Accepted")
				if not Semantic.houve_erro: Semantic.print_file()
				else: print("\nCompilação falhou devido a erros.")
				return
			else:
				Semantic.houve_erro = True
				print(f"\nErro Sintático: {errors.get(action, 'Erro desconhecido')} (Token: '{a.t_name}', Linha: {a.line})")
				sync_tokens = {'ptv', 'fim', 'fimse', 'fimFaca', '$'}
				a = next(token_iterator, None)
				while a and a.t_class not in sync_tokens: a = next(token_iterator, None)
parser()