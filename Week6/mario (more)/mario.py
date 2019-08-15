while True:
    s = input("Height: ")
    try:
        if int(s) >= 1 and int(s) <= 8:
            n = int(s)
            break
    except ValueError:
        continue

for i in range(1, n + 1):
    print(f"{' ' * (n - i)}{'#' * i}  {'#' * i}")
