import { request } from "https"
import { readFileSync } from "fs"

const gameUrl = "api.considition.com"
const apiKey = "d6b11135-fd26-4526-86f3-e445466c9616"
const mapFile = "Map-Gothenburg.json"

var obj = JSON.parse(readFileSync(mapFile, "utf8"))

const gameInput = {
  MapName: "Gothenburg",
  Proposals: [],
  Iterations: [],
}

for (let customer of obj.customers) {
  gameInput.Proposals.push({
      CustomerName: customer.name,
      MonthsToPayBackLoan: obj.gameLengthInMonths,
      YearlyInterestRate: 0.05,
  })
}

const actionTypes = ["Award", "Skip"]
const awardTypes = ["IkeaFoodCoupon", "IkeaDeliveryCheck", "IkeaCheck", "GiftCard", "HalfInterestRate", "NoInterestRate"]

for (let i = 0; i < obj.gameLengthInMonths; i++) {
    const customerActionsDict = {};
    for (let customer of obj.customers) {
        const randomIndex = Math.floor(Math.random() * actionTypes.length);
        const randomType = actionTypes[randomIndex];
        const randomAward = randomType === "Skip" ? "None" : awardTypes[Math.floor(Math.random() * awardTypes.length)];
        customerActionsDict[customer.name] = {
            Type: randomType,
            Award: randomAward,
        };
    }

    gameInput.Iterations.push(customerActionsDict);
}

// Uncomment this to preview game
// console.log(JSON.stringify(gameInput, null, 2));
// gameInput.iterations.forEach((element) => {
//     console.log(element);
// });

const options = {
    hostname: gameUrl,
    path: "/game",
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
    },
};

const req = request(options, (res) => {
    let body = "";
    res.on("data", (chunk) => {
        body += chunk;
    });

    res.on("end", () => {
        if (res.statusCode === 200) {
            console.log(JSON.parse(body, null, 2));
        } else {
            console.error(`Error: ${res.statusCode} - ${body}`);
        }
    });
});

req.write(JSON.stringify(gameInput));
req.end();
