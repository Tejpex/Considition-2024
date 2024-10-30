import http.client
import json
import random
import pprint

game_url = "api.considition.com"
api_key = "ENTER API KEY HERE" # API-key is sent in mail inbox
map_file = "Map-Gothenburg.json" # Change map here

with open(map_file, "r") as file:
    obj = json.load(file)

game_input = {
    "MapName": "Gothenburg",
    "Proposals": [],
    "Iterations": []
}

for customer in obj["customers"]:
    game_input["Proposals"].append({
        "CustomerName": customer["name"],
        "MonthsToPayBackLoan": obj["gameLengthInMonths"],
        "YearlyInterestRate": 0.05
    })


action_types = ["Award", "Skip"]
award_types = ["IkeaFoodCoupon", "IkeaDeliveryCheck", "IkeaCheck", "GiftCard", "HalfInterestRate", "NoInterestRate"]

for index in range(obj["gameLengthInMonths"]):
  customer_actions_dict = {}
  for customer in obj['customers']:
    random_index = random.randint(0, len(action_types) - 1)
    random_type = action_types[random_index];
    random_award = "None" if random_type == "Skip" else random.choice(award_types)
    customer_actions_dict[customer["name"]] = {
        "Type": random_type,
        "Award": random_award
    }
  game_input["Iterations"].append(customer_actions_dict)


# Uncomment this to preview game
# pprint.pprint(game_input)

conn = http.client.HTTPSConnection(game_url)
headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key
}

conn.request("POST", "/game", json.dumps(game_input), headers)
response = conn.getresponse()
body = response.read().decode()

if response.status == 200:
    pprint.pprint(json.loads(body))
else:
    print(f"Error: {response.status} - {body}")

conn.close()