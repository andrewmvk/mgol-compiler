# semantic.py

from scanner import Token, symbolsTable

declaracoes, codigo, t_number, houve_erro = [], [], 0, False


class Semantic:
    houve_erro = False

    @staticmethod
    def start_faca_loop():
        codigo.append("do {")

    @staticmethod
    def rule5(token: Token, stack_semant: list[Token]):
        pass

    @staticmethod
    def rule6(token: Token, stack_semant: list[Token]):
        tipo_token, l_token = stack_semant[-2], stack_semant[-3]
        ids, tipo = getattr(l_token, "ids", []), tipo_token.t_type
        print(f"rule6 -> IDS:  {ids}")
        print(f"rule6 -> TIPO:  {tipo}")
        tipo_c = {"inteiro": "int", "real": "double", "lit": "literal"}.get(tipo)
        for id_name in ids:
            entry = symbolsTable.search(id_name)
            if entry and entry.t_type != "NULL":
                print(f"Erro Semântico: Variável '{id_name}' já declarada.");
                Semantic.houve_erro = True
            elif entry:
                entry.t_type = tipo; declaracoes.append(f"{tipo_c} {id_name};")

    @staticmethod
    def rule7(token: Token, stack_semant: list[Token]):
        id_token, l_token = stack_semant[-3], stack_semant[-1]
        token.ids = [id_token.t_name] + getattr(l_token, "ids", [])

    @staticmethod
    def rule8(token: Token, stack_semant: list[Token]):
        id_token = stack_semant[-1]
        token.ids = [id_token.t_name]
        print(f"rule8 -> ID: {id_token!r}")

    @staticmethod
    def rule9(token: Token, stack_semant: list[Token]):
        token.t_type = stack_semant[-1].t_type
        print(f"rule9 -> ID: {stack_semant}")

    @staticmethod
    def rule13(token: Token, stack_semant: list[Token]):
        id_token = stack_semant[-2]
        entry = symbolsTable.search(id_token.t_name)
        if not entry or entry.t_type == "NULL":
            print(f"Erro Semântico: Variável '{id_token.t_name}' não declarada.");
            Semantic.houve_erro = True;
            return
        tipo = entry.t_type.lower()
        if tipo == "lit":
            format_spec, arg = "%s", entry.t_name
        elif tipo == "inteiro":
            format_spec, arg = "%d", f"&{entry.t_name}"
        elif tipo == "real":
            format_spec, arg = "%lf", f"&{entry.t_name}"
        else:
            Semantic.houve_erro = True; return
        codigo.append(f'scanf("{format_spec}", {arg});')

    @staticmethod
    def rule14(token: Token, stack_semant: list[Token]):
        arg = stack_semant[-2]
        if arg.t_class == 'lit': codigo.append(f'printf({arg.t_name});'); return
        tipo = arg.t_type.lower()
        if tipo == "lit":
            codigo.append(f'printf("%s", {arg.t_name});')
        elif tipo == "inteiro":
            codigo.append(f'printf("%d", {arg.t_name});')
        elif tipo == "real":
            codigo.append(f'printf("%lf", {arg.t_name});')
        else:
            print(f"Erro Semântico: Tipo '{arg.t_type}' inválido para 'escreva'."); Semantic.houve_erro = True; return

    @staticmethod
    def rule15(token: Token, stack_semant: list[Token]):
        child_token = stack_semant[-1]
        if child_token.t_class == 'id':
            entry = symbolsTable.search(child_token.t_name)
            if not entry or entry.t_type == "NULL":
                print(f"Erro Semântico: Variável '{child_token.t_name}' não declarada.");
                Semantic.houve_erro, token.t_type = True, "erro"
            else:
                token.t_type = entry.t_type
        else:
            token.t_type = child_token.t_type
        token.t_name, token.line = child_token.t_name, child_token.line

    @staticmethod
    def rule17(token: Token, stack_semant: list[Token]):
        Semantic.rule15(token, stack_semant)

    @staticmethod
    def rule19(token: Token, stack_semant: list[Token]):
        id_token, ld_token = stack_semant[-4], stack_semant[-2]
        id_entry = symbolsTable.search(id_token.t_name)
        if not id_entry or id_entry.t_type == "NULL":
            print(f"Erro Semântico: Variável '{id_token.t_name}' não declarada.");
            Semantic.houve_erro = True;
            return
        if ld_token.t_type == "erro": return
        if not (
                id_entry.t_type == 'real' and ld_token.t_type == 'inteiro') and id_entry.t_type.lower() != ld_token.t_type.lower():
            print(f"Erro: Tipos diferentes para atribuição - Linha: {id_token.line}");
            Semantic.houve_erro = True;
            return
        codigo.append(f"{id_token.t_name} = {ld_token.t_name};")

    @staticmethod
    def rule20(token: Token, stack_semant: list[Token]):
        global t_number
        oprd1, oprd2, op = stack_semant[-3], stack_semant[-1], stack_semant[-2]
        # --- LOG NO FORMATO SOLICITADO ---
        print(f"rule20 ->  {oprd1!r} {oprd2!r}")
        print(f"rule20 ->  {oprd1!r} {oprd2!r} {op!r}")
        if oprd1.t_type == "erro" or oprd2.t_type == "erro": token.t_type = "erro"; return
        tipo_resultante = oprd1.t_type
        if oprd1.t_type != oprd2.t_type:
            if {oprd1.t_type, oprd2.t_type} == {'inteiro', 'real'}:
                tipo_resultante = 'real'
            else:
                print(
                    f"Erro: Operandos com tipos incompatíveis."); Semantic.houve_erro, token.t_type = True, "erro"; return
        temp_name = f"T{t_number}";
        t_number += 1
        if op.t_class == "opr":
            token.t_type = "booleano"; declaracoes.append(f"int {temp_name};")
        else:
            token.t_type = tipo_resultante
            tipo_c = {"inteiro": "int", "real": "double"}.get(tipo_resultante)
            declaracoes.append(f"{tipo_c} {temp_name};")
        token.t_name = temp_name
        codigo.append(f"{token.t_name} = {oprd1.t_name} {op.t_name} {oprd2.t_name};")

    @staticmethod
    def rule25(token: Token, stack_semant: list[Token]):
        codigo.append("}")

    @staticmethod
    def rule26(token: Token, stack_semant: list[Token]):
        exp_r = stack_semant[-3]
        print(f"rule26 ->  {exp_r!r}")
        if exp_r.t_type != "erro": codigo.append(f"if ({exp_r.t_name}) {{")

    @staticmethod
    def rule33(token: Token, stack_semant: list[Token]):
        exp_r = stack_semant[-3]
        if exp_r.t_type != "erro": codigo.append(f"}} while (!({exp_r.t_name}));")

    @staticmethod
    def rule37(token: Token, stack_semant: list[Token]):
        pass

    @staticmethod
    def print_file():
        all_declarations = sorted(list(set(declaracoes)))
        final_code = "\n".join(all_declarations) + "\n\n\n" + "\n".join(codigo)
        print(final_code)
        with open("PROGRAMA.C", "w") as f:
            f.write("#include <stdio.h>\n#include <stdbool.h>\n\n")
            f.write("typedef char literal[256];\n\nvoid main(void) {\n")
            f.write("\t/*----Variaveis----*/\n")
            for dec in all_declarations: f.write(f"\t{dec}\n")
            f.write("\n\t/*----Codigo----*/\n")
            for line in codigo: f.write(f"\t{line if line else ''}\n")
            f.write("}\n")
        print("\nArquivo PROGRAMA.C gerado com sucesso!")

    @staticmethod
    def default(token: Token, stack_semant: list[Token]):
        pass