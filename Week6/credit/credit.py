from cs50 import get_int

amex_nums = {34, 37}
mastercard_nums = {51, 52, 53, 54, 55}
visa_nums = {4}

card_num = get_int("Number: ")
card_str = str(card_num)
card_sum = 0

for i in range(len(card_str) - 2, -1, -2):
    product = int(card_str[i]) * 2

    # if product is two digits, add both to card_sum
    if int(card_str[i]) > 4:
        card_sum += product // 10**0 % 10
        card_sum += product // 10**1 % 10
    else:
        card_sum += product

for i in range(len(card_str) - 1, -1, -2):
    card_sum += int(card_str[i])

if card_sum % 10 != 0:
    print("INVALID")

elif int(card_str[0:2]) in amex_nums:
    print("AMEX")

elif int(card_str[0:2]) in mastercard_nums:
    print("MASTERCARD")

elif int(card_str[0]) in visa_nums:
    print("VISA")

else:
    print("INVALID")
