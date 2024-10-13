import os
from datacrunch import DataCrunchClient, exceptions
import random
from random import randint
import time
from dhooks import Webhook, Embed
from datetime import datetime
from pytz import timezone
tz = timezone('EST')

#A100
A100 = '1A100.22V'
A100x2 = '2A100.44V'
A100x4 = '4A100.88V'
A100x8 = '8A100.176V'

#A6000
A6000 = '1A6000.10V'
A6000x2 = '2A6000.20V'
A6000x4 = '4A6000.40V'
A6000x8 = '8A6000.80V'

#ADA6000
ADA6000 = '1RTX6000ADA.10V'
ADA6000x2 = '2RTX6000ADA.20V'
ADA6000x4 = '4RTX6000ADA.40V'
ADA6000x8 = '8RTX6000ADA.80V'

# info -- grab at https://cloud.datacrunch.io/dashboard/account-settings => "REST API CREDENTIALS"
CLIENT_SECRET = "todo"
CLIENT_ID = "todo"

#webhook to send success to
webhook = Webhook('https://discord.com/api/webhooks/webhook')

#gpu to snipe, refer to above codes
gpu_code = A6000

#delay (seconds) between fails
delay = 30




datacrunch = DataCrunchClient(CLIENT_ID, CLIENT_SECRET)

ssh_keys = datacrunch.ssh_keys.get()
ssh_keys_ids = list(map(lambda ssh_key: ssh_key.id, ssh_keys))

def success(code):
    embed = Embed(
        description=f"**instance deployed!**\ncode: {code}",
        color=0x95a5a6,
        timestamp='now'
        )
    
    webhook.send(embed=embed)


while True:
    try:
        instance = datacrunch.instances.create(instance_type=gpu_code,
                                                image='ubuntu-22.04-cuda-12.0',
                                                ssh_key_ids=ssh_keys_ids,
                                                hostname='user',
                                                description=f'sniped{random.random()}'
                                                )
        #successfully deployed
        success(gpu_code) 
        print(gpu_code + ' deployed! || ' + datetime.now(tz))
        break
    except exceptions.APIException as e: #oos
        if "Not enough resources" in str(e):
            print(f"{gpu_code} out of stock, retrying in {delay} seconds. || {datetime.now(tz) }")
            time.sleep(delay + randint(1,3))
        else:
            print(f"possible rate limit, retrying in {delay} seconds. || {datetime.now(tz) }")
            time.sleep(delay + randint(1,3))