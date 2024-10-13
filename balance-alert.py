import requests
import json
import time
from dhooks import Embed, Webhook
from datacrunch import DataCrunchClient
from datacrunch.exceptions import APIException

#DISCORD WEBHOOK
webhook_url = "https://discord.com/api/webhooks/webhook"

#https://console.oblivus.com/dashboard/api/credentials/
oblivus_api_key = "todo"
oblivus_token = "todo"

#https://cloud.datacrunch.io/dashboard/project/cloud-project/keys
datacrunch_client_secret = "todo"
datacrunch_client_id = 'todo'

# Colors
pure_red = "\033[0;31m"
dark_green = "\033[0;32m"
orange = "\033[0;33m"
dark_blue = "\033[0;34m"
bright_purple = "\033[0;35m"
dark_cyan = "\033[0;36m"
dull_white = "\033[0;37m"
pure_black = "\033[0;30m"
bright_red = "\033[0;91m"
light_green = "\033[0;92m"
yellow = "\033[0;93m"
bright_blue = "\033[0;94m"
magenta = "\033[0;95m"
light_cyan = "\033[0;96m"
bright_black = "\033[0;90m"
bright_white = "\033[0;97m"
cyan_back = "\033[0;46m"
purple_back = "\033[0;45m"
white_back = "\033[0;47m"
blue_back = "\033[0;44m"
orange_back = "\033[0;43m"
green_back = "\033[0;42m"
pink_back = "\033[0;41m"
grey_back = "\033[0;40m"
grey = '\033[38;4;236m'
bold = "\033[1m"
underline = "\033[4m"
italic = "\033[3m"
darken = "\033[2m"
invisible = '\033[08m'
reverse_colour = '\033[07m'
reset_colour = '\033[0m'
grey = "\x1b[90m"

#variables
OblivusUnderThreshold = False
DatacrunchUnderThreshold = False

Oblivus_Threshold = 0
Datacrunch_Threshold = 0

discord_webhook = Webhook(webhook_url)
datacrunch = DataCrunchClient(datacrunch_client_id, datacrunch_client_secret)

def send_alert(balance, type):
    if type == "oblivus":
        embed = Embed(
            description=f"Your Oblivus balance is under ${Oblivus_Threshold}!\n**BALANCE: ${balance}**",
            color=0xe74c3c,
            timestamp='now'
        )

    if type == "datacrunch":
        embed = Embed(
            description=f"Your Datacrunch balance is under ${Datacrunch_Threshold}!\n**BALANCE: ${balance}**",
            color=0xe74c3c,
            timestamp='now'
        )
    
    discord_webhook.send(embed=embed)

def check_oblivus(balance):
    global OblivusUnderThreshold
    if balance < Oblivus_Threshold and OblivusUnderThreshold != True: #under balance, not been alerted before
        OblivusUnderThreshold = True
        print(bright_red + "OBLIVUS UNDER THRESHOLD, SENDING ALERT!")
        send_alert(balance, "oblivus")
    if balance > Oblivus_Threshold and OblivusUnderThreshold == True: #now back over threshold, free to alert again
        OblivusUnderThreshold = False

def check_datacrunch(balance):
    global DatacrunchUnderThreshold
    if balance < Datacrunch_Threshold and DatacrunchUnderThreshold != True: #under balance, not been alerted before
        DatacrunchUnderThreshold = True
        print(bright_red + "DATACRUNCH UNDER THRESHOLD, SENDING ALERT!")
        send_alert(balance, "datacrunch")
    if balance > Datacrunch_Threshold and DatacrunchUnderThreshold == True: #now back over threshold, free to alert again
        DatacrunchUnderThreshold = False

#pick which services to use
obl = input(reset_colour + "\nTrack Oblivus? (y/n): ")
if obl == "y":
    Oblivus_Threshold = float(input(reset_colour + "$ Threshold to alert under for Oblivus: "))

dc = input(reset_colour + "\nTrack Datacrunch? (y/n): ")
if dc == "y":
    Datacrunch_Threshold = float(input(reset_colour + "$ Threshold to alert under for Datacrunch: "))
    
print("--------------------------------------")
print("3600 = 1 hour\n1800 = 30 minutes\n900 = 15 minutes")
print("")
delay = int(input("Delay (in seconds): "))


while True:
    print(orange + "Checking balances...")

    if obl == "y":
        while True:
            try:
                response = requests.get(f'https://api.oblivus.com/account/user/?apiKey={oblivus_api_key}&apiToken={oblivus_token}')
                if response.status_code == 200:
                    oblivus_response = float(json.loads(response.text)["data"]["balance"])
                    print(dark_green + f"OBLIVUS: ${oblivus_response}")
                    check_oblivus(oblivus_response)
                    break
                else:
                    print(f"Error: Received oblivus response code {response.status_code}")
                    time.sleep(10)

            except requests.exceptions.RequestException as e:
                print(f"An error occurred getting oblivus: {e}")
                time.sleep(10)

    if dc == "y":
        while True:
            try:
                datacrunch_balance = datacrunch.balance.get().amount
                print(dark_green + f"DATACRUNCH: ${datacrunch_balance}")
                check_datacrunch(datacrunch_balance)
                break
            except APIException as exception:
                print(f"An error occurred getting datacrunch: {exception}")
                time.sleep(10)

    print(orange + f"Sleeping {delay/60} minutes")
    time.sleep(delay)