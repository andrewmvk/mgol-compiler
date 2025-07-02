# scanner.py

import re

class Token:
  def __init__(self, t_class, t_name="", t_type="NULL", line=-1, column=-1):
    self.t_class, self.t_name, self.t_type = t_class, t_name, t_type
    self.line, self.column, self.ids = line, column, []

  def __repr__(self):
    # --- MUDANÇA DE FORMATO DO PRINT ---
    # Ajustado para corresponder ao log desejado
    return f"CLASSE: {self.t_class} | LEXEMA: {self.t_name} | TIPO: {self.t_type}"

class SymbolsTable:
  def __init__(self): self.table = {}
  def insert(self, token):
    if token.t_name not in self.table: self.table[token.t_name] = token
  def search(self, t_name): return self.table.get(t_name)
  def print_table(self):
    print("Tabela de Símbolos:")
    for token in self.table.values(): print(f"  {token!r}")
  def pre_fetch(self, reservedWords):
    for word in reservedWords: self.insert(Token(t_class=word, t_name=word, t_type=word))

reserverdWords = ["inicio", "varinicio", "varfim", "escreva", "leia", "se", "entao", "fimse", "facaAte", "fimFaca", "fim", "inteiro", "lit", "real"]
symbolsTable = SymbolsTable()
symbolsTable.pre_fetch(reserverdWords)

class Scanner:
    def __init__(self, f):
        self.source = f.read()
        self.tokens = self._tokenize()
        self.pos = 0

    def _tokenize(self):
        token_specs = [
            ('COMENTARIO', r'\{.*?\}'), ('NUM', r'\d+(\.\d*)?'), ('LITERAL', r'\"[^\"]*\"'),
            ('ID', r'[a-zA-Z][a-zA-Z0-9_]*'), ('RCB', r'<-'), ('OPR', r'<=|>=|<>|=|<|>'),
            ('OPM', r'\+|-|\*|/'), ('PTV', r';'), ('VIR', r','), ('AB_P', r'\('), ('FC_P', r'\)'),
            ('NEWLINE', r'\n'), ('SKIP', r'[ \t]+'), ('MISMATCH', r'.'),
        ]
        regex, line_num, line_start, tokens = '|'.join('(?P<%s>%s)' % pair for pair in token_specs), 1, 0, []
        for mo in re.finditer(regex, self.source):
            kind, value, column = mo.lastgroup, mo.group(), mo.start() - line_start
            if kind == 'NEWLINE': line_start, line_num = mo.end(), line_num + 1; continue
            if kind in ['SKIP', 'COMENTARIO']: continue
            if kind == 'MISMATCH': print(f"ERRO LÉXICO: Caractere inesperado '{value}' na linha {line_num}"); continue
            if kind == 'ID' and value in reserverdWords: t_class, t_type = value, value
            elif kind == 'ID':
                t_class, t_type = 'id', 'NULL'
                symbolsTable.insert(Token(t_class, value, t_type, line_num, column))
            elif kind == 'LITERAL': t_class, t_type = 'lit', 'lit'
            elif kind == 'NUM': t_class, t_type = 'num', 'real' if '.' in value else 'inteiro'
            else: t_class, t_type = kind.lower(), kind.lower()
            tokens.append(Token(t_class, value, t_type, line_num, column))
        tokens.append(Token("$", "$", "$", line_num, 0))
        return tokens

    def scan(self):
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]; self.pos += 1; return token
        return self.tokens[-1]