import http.client
import json
import random
import pprint
import pandas
import time

game_url = "api.considition.com"
api_key = "d6b11135-fd26-4526-86f3-e445466c9616"
map_file = "Map-Gothenburg.json"  # Change map here
latest_score = 0

breakpoint_environment = 50
low_breakpoint_capital_difference = 0.2
high_breakpoint_capital_difference = 0.6
high_rate = 0.5
low_rate = 0.055
rate_increase = 0.08
rate_decrease = 0.015
award_number_good = 1500
award_number_bad = 800
gordons_rate = 0.02
glenns_rate = 0.57
kims_rate = 0.01
responses = []

with open(map_file, "r") as file:
    map_obj = json.load(file)

data_to_save = [[
        "breakpoint_environment",
        "high_rate",
        "low_rate",
        "Glenn",
        "environmentalImpact",
        "happynessScore",
        "totalProfit"
        "totalScore"]]

for _ in range(100):
    time.sleep(0.8)
    for _ in range(5):
        game_input = {
            "MapName": map_obj["name"],
            "Proposals": [],
            "Iterations": []
        }

        for customer in map_obj["customers"]:
            if customer["loan"]["environmentalImpact"] < breakpoint_environment:
                rate = high_rate
            else:
                rate = low_rate
            if customer["capital"] / customer["loan"]["amount"] < low_breakpoint_capital_difference:
                rate += rate_increase
            if customer["capital"] / customer["loan"]["amount"] > high_breakpoint_capital_difference:
                rate -= rate_decrease
            if customer["personality"] == "Conservative" or customer["personality"] == "Innovative":
                rate -= rate_decrease
            if customer["name"] == "Gordon":
                rate = gordons_rate
            if customer["name"] == "Glenn":
                rate = glenns_rate
            if customer["name"] == "Kim":
                rate = kims_rate
            game_input["Proposals"].append({
                "CustomerName": customer["name"],
                "MonthsToPayBackLoan": map_obj["gameLengthInMonths"],
                "YearlyInterestRate": rate
            })

        award_types = ["IkeaFoodCoupon", "IkeaDeliveryCheck", "IkeaCheck",
                       "GiftCard", "HalfInterestRate", "NoInterestRate"]

        for month in range(map_obj["gameLengthInMonths"]):
            customer_actions_dict = {}
            for customer in map_obj['customers']:
                if customer["personality"] == "Conservative" or customer["personality"] == "Practical":
                    action_types = ["Skip"]
                    for i in range(award_number_good):
                        action_types.append("Award")
                else:
                    action_types = ["Skip"]
                    for i in range(award_number_bad):
                        action_types.append("Award")
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
        data_to_save.append([
            breakpoint_environment,
            high_rate,
            low_rate,
            kims_rate,
            response["score"]["environmentalImpact"],
            response["score"]["happynessScore"],
            response["score"]["totalProfit"],
            response["score"]["totalScore"]],
        )
    responses = []

    average_score = sum(scores) / len(scores)
    print(average_score)

    if average_score > latest_score or latest_score - average_score < 1000:
        kims_rate += 0.01
        latest_score = average_score
    elif average_score < latest_score and latest_score - average_score > 1000:
        if kims_rate >= 0.01:
            kims_rate -= 0.01
        latest_score = average_score

csv_data = pandas.DataFrame(data_to_save)
csv_data.to_csv("Data.csv")
