import argparse
import bittensor as bt
import time
import logging
from dhooks import Webhook, Embed
from dotenv import load_dotenv
load_dotenv()

# input data here for eacch subnet to monitor
webhook_data = {
    #key: 
        #int: subnet id (1-45)
    
    #values:
        #url: discord webhook
        #mention: discord role id if you would like to alert users when the registration price changes
        
    #ex
    1: {
        "url": "https://discord.com/api/webhooks/webhook",
        "mention": "<@&discord_role>"
    },
}

# logging
logging.basicConfig(filename='bittensor_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# discord webhooks
def fee_webhook(message, webhook, role):
    feeEmbed = Embed(
    description=message,
    color=0x95a5a6,
    timestamp='now'
    )

    Webhook(webhook).send(role, embed=feeEmbed)



def registration_webhook(message, webhook):
    regEmbed = Embed(
    description=message,
    color=0xe74c3c,
    timestamp='now'
    )

    Webhook(webhook).send(embed=regEmbed)

#bt tooling
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

def get_registration_fee(subnet_config, subnet_id):
    try:
        register_cost = subnet_config.burn(subnet_id).tao
        return register_cost
    except Exception as e:
        logging.error(f"Error in getting registration fee for subnet {subnet_id}: {e}")
        return None
    
def check_new_wallets(old_wallets, new_wallets, subnet_id, webhook_info):
    new_added_wallets = set(new_wallets) - set(old_wallets)
    if new_added_wallets:
        logging.info(f"New wallets detected in subnet {subnet_id}: {new_added_wallets}")
        for wallet in new_added_wallets:
            wallet_message = f"New wallet registered: [**{wallet}**](https://taostats.io/hotkey/?hkey={wallet}#netuid_{subnet_id})"
            registration_webhook(wallet_message, webhook_info["url"])
    else:
        logging.info(f"No new wallets detected in subnet {subnet_id}")

def monitor_subnets(subnet_ids, previous_fees, previous_wallets, subnet_config, webhook_data):
    for subnet_id in subnet_ids:
        if not subnet_config:
            logging.warning(f"Failed to get subnet configuration for subnet {subnet_id}")
            return

        # Check registration fees
        current_fee = get_registration_fee(subnet_config, subnet_id)
        if current_fee is not None and current_fee != previous_fees[subnet_id]:
            if previous_fees[subnet_id] is not None:  # not the initial run
                message = f"New Registration Fee for sn**{subnet_id}**: {current_fee}**τ**"
                webhook_info = webhook_data.get(subnet_id)
                logging.info(message)
                fee_webhook(message, webhook_info["url"], webhook_info['mention'])
            previous_fees[subnet_id] = current_fee

        # Check new wallets
        try:
            metagraph = subnet_config.metagraph(subnet_id)
            new_wallets = metagraph.hotkeys
            if previous_wallets[subnet_id] and new_wallets != previous_wallets[subnet_id]:
                check_new_wallets(previous_wallets[subnet_id], new_wallets, subnet_id, webhook_data.get(subnet_id))
            previous_wallets[subnet_id] = new_wallets
        except Exception as e:
            logging.error(f"Error fetching metagraph data for subnet {subnet_id}: {e}")

##### Main Function #####

if __name__ == "__main__":
    # subnets to monitor
    subnet_ids = list(webhook_data.keys())
    previous_fees = {subnet_id: None for subnet_id in subnet_ids}
    previous_wallets = {subnet_id: [] for subnet_id in subnet_ids}

    # fetch the initial subnet config
    subnet_config = get_subnet_config()

    while True:
        monitor_subnets(subnet_ids, previous_fees, previous_wallets, subnet_config, webhook_data)
        if not subnet_config:  # Retry fetching subnet config if needed
            subnet_config = get_subnet_config()
        
        time.sleep(60)