import http.client
import json
import random
import pprint
import os
from dotenv import load_dotenv

load_dotenv()

game_url = "api.considition.com"
api_key = os.getenv("API_KEY")
map_file = "../Map-Almhult.json"  # Change map here

breakpoint_environment = 80000
environment_no = 80000
low_breakpoint_capital_difference = 0.1
high_breakpoint_capital_difference = 0.7
high_rate = 0.8
low_rate = 0.1
rate_increase = 1
rate_decrease = 0.045

low_payback_time = 8
high_payback_time = 12

start_fund = 500000

responses = []


def calculate_rate(customer_obj):
    capital_difference = customer_obj["capital"] / customer_obj["loan"]["amount"]
    if customer_obj["loan"]["environmentalImpact"] < breakpoint_environment:
        new_rate = high_rate
    else:
        new_rate = low_rate
    if capital_difference < low_breakpoint_capital_difference:
        new_rate += rate_increase
    if capital_difference > high_breakpoint_capital_difference:
        new_rate -= rate_decrease
    if customer_obj["personality"] == "Conservative":
        new_rate -= rate_decrease
    return new_rate


def calculate_payback_time(customer_obj):
    if customer_obj["personality"] == "Conservative":
        time = low_payback_time
    else:
        time = high_payback_time
    return time


def approve_customer(customer_obj):
    if (
            customer["loan"]["amount"] > start_fund or
            # customer["capital"] / customer["loan"]["amount"] < low_breakpoint_capital_difference or
            customer_obj["loan"]["environmentalImpact"] < environment_no
            # customer_obj["personality"] == "RiskTaker"
    ):
        return False
    else:
        return True


with open(map_file, "r") as file:
    map_obj = json.load(file)

for _ in range(5):
    game_input = {
        "MapName": map_obj["name"],
        "Proposals": [],
        "Iterations": []
    }

    lent_amount = 0

    for customer in map_obj["customers"]:
        if approve_customer(customer):
            lent_amount += customer["loan"]["amount"]
            game_input["Proposals"].append({
                "CustomerName": customer["name"],
                "MonthsToPayBackLoan": calculate_payback_time(customer),
                "YearlyInterestRate": calculate_rate(customer)
            })

    award_types = ["IkeaFoodCoupon", "IkeaDeliveryCheck", "IkeaCheck",
                   "GiftCard", "HalfInterestRate", "NoInterestRate"]
    action_types = ["Award", "Award", "Award"]

    for month in range(map_obj["gameLengthInMonths"]):
        customer_actions_dict = {}
        for customer in map_obj['customers']:
            if month % 2 == 0:
                random_action_type = action_types[random.randint(0, len(action_types) - 1)]
            else:
                random_action_type = "Skip"
            random_award = "None" if random_action_type == "Skip" else random.choice(award_types)
            if approve_customer(customer):
                customer_actions_dict[customer["name"]] = {
                    "Type": random_action_type,
                    "Award": random_award
                }
        game_input["Iterations"].append(customer_actions_dict)

    # Preview game-input
    # pprint.pprint(game_input["Proposals"])
    # print(lent_amount)

    conn = http.client.HTTPSConnection(game_url)
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    conn.request("POST", "/game", json.dumps(game_input), headers)
    response = conn.getresponse()
    res_body = response.read().decode()

    if response.status == 200:
        pprint.pprint(json.loads(res_body))
        responses.append(json.loads(res_body))
    else:
        print(f"Error: {response.status} - {res_body}")

    conn.close()

scores = [response["score"]["totalScore"] for response in responses]
responses = []

average_score = sum(scores) / len(scores)
print(average_score)
