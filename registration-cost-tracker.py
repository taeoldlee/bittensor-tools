import requests
import json
from time import sleep


def get_coldkeys():
    coldkeys = []
    input_type = input("Do you want to enter a single wallet address or provide a path to a file with coldkeys? (enter 'single' or 'file'): ").strip().lower()

    if input_type == 'single':
        coldkey = input("Please enter the wallet address: ").strip()
        coldkeys.append(coldkey)
    elif input_type == 'file':
        file_path = input("Please enter the path to the file with coldkeys: ").strip()
        try:
            with open(file_path, 'r') as file:
                coldkeys = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print("The specified file was not found.")
            return []
    else:
        print("Invalid input. Please enter either 'single' or 'file'.")
        return []

    return coldkeys


def get_extrinsics(coldkeys, api_key):
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }

    all_extrinsics = {}
    for coldkey in coldkeys:
        page = 1
        count = 200
        all_extrinsics[coldkey] = []
        while count == 200:
            print(f"Getting extrinsics for {coldkey}, current count: {len(all_extrinsics[coldkey])}")
            url = f"https://api.taostats.io/api/v1/extrinsic?signer_address={coldkey}&limit=200&page={page}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                resJson = json.loads(response.text)
                all_extrinsics[coldkey] += resJson['extrinsics']
                count = resJson['count']
                page += 1
            else:
                print(f"Error fetching extrinsics for {coldkey}: {response.status_code}")
                count = 0

            # TODO: RATE LIMIT: change this to whatever API allows at time of running
            sleep(4)

    return all_extrinsics


def filter_extrinsics(extrinsics, api_key, wallet_address):
    all_neuron_registration = []
    count_fail = 0
    count_success = 0

    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }

    for extrinsic in extrinsics:
        success = extrinsic['success']
        block = extrinsic['block_id']
        extrinsicid = extrinsic['id']
        time = extrinsic['timestamp']
        name = extrinsic['full_name']
        temp = {"block": block, "extrinsic": extrinsicid, "time": time, "name": name, "wallet": wallet_address}

        if success:
            if "burned" in name:
                url = f"https://api.taostats.io/api/v1/event?name=Withdraw&extrinsic_id={extrinsicid}"
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    resJson = json.loads(response.text)
                    events = resJson['events']
                    for event in events:
                        if event['name'] == 'Withdraw':
                            recycled_amount = float(event['args']['amount']) / 1e9  # Convert RAO to TAO
                            temp['recycled_amount'] = recycled_amount
                            print(f"Withdraw event found: {recycled_amount} TAO recycled at block {block} from wallet {wallet_address}")
                # TODO: RATE LIMIT: change this to whatever API allows at time of running
                sleep(4)
                all_neuron_registration.append(temp)
            count_success += 1
        else:
            count_fail += 1

    print(f"Successful extrinsics: {count_success}")
    print(f"Failed extrinsics: {count_fail}")

    return all_neuron_registration


def main():
    api_key = input("Please enter your API key: ").strip()
    coldkeys = get_coldkeys()

    if coldkeys:
        all_extrinsics = get_extrinsics(coldkeys, api_key)

        total_recycled_tao = 0
        successful_registrations = 0

        for wallet in coldkeys:
            print(f"\nProcessing wallet: {wallet}")
            extrinsics_for_wallet = all_extrinsics[wallet]
            all_neuron_registration = filter_extrinsics(extrinsics_for_wallet, api_key, wallet)

            print(f"Total neuron registrations for {wallet}: {len(all_neuron_registration)}")

            for reg in all_neuron_registration:
                recycled_amount = reg.get('recycled_amount', 0)
                total_recycled_tao += recycled_amount
                if recycled_amount > 0:
                    successful_registrations += 1
                print(f"Neuron registration at block {reg['block']} recycled {recycled_amount} TAO from wallet {reg['wallet']}.")

        print(f"\nTotal recycled TAO: {total_recycled_tao} TAO")
        print(f"Total successful neuron registrations: {successful_registrations}")


if __name__ == "__main__":
    main()
