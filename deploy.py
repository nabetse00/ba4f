from algosdk import constants, encoding, mnemonic, transaction
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    TransactionWithSigner,
)
from beaker import client, sandbox

from smart_contracts.bet import Bet

# get the first acct in the sandbox
accts = sandbox.get_accounts()  # type: ignore
acct = accts[0]
acct2 = accts[1]  # type: ignore
print(f"======================================> {acct2.address} {acct.address}")
print(mnemonic.from_private_key(acct.private_key))

algod_client = sandbox.get_algod_client()  # type: ignore

# create an app client
app_client = client.ApplicationClient(  # type: ignore
    client=algod_client, app=Bet(), signer=acct.signer  # type: ignore
)
# deploy the app on-chain
app_client.create()
print(
    f"App created [{acct.address}] with app id "
    + f"{app_client.app_id} and addr [{app_client.app_addr}]"
)

# call the method start method
result = app_client.call(
    Bet.start_bet,
    description="test bet",
    results=["a", "b", "c"],
    bet_lenght=10000,
    oracle=acct.address,
)
print(f"====> create bet {result.return_value}")  # 42

# call the method place bet method
params = algod_client.suggested_params()
# comment out the next two (2) lines to use suggested fees
params.flat_fee = True
params.fee = constants.MIN_TXN_FEE
receiver = app_client.app_addr
note = "Hello World"  # .encode()
amount = 1000000000
unsigned_txn = transaction.PaymentTxn(
    acct.address, params, receiver, amount, None, note
)

signed_txn = unsigned_txn.sign(acct.private_key)
signer = AccountTransactionSigner(acct.private_key)
tws = TransactionWithSigner(unsigned_txn, signer)


result = app_client.call(
    Bet.place_bet,
    payment=tws,
    result=1,
    boxes=[[app_client.app_id, encoding.decode_address(acct.address)]],  # type: ignore
)

print(f"first bet ==> {result.return_value}")  # 42

# call the method place bet method
params = algod_client.suggested_params()
# comment out the next two (2) lines to use suggested fees
params.flat_fee = True
params.fee = constants.MIN_TXN_FEE
receiver = app_client.app_addr
note = "Hello World"  # .encode()
amount = 1000000000
unsigned_txn = transaction.PaymentTxn(
    acct.address, params, receiver, amount, None, note
)

signed_txn = unsigned_txn.sign(acct.private_key)
signer = AccountTransactionSigner(acct.private_key)
tws = TransactionWithSigner(unsigned_txn, signer)
try:
    result = app_client.call(
        Bet.place_bet,
        payment=tws,
        result=1,
        boxes=[
            [app_client.app_id, encoding.decode_address(acct.address)] # type: ignore
        ],  # type: ignore
    )
except Exception as e:
    print(f"second bet failed ==> {e}")  # 42

print("next =====> ")
## increase bet

# call the method place bet method
params = algod_client.suggested_params()
# comment out the next two (2) lines to use suggested fees
params.flat_fee = True
params.fee = constants.MIN_TXN_FEE
receiver = app_client.app_addr
note = "Double bet value"  # .encode()
amount = 1000000000
unsigned_txn = transaction.PaymentTxn(
    acct.address, params, receiver, amount, None, note
)
signed_txn = unsigned_txn.sign(acct.private_key)
signer = AccountTransactionSigner(acct.private_key)
tws = TransactionWithSigner(unsigned_txn, signer)


result = app_client.call(
    Bet.increase_bet,
    payment=tws,
    boxes=[[app_client.app_id, encoding.decode_address(acct.address)]],  # type: ignore
)

print(f"increment bet ==> {result.return_value}")

# call the method place bet method
params = algod_client.suggested_params()
# comment out the next two (2) lines to use suggested fees
params.flat_fee = True
params.fee = constants.MIN_TXN_FEE
receiver = app_client.app_addr
note = "Hello World"  # .encode()
amount = 1000000000
unsigned_txn = transaction.PaymentTxn(
    acct2.address, params, receiver, amount, None, note
)

signed_txn = unsigned_txn.sign(acct2.private_key)
signer = AccountTransactionSigner(acct2.private_key)
tws = TransactionWithSigner(unsigned_txn, signer)

print(f"{acct2.address}")

result = app_client.call(
    Bet.place_bet,
    payment=tws,
    result=1,
    boxes=[[app_client.app_id, encoding.decode_address(acct2.address)]],  # type: ignore
    signer=acct2.signer,
)

print(f"new bettor bet ==> {result.return_value}")

# get total bets

result = app_client.call(
    Bet.get_bet,
    boxes=[
        [app_client.app_id, encoding.decode_address(acct.address)], # type: ignore
    ],  # type: ignore
)

print(f"acct bet  ==> {result.return_value}")  # 42

result = app_client.call(
    Bet.get_bet,
    boxes=[
        [app_client.app_id, encoding.decode_address(acct2.address)],],  # type: ignore
    signer=acct2.signer,
)

print(f"acct 2 bet  ==> {result.return_value}")  # 42

print(f"global vars ==>  {app_client.get_application_state()}")

for i in range(0,3):
    bk = b"results_amount\x00\x00\x00\x00\x00\x00\x00" + i.to_bytes()
    bl = bytearray(bk)
    stringlist=[chr(x) for x in bl]
    print(f"===> result {i} total amount is:")
    print(app_client.get_application_state()["".join(stringlist)])

for i in range(0,3):
    bk = b"results_desc\x00\x00\x00\x00\x00\x00\x00" + i.to_bytes()
    bl = bytearray(bk)
    stringlist=[chr(x) for x in bl]
    print(f"===> result {i} description is:")
    print(app_client.get_application_state()["".join(stringlist)])
