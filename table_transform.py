import csv

def table_transform():
	"""
	This function reads a CSV file containing a parsing table and transforms it into two dictionaries:
	ACTION and GOTO. Each dictionary contains the parsing actions and state transitions for a given grammar.
	The function returns these two dictionaries.
	"""
	with open("tableslr(1).csv", newline='', encoding='utf-8') as csvfile:
		reader = csv.reader(csvfile)
		rows = list(reader)

	ACTION_HEADERS = rows[1][1:25]   # action start at col 1, end at col 24
	GOTO_HEADERS   = rows[1][25:43]  # goto start at col 25, end at col 42

	# fill each array (length = 76) with empty strings
	ACTION = {h: [""] * 76 for h in ACTION_HEADERS}
	GOTO   = {h: [""] * 76 for h in GOTO_HEADERS}

	for row in rows[2:]:
		state = int(row[0])
		# fill ACTION cols
		for i, h in enumerate(ACTION_HEADERS):
			col = 1 + i
			ACTION[h][state] = row[col]
		# fill GOTO cols
		offset = 1 + len(ACTION_HEADERS) # the GOTO table starts at col 25...
		for j, h in enumerate(GOTO_HEADERS):
			col = offset + j
			GOTO[h][state] = row[col]

	return ACTION, GOTO