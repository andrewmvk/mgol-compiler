from scanner import Scanner
from table_transform import table_transform
from semantic import Semantic
from scanner import Token

grammar = [
	("P'", ["P"], Semantic.default),
	("P", ["inicio", "V", "A"], Semantic.default),
	("V", ["varinicio", "LV"], Semantic.default),
	("LV", ["D", "LV"], Semantic.default),
	("LV", ["varfim", "ptv"], Semantic.default),
	("D", ["L", "TIPO", "ptv"], Semantic.rule6),
	("L", ["id", "vir", "L"], Semantic.rule7),
	("L", ["id"], Semantic.rule8),
	("TIPO", ["inteiro"], Semantic.rule9),
	("TIPO", ["real"] , Semantic.rule9),
	("TIPO", ["lit"], Semantic.rule9),
	("A", ["ES", "A"], Semantic.default),
	("ES", ["leia", "id", "ptv"], Semantic.rule13),
	("ES", ["escreva", "ARG", "ptv"], Semantic.rule14),
	("ARG", ["lit"], Semantic.rule15),
	("ARG", ["num"], Semantic.rule15),
	("ARG", ["id"], Semantic.rule17),
	("A", ["CMD", "A"], Semantic.default),
	("CMD", ["id", "rcb", "LD", "ptv"], Semantic.rule19),
	("LD", ["OPRD", "opm", "OPRD"], Semantic.rule20),
	("LD", ["OPRD"] , Semantic.rule15),
	("OPRD", ["id"] , Semantic.rule17),
	("OPRD", ["num"], Semantic.rule15),
	("A", ["COND", "A"], Semantic.default),
	("COND", ["CAB", "CP"], Semantic.rule25),
	("CAB", ["se", "ab_p", "EXP_R", "fc_p", "entao"], Semantic.rule26),
	("EXP_R", ["OPRD", "opr", "OPRD"], Semantic.rule27),
	("CP", ["ES", "CP"], Semantic.default),
	("CP", ["CMD", "CP"], Semantic.default),
	("CP", ["COND", "CP"], Semantic.default),
	("CP", ["fimse"], Semantic.default),
	("A", ["R", "A"], Semantic.default),
	("R", ["facaAte", "ab_p", "EXP_R", "fc_p", "CP_R"], Semantic.rule33),
	("CP_R", ["ES", "CP_R"], Semantic.default),
	("CP_R", ["CMD", "CP_R"], Semantic.default),
	("CP_R", ["COND", "CP_R"], Semantic.default),
	("CP_R", ["fimFaca"], Semantic.default),
	("A", ["fim"], Semantic.default),
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
			d = b if b != "literal" else "lit"
			action = ACTION[d][s]
			if (action.startswith("S")):
				t = action[1:]
				stack_sint.append(t)
				stack_semant.append(a)  # empilha na pilha semantica
				if a.t_class == 'facaAte': Semantic.rule37()
				a = scanner.scan()
				b = a.t_class
			elif (action.startswith("R")):
				t = int(action[1:])
				left, right, rule = grammar[t-1] # rule t is in the t-1 index
				for _ in range(len(right)):
					stack_sint.pop()
				t = int(stack_sint[-1])
				stack_sint.append(GOTO[left][t])
				print(f"{left} → {' '.join(right)}")
				new_token = Token(left)
				rule(token=new_token, stack_semant=stack_semant)
				for _ in range(len(right)):
					stack_semant.pop()
				stack_semant.append(new_token)  # empilha na pilha semantica
			elif (action == "Acc"):
				print("Accepted")
				Semantic.write_file()
				return
			else:
				print(f"Error -", errors[action],  "Linha:", a.line, "Coluna:", a.column)
				Semantic.error = True
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