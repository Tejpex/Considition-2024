import http.client
import json
import random
import pprint
import os
from dotenv import load_dotenv

game_url = "api.considition.com"
api_key = "d6b11135-fd26-4526-86f3-e445466c9616"
map_file = "../Map-Gothenburg.json"  # Change map here
latest_score = 0

breakpoint_environment = 50
low_breakpoint_capital_difference = 0.2
high_breakpoint_capital_difference = 0.6
high_rate = 0.5
low_rate = 0.055
rate_increase = 0.08
rate_decrease = 0.29
award_number_good = 1500
award_number_bad = 800

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
    if customer_obj["personality"] == "Conservative" or customer_obj["personality"] == "Innovative":
        new_rate -= rate_decrease
    return new_rate


with open(map_file, "r") as file:
    map_obj = json.load(file)

for _ in range(5):
    game_input = {
        "MapName": map_obj["name"],
        "Proposals": [],
        "Iterations": []
    }

    for customer in map_obj["customers"]:
        game_input["Proposals"].append({
            "CustomerName": customer["name"],
            "MonthsToPayBackLoan": map_obj["gameLengthInMonths"],
            "YearlyInterestRate": calculate_rate(customer)
        })

    award_types = ["IkeaFoodCoupon", "IkeaDeliveryCheck", "IkeaCheck",
                   "GiftCard", "HalfInterestRate", "NoInterestRate"]
    action_types = ["Skip", "Award"]

    for month in range(map_obj["gameLengthInMonths"]):
        customer_actions_dict = {}
        for customer in map_obj['customers']:
            random_action_type = action_types[random.randint(0, len(action_types) - 1)]
            random_award = "None" if random_action_type == "Skip" else random.choice(award_types)
            customer_actions_dict[customer["name"]] = {
                "Type": random_action_type,
                "Award": random_award
            }
        game_input["Iterations"].append(customer_actions_dict)

    # Preview game-input
    # pprint.pprint(game_input["Proposals"])

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

scores = []
for response in responses:
    scores.append(response["score"]["totalScore"])
responses = []

average_score = sum(scores) / len(scores)
print(average_score)
