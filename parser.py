from scanner import scanner
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

ACTION, GOTO = table_transform()

def parser():
	with open("model.txt", "r") as f:
		while True:
			token = scanner(f)
			a = token.t_class
			stack = ["$", "0"]
			
			while True:
				# print(f"Stack[-1]: '", stack[-1], "'", stack)
				s = int(stack[-1]) # top of the stack
				print(f"Stack: ", stack, a, s, ACTION[a][s])
				if (ACTION[a][s].startswith("S")):
					t = ACTION[a][s][1:]
					stack.append(t)
					a = scanner(f).t_class
				elif (ACTION[a][s].startswith("R")):
					t = int(ACTION[a][s][1:])
					left, right = grammar[t-1] # rule t is in the t-1 index
					for _ in range(len(right)):
						stack.pop()
					#print(f"Stack after Pop of (", len(right), "), ",  stack)
					t = int(stack[-1])
					print(f"GOTO: ", left, t, GOTO[left][t])
					stack.append(GOTO[left][t])
					print(f"{left} → {' '.join(right)}")
				elif (ACTION[a][s] == "Acc"):
					print("Accepted")
					return
				else:
					print(f"Error: ", a, s, ACTION[a][s])
					break
				
			if token.t_name == "$":
				break

parser()