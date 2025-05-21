from scanner import scanner

with open("model.txt", "r") as f:
    while True:
        token = scanner(f)
        print(token)
        if token.t_name == "$":
            break