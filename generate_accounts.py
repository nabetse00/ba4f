
from algosdk import account, mnemonic
from algosdk.v2client import algod, indexer

algod_address = "https://testnet-algorand.api.purestake.io/ps22"
algod_token = "your_purestake_api_key"
headers = {
    "X-API-Key": algod_token,
}

indexer_address = "https://testnet-algorand.api.purestake.io/idx2"
indexer_token = algod_token
headers = {
    "X-API-Key": indexer_token,
}

# clients
algod_client = algod.AlgodClient(algod_token, algod_address, headers)
algoidx_client = indexer.IndexerClient(
    indexer_token, indexer_address, headers)


# get the first 3 acct in the sandbox
def generate_algorand_keypair(index: int):
    private_key, address = account.generate_account()
    print(f"=== account{index} ===")
    print("My address{}: {}".format(index, address))
    print("My private key: {}".format(private_key))
    print("My passphrase: {}".format(mnemonic.from_private_key(private_key)))
    print("========================")

for i in range(0,4):
    generate_algorand_keypair(i)
