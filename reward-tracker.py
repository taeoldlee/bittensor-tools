import requests
import time

API_URL = "https://beta-api.taostats.io/api/v1/delegate?account_id={PUTTAOADDRESSHERE}"

def fetch_delegation_events(wallet_address, headers):
    url = API_URL.replace("{PUTTAOADDRESSHERE}", wallet_address)
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print(f"Error fetching delegation events for {wallet_address}: {response.status_code}")
        return []

def calculate_net_rewards(events):
    net_rewards_by_delegate = {}

    for event in events:
        delegate_address = event.get('delegate_address', {}).get('ss58')
        amount = int(event.get('amount', 0)) / 1e9  # Convert RAO to TAO
        action = event.get('action')

        if delegate_address not in net_rewards_by_delegate:
            net_rewards_by_delegate[delegate_address] = 0

        # net rewards calculated here
        if action == "UNDELEGATE":
            net_rewards_by_delegate[delegate_address] += amount  # undelegate -> unstake -> you get rewards
        elif action == "DELEGATE":
            net_rewards_by_delegate[delegate_address] -= amount  # delegate -> should cancel out with your undelegate so subtract from rewards

    return net_rewards_by_delegate

def process_wallets_from_file(file_path, headers):
    total_net_positive_rewards = 0
    total_net_negative_rewards = 0
    
    try:
        with open(file_path, 'r') as file:
            wallet_addresses = file.readlines()

        for wallet_address in wallet_addresses:
            wallet_address = wallet_address.strip()
            if wallet_address:
                print(f"\nProcessing wallet: {wallet_address}")
                
                delegation_events = fetch_delegation_events(wallet_address, headers)

                net_rewards = calculate_net_rewards(delegation_events)

                print(f"Net staking/unstaking rewards by delegate (hotkey) for wallet {wallet_address}:")
                if net_rewards:
                    for delegate, net_amount in net_rewards.items():
                        print(f"Delegate: {delegate}, Net Reward Balance: {net_amount:.6f} τ")
                        if net_amount > 0:
                            total_net_positive_rewards += net_amount
                        elif net_amount < 0:
                            total_net_negative_rewards += net_amount
                else:
                    print(f"No delegation events found for {wallet_address}.")

                # TODO: RATE LIMIT: change this to whatever API allows at time of running
                time.sleep(4)

        print(f"\nTotal Net Reward Balance (excluding negative balances): {total_net_positive_rewards:.6f} τ")
        print(f"Total Negative Reward Balance (read note in code): {total_net_negative_rewards:.6f} τ")
        # NOTE: There may be negative balance due to coldkey swaps done. This issue will hopefully be fixed in coming updates to the API. 

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    api_key = input("Please enter your API key: ").strip()
    
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }

    option = input("Do you want to enter a single wallet address or provide a path to a file with coldkeys? (enter 'single' or 'file'): ").strip()

    if option == "single":
        wallet_address = input("Enter the TAO wallet address: ").strip()
        
        delegation_events = fetch_delegation_events(wallet_address, headers)

        net_rewards = calculate_net_rewards(delegation_events)

        print(f"\nNet staking/unstaking rewards by delegate (hotkey) for wallet {wallet_address}:")
        total_net_positive_rewards = 0
        total_net_negative_rewards = 0
        if net_rewards:
            for delegate, net_amount in net_rewards.items():
                print(f"Delegate: {delegate}, Net Reward Balance: {net_amount:.6f} τ")
                if net_amount > 0:
                    total_net_positive_rewards += net_amount
                elif net_amount < 0:
                    total_net_negative_rewards += net_amount

            print(f"\nTotal Net Reward Balance (excluding negative balances): {total_net_positive_rewards:.6f} τ")
            print(f"Total Negative Reward Balance: {total_net_negative_rewards:.6f} τ")
        else:
            print("No delegation events found.")

    elif option == "file":
        file_path = input("Enter the path to the .txt file containing wallet addresses: ").strip()
        process_wallets_from_file(file_path, headers)
    else:
        print("Invalid option. Please enter 1 for single wallet or 2 for multiple wallets.")

if __name__ == "__main__":
    main()
