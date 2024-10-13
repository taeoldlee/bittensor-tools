import argparse
import bittensor as bt
import time
import logging
from dhooks import Webhook, Embed

def load_wallets(file_path):
    wallets = {}

    with open(file_path, 'r') as file:
        for line in file:
            # Skip lines starting with '##'
            if line.startswith('##'):
                continue

            if line.startswith('**'):
                webhook = line.strip().replace("** DISCORD WEBHOOK: ","")
                wallets["webhook"] = webhook
                continue

            if ',' not in line:
                continue

            # Split the line into hot key and subnet ID
            wallet_name, hot_key, subnet_id = line.strip().split(',')
            subnet_id = int(subnet_id)

            # Add the hot key to the dictionary
            if subnet_id in wallets:
                wallets[subnet_id].append([wallet_name,hot_key])
            else:
                wallets[subnet_id] = [[wallet_name, hot_key]]

    return wallets

def remove_wallet_entry(file_path, subnet_id, hot_key, wallet_name):
    with open(file_path, "r") as file:
        lines = file.readlines()

    with open(file_path, "w") as file:
        for line in lines:
            if line.strip() != f"{wallet_name},{hot_key},{subnet_id}":
                file.write(line)

def dereg_webhook(message, webhook):
    dereg = Embed(
    description=message,
    color=0xe74c3c,
    timestamp='now'
    )

    Webhook(webhook).send(embed=dereg)

def get_subnet_config():
    try:
        parser = argparse.ArgumentParser()
        bt.subtensor.add_args(parser)
        config = bt.config(parser)
        subtensor = bt.subtensor(config=config)
        return subtensor
    except Exception as e:
        logging.error(f"Error in getting subnet config for subnet {subnet_id}: {e}")
        return None

#load wallets
wallets_dict = load_wallets('wallets.txt')

#load webhook
try:
    discord_webhook = wallets_dict["webhook"]
    print(f"Loaded webhook: {discord_webhook}")
except Exception as e:
    print("ERROR DETECTED WITH WEBHOOK!!!!!")
    quit

#print wallets
print()
print("Successfully loaded wallets:")
print()
for subnet_id, miners in wallets_dict.items(): #iterate through, print nicely.
    if subnet_id == "webhook":
        continue
    print(f"Subnet ID: {subnet_id}")
    for miner in miners:
        print(f"  Name: {miner[0]}")
        print(f"    Hot Key: {miner[1]}")
    print()

print()

subnet_config = get_subnet_config() #connect to network

while True:
    wallets_dict = load_wallets('wallets.txt')

    for subnet_id, miners in wallets_dict.items():

        if subnet_id == "webhook":
            continue

        metagraph = subnet_config.metagraph(subnet_id)

        subnet_hotkeys = metagraph.hotkeys

        for miner in miners:
            if miner[1] in subnet_hotkeys:
                print("\033[92m==SAFE==")
                print(f"\033[92mName: {miner[0]}")
                print(f"\033[92m  Subnet ID: {subnet_id}")
                print(f"\033[92m    Hot Key: {miner[1]}")

            else: #deregitered
                print("\033[93m==DEREGISTRATION FOUND==")
                print(f"\033[93mName: {miner[0]}")
                print(f"\033[93m  Subnet ID: {subnet_id}")
                print(f"\033[93m    Hot Key: {miner[1]}")

                dereg_webhook(f"**DEREG FOUND :(**\nName: {miner[0]}\nSubnet ID: {subnet_id}\nHot Key: [**{miner[1]}**](https://taostats.io/hotkey/?hkey={miner[1]}#netuid_{subnet_id})", discord_webhook)

                remove_wallet_entry('wallets.txt', subnet_id, miner[1], miner[0]) #remove from text fild
                

    
    print("===========Done, sleeping 30 minutes...===========")
    time.sleep(1800)

            