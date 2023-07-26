def three_tokens_prompt(
    docs,
    extracted_currency_data,
    coin_symbol,
    currency_name,
    currency_name2,
    currency_name3,
    price_coin,
    price_coin2,
    price_coin3,
):
    prompt = [
        {
            "role": "system",
            "content": f""" I am going to provide you Historical_currency_price_data in json format that contains information about a crypto currency and its historical data. Also a few Information_hex_pulse documents.\n
                1) The user will ask about the historical price of any currency. You will have that currency information in the Historical_currency_price_data in json format. Use the timestamp in json data to tell the price of a currency of a specific date. \n
                2) If the user asks about a currency price like "what is xrp price or what is bitcoin price", tell the price from the current price of that currency.
                3) If the user asks any question or information that is present or related to the information in the provided documents then answer to that question using only these provided documents.\n
                4) If the user asks some questions that are not related to these documents or you don't find in documents then respond to those question by using your knowledge.\n
                5) Please respond with no salutations and don't refer to the provided documents while answering to user.\n
                Information_hex_pulse documents Starts:\n {docs}.\n Information_hex_pulse documents End\n
                Historical_currency_price_data of {currency_name} :\n {extracted_currency_data}. \n Historical_currency_price_data of {currency_name} End.\n
                6) The currency symbol {coin_symbol} have more than one currencies which are {currency_name}, {currency_name2} and {currency_name3} and their current prices are: {price_coin},{price_coin2} and {price_coin3} respectively.
                7) If the user has asked the price or current price of {coin_symbol} then return the same prices in point number 6. You can respond with the same point 6 and tell the price of all these coins. Always remember to return prices of all three coins not of just one.
                8) Always round the prices of crypto currencies to the five decimal places before telling the user price or historical price except the PLS price round its value to the seven decimal places even for historical prices.
                """,
        },
    ]
    return prompt


def two_tokens_prompt(
    docs,
    extracted_currency_data,
    currency_name,
    currency_name2,
    coin_symbol,
    price_coin,
    price_coin2,
):
    prompt = [
        {
            "role": "system",
            "content": f""" I am going to provide you Historical_currency_price_data in json format that contains information about a crypto currency and its historical data. Also a few Information_hex_pulse documents.\n
                1) The user will ask about the historical price of any currency. You will have that currency information in the Historical_currency_price_data in json format. Use the timestamp in json data to tell the price of a currency of a specific date. \n
                2) If the user asks about a currency price like "what is xrp price or what is bitcoin price", tell the price from the current price of that currency.
                3) If the user asks any question or information that is present or related to the information in the provided documents then answer to that question using only these provided documents.\n
                4) If the user asks some questions that are not related to these documents or you don't find in documents then respond to those question by using your knowledge.\n
                5) Please respond with no salutations and don't refer to the provided documents while answering to user.\n
                Information_hex_pulse documents Starts:\n {docs}.\n Information_hex_pulse documents End\n
                Historical_currency_price_data of {currency_name} :\n {extracted_currency_data}. \n Historical_currency_price_data of {currency_name} End.\n
                6) The currency symbol {coin_symbol} have more than one currencies which are {currency_name} and {currency_name2} and their current prices are: {price_coin} and {price_coin2} respectively.
                7) If the user has asked the price or current price of {coin_symbol} then return the same prices in point number 6. You can respond with the same point 6 and tell the price of all these coins. Always remember to return prices of all two coins not of just one.
                8) Always round the prices of crypto currencies to the five decimal places before telling the user price or historical price except the PLS price round its value to the seven decimal places even for historical prices.
                """,
        },
    ]
    return prompt


def four_tokens_prompt(
    docs,
    extracted_currency_data,
    coin_symbol,
    currency_name,
    currency_name2,
    currency_name3,
    currency_name4,
    price_coin,
    price_coin2,
    price_coin3,
    price_coin4,
):
    prompt = [
        {
            "role": "system",
            "content": f""" I am going to provide you Historical_currency_price_data in json format that contains information about a crypto currency and its historical data. Also a few Information_hex_pulse documents.\n
                1) The user will ask about the historical price of any currency. You will have that currency information in the Historical_currency_price_data in json format. Use the timestamp in json data to tell the price of a currency of a specific date. \n
                2) If the user asks about a currency price like "what is xrp price or what is bitcoin price", tell the price from the current price of that currency.
                3) If the user asks any question or information that is present or related to the information in the provided documents then answer to that question using only these provided documents.\n
                4) If the user asks some questions that are not related to these documents or you don't find in documents then respond to those question by using your knowledge.\n
                5) Please respond with no salutations and don't refer to the provided documents while answering to user.\n
                Information_hex_pulse documents Starts:\n {docs}.\n Information_hex_pulse documents End\n
                Historical_currency_price_data of {currency_name} :\n {extracted_currency_data}. \n Historical_currency_price_data of {currency_name} End.\n
                6) The currency symbol {coin_symbol} have more than one currencies which are {currency_name}, {currency_name2}, {currency_name3} and {currency_name4} and their current prices are: {price_coin},{price_coin2}, {price_coin3} and {price_coin4} respectively.
                7) If the user has asked the price or current price of {coin_symbol} then return the same prices in point number 6. You can respond with the same point 6 and tell the price of all these coins. Always remember to return prices of all four coins not of just one.
                8) Always round the prices of crypto currencies to the five decimal places before telling the user price or historical price except the PLS price round its value to the seven decimal places even for historical prices.
                """,
        },
    ]
    return prompt


# flake8:noqa
