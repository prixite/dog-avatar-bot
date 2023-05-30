import json

with open("output.txt", "r") as file:
    data_string = file.read()

# Define your lists
first_list = [
    "hex",
    "bitcoin",
    "ethereum",
    "tether",
    "bnb",
    "usdcoin",
    "xrp",
    "cardano",
    "dogecoin",
    "solana",
    "polygon",
]
second_list = [
    "HEX",
    "BTC",
    "ETH",
    "USDT",
    "BNB",
    "USDC",
    "XRP",
    "ADA",
    "DOGE",
    "SOL",
    "MATIC",
]

# Get user input
user_string = input("Enter your string: ").lower()


index = 99
# Check each word in the user string
for word in user_string.split():
    if word in first_list:
        # If the word is in the first list, add its index to the new list

        index = first_list.index(word)

if index != 99:
    # Print the indices
    curreny_symbol = second_list[index]
    # Parse the JSON string into a Python dictionary
    data = json.loads(data_string)

    # Extract the Bitcoin data
    bitcoin_data = data["data"][curreny_symbol]

    print(bitcoin_data)
else:
    print("I don't Know please enter currency name correctly")
