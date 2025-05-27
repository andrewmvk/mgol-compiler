from scanner import Scanner
from table_transform import table_transform

grammar = [
	("P'", ["P"]),
	("P", ["inicio", "V", "A"]),
	("V", ["varinicio", "LV"]),
	("LV", ["D", "LV"]),
	("LV", ["varfim", "ptv"]),
	("D", ["L", "TIPO", "ptv"]),
	("L", ["id", "vir", "L"]),
	("L", ["id"]),
	("TIPO", ["inteiro"]),
	("TIPO", ["real"]),
	("TIPO", ["lit"]),
	("A", ["ES", "A"]),
	("ES", ["leia", "id", "ptv"]),
	("ES", ["escreva", "ARG", "ptv"]),
	("ARG", ["lit"]),
	("ARG", ["num"]),
	("ARG", ["id"]),
	("A", ["CMD", "A"]),
	("CMD", ["id", "rcb", "LD", "ptv"]),
	("LD", ["OPRD", "opm", "OPRD"]),
	("LD", ["OPRD"]),
	("OPRD", ["id"]),
	("OPRD", ["num"]),
	("A", ["COND", "A"]),
	("COND", ["CAB", "CP"]),
	("CAB", ["se", "ab_p", "EXP_R", "fc_p", "entao"]),
	("EXP_R", ["OPRD", "opr", "OPRD"]),
	("CP", ["ES", "CP"]),
	("CP", ["CMD", "CP"]),
	("CP", ["COND", "CP"]),
	("CP", ["fimse"]),
	("A", ["R", "A"]),
	("R", ["facaAte", "ab_p", "EXP_R", "fc_p", "CP_R"]),
	("CP_R", ["ES", "CP_R"]),
	("CP_R", ["CMD", "CP_R"]),
	("CP_R", ["COND", "CP_R"]),
	("CP_R", ["fimFaca"]),
	("A", ["fim"]),
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
		stack = ["$", "0"]
		
		while True:
			s = int(stack[-1]) # top of the stack
			action = ACTION[b][s]
			#print(f"Stack: ", stack, b, s, action, "Linha: ", a.line, "Column: ", a.column)
			if (action.startswith("S")):
				t = action[1:]
				stack.append(t)
				a = scanner.scan()
				b = a.t_class
			elif (action.startswith("R")):
				t = int(action[1:])
				left, right = grammar[t-1] # rule t is in the t-1 index
				for _ in range(len(right)):
					stack.pop()
				#print(f"Stack after Pop of (", len(right), "), ",  stack)
				t = int(stack[-1])
				#print(f"GOTO: ", left, t, GOTO[left][t])
				stack.append(GOTO[left][t])
				print(f"{left} → {' '.join(right)}")
			elif (action == "Acc"):
				print("Accepted")
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
				elif action == "E1":
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