from scanner import Scanner
from table_transform import table_transform
from semantic import Semantic
from scanner import Token

grammar = [
	(Token("P'"), ["P"], Semantic.default),
	(Token("P"), ["inicio", "V", "A"], Semantic.default),
	(Token("V"), ["varinicio", "LV"], Semantic.default),
	(Token("LV"), ["D", "LV"], Semantic.default),
	(Token("LV"), ["varfim", "ptv"], Semantic.rule5),
	(Token("D"), ["L", "TIPO", "ptv"], Semantic.rule6),
	(Token("L"), ["id", "vir", "L"], Semantic.rule7),
	(Token("L"), ["id"], Semantic.rule8),
	(Token("TIPO"), ["inteiro"], Semantic.rule9),
	(Token("TIPO"), ["real"] , Semantic.rule9),
	(Token("TIPO"), ["lit"], Semantic.rule9),
	(Token("A"), ["ES", "A"], Semantic.default),
	(Token("ES"), ["leia", "id", "ptv"], Semantic.rule13),
	(Token("ES"), ["escreva", "ARG", "ptv"], Semantic.rule14),
	(Token("ARG"), ["lit"], Semantic.rule15),
	(Token("ARG"), ["num"], Semantic.rule15),
	(Token("ARG"), ["id"], Semantic.rule15),
	(Token("A"), ["CMD", "A"], Semantic.default),
	(Token("CMD"), ["id", "rcb", "LD", "ptv"], Semantic.rule19),
	(Token("LD"), ["OPRD", "opm", "OPRD"], Semantic.rule20),
	(Token("LD"), ["OPRD"] , Semantic.rule15),
	(Token("OPRD"), ["id"] , Semantic.rule17),
	(Token("OPRD"), ["num"], Semantic.rule15),
	(Token("A"), ["COND", "A"], Semantic.default),
	(Token("COND"), ["CAB", "CP"], Semantic.rule25),
	(Token("CAB"), ["se", "ab_p", "EXP_R", "fc_p", "entao"], Semantic.rule26),
	(Token("EXP_R"), ["OPRD", "opr", "OPRD"], Semantic.rule20),
	(Token("CP"), ["ES", "CP"], Semantic.default),
	(Token("CP"), ["CMD", "CP"], Semantic.default),
	(Token("CP"), ["COND", "CP"], Semantic.default),
	(Token("CP"), ["fimse"], Semantic.default),
	(Token("A"), ["R", "A"], Semantic.default),
	(Token("R"), ["facaAte", "ab_p", "EXP_R", "fc_p", "CP_R"], Semantic.rule33),
	(Token("CP_R"), ["ES", "CP_R"], Semantic.default),
	(Token("CP_R"), ["CMD", "CP_R"], Semantic.default),
	(Token("CP_R"), ["COND", "CP_R"], Semantic.default),
	(Token("CP_R"), ["fimFaca"], Semantic.rule37),
	(Token("A"), ["fim"], Semantic.default),
]

errors = {
	"E1": "Erro de sintaxe: Esperado 'inicio'",
	"E2": "Erro de sintaxe: Esperado 'varinicio'",
	"E3": "Erro de sintaxe: Esperado 'escreva' 'entao' 'senao''fimse' 'fimfaca'",
	"E4": "Erro de sintaxe: Esperado 'varfim' 'id'",
	"E5": "Erro de sintaxe: Esperado '$'",
	"E7": "Erro de sintaxe: Esperado 'ptv'",
	"E9": "Erro de sintaxe: Esperado 'inteiro' 'real' 'lit'",
	"E10": "Erro de sintaxe: Esperado 'vir' 'inteiro' 'real' 'lit'",
	"E11": "Erro de sintaxe: Esperado 'id'",
	"E17": "Erro de sintaxe: Esperado 'id' 'leia' 'escreva' 'se' 'fimse'",
	"E18": "Erro de sintaxe: Esperado 'ab_p'",
	"E19": "Erro de sintaxe: Esperado 'rcb'",
	"E24": "Erro de sintaxe: Esperado 'id' 'leia' 'escreva' 'se' 'fimse' 'facaAte' 'fimFaca' 'fim'",
	"E29": "Erro de sintaxe: Esperado 'id' 'lit' 'num'",
	"E30": "Erro de sintaxe: Esperado 'id' 'num'",
	"E31": "Erro de sintaxe: Esperado 'ptv' 'opm' 'opr' 'fc_p'",
	"E33": "Erro de sintaxe: Esperado 'opr'",
	"E34": "Erro de sintaxe: Esperado 'fc_p'",
	"E35": "Erro de sintaxe: Esperado 'entao'",
	"E51": "Erro de sintaxe: Esperado 'ptv' 'opm'",
	"E55": "Erro de sintaxe: Esperado 'id' 'leia' 'escreva' 'se' 'fimFaca'"
}



ACTION, GOTO = table_transform()

def parser():
	with open("model.txt", "r") as f:
		scanner = Scanner(f)
		a = scanner.scan()
		b = a.t_class
		stack_sint = ["$", "0"]
		stack_semant = []

		while True:
			s = int(stack_sint[-1]) # top of the stack_sint
			action = ACTION[b][s]
			if (action.startswith("S")):
				t = action[1:]
				stack_sint.append(t)
				stack_semant.append(a)  #empilha na pilha semantica
				a = scanner.scan()
				b = a.t_class
			elif (action.startswith("R")):
				t = int(action[1:])
				left, right, rule = grammar[t-1] # rule t is in the t-1 index
				for _ in range(len(right)):
					stack_sint.pop()
				t = int(stack_sint[-1])
				stack_sint.append(GOTO[left.t_class][t])
				print(f"{left.t_class} → {' '.join(right)}")
				rule(token=left, stack_semant=stack_semant)
				for _ in range(len(right)):
					stack_semant.pop()
				stack_semant.append(left)  # empilha na pilha semantica
			elif (action == "Acc"):
				print("Accepted")
				Semantic.print_file()
				return
			else:
				print(f"Error - ", errors[action],  "Linha: ", a.line, "Coluna: ", a.column)
				if action == "E7":
					print("Correção do argumento que falta ';'")
					b = "ptv"
				elif action == "E18":
					print("Correção do argumento que falta '('")
					b = "ab_p"
				elif action == "E34":
					print("Correção do argumento que falta ')'")
					b = "fc_p"
				elif action == "E1":
					print("Correção do argumento que falta 'inicio'")
					b = "inicio"
				elif action == "E2":
					print("Correção do argumento que falta 'varinicio'")
					b = "varinicio"
				elif action == "E11":
					print("Correção do argumento que falta 'id'")
					b = "id"
				elif action == "E19":
					print("Correção do argumento que falta 'rcb'")
					b = "rcb"
				elif action == "E33":
					print("Correção do argumento que falta 'opr'")
					b = "opr"
				elif action == "E35":
					print("Correção do argumento que falta 'entao'")
					b = "entao"
				else:
					a = scanner.scan()
					b = a.t_class
				if b == "$":
					print("End of file reached")
					return

parser()