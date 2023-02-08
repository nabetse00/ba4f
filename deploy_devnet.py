import base64
import os
from datetime import datetime
from time import sleep
from typing import Any

from algosdk import account, constants, encoding, mnemonic, transaction
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    TransactionWithSigner,
)
from algosdk.transaction import wait_for_confirmation
from algosdk.v2client import algod, indexer
from beaker import client, sandbox
from dotenv import load_dotenv
from progress.spinner import Spinner

from smart_contracts.bet import Bet

load_dotenv("./smart_contracts/.env")

algod_address = os.getenv("ALGOD_SERVER_TESTNET")
algod_token = os.getenv("ALGOD_TOKEN_TESTNET")
headers = {
    "X-API-Key": algod_token,
}

indexer_address = os.getenv("INDEXER_SERVER_TESNET")
indexer_token = os.getenv("INDEXER_TOKEN_TESTNET")
headers = {
    "X-API-Key": indexer_token,
}

# clients for test net
algod_client = algod.AlgodClient(algod_token, algod_address, headers)
algoidx_client = indexer.IndexerClient(indexer_token, indexer_address, headers)

mnemonics = [
    os.getenv("MNEMONIC1"),
    os.getenv("MNEMONIC2"),
    os.getenv("MNEMONIC3"),
    os.getenv("MNEMONIC4"),
    os.getenv("MNEMONIC4"),
]
addrs: list[str] = [
    str(os.getenv("ADDR1")),
    str(os.getenv("ADDR2")),
    str(os.getenv("ADDR3")),
    str(os.getenv("ADDR4")),
    str(os.getenv("ADDR5")),
]

print("")

creator = sandbox.SandboxAccount(  # type: ignore
    addrs[0],
    mnemonic.to_private_key(mnemonics[0]),
    AccountTransactionSigner(mnemonic.to_private_key(mnemonics[0])),
)
acct1 = sandbox.SandboxAccount(  # type: ignore
    addrs[1],
    mnemonic.to_private_key(mnemonics[1]),
    AccountTransactionSigner(mnemonic.to_private_key(mnemonics[1])),
)
acct2 = sandbox.SandboxAccount(  # type: ignore
    addrs[2],
    mnemonic.to_private_key(mnemonics[2]),
    AccountTransactionSigner(mnemonic.to_private_key(mnemonics[2])),
)
acct3 = sandbox.SandboxAccount(  # type: ignore
    addrs[3],
    mnemonic.to_private_key(mnemonics[3]),
    AccountTransactionSigner(mnemonic.to_private_key(mnemonics[3])),
)


def check_accounts_balances(val: int):
    for addr in addrs:
        bal = algod_client.account_info(addr)["amount"]
        if bal < val:
            raise Exception(
                f"not enought funds for {addr} / {bal} uAlgo,"
                f"should be at least {val} uAlgo"
                f"use {os.getenv('ALGO_TESTNET_DIPENSER')} testnet dispenser"
            )
        print(f"addrs: {addr} bal: {bal} uAlgo")


check_accounts_balances(10_000_000)

# if already deployed => change APP_ID
APP_ID = 0
# create an app client
app_client = client.ApplicationClient(  # type: ignore
    client=algod_client,
    app=Bet(),
    signer=creator.signer,  # type: ignore
    suggested_params=algod_client.suggested_params(),
    app_id=APP_ID,
)
# deploy the app on-chain
if APP_ID == 0:
    app_creation = app_client.create()
    APP_ID = app_client.app_addr
    # call the method start method
    result = app_client.call(
        Bet.start_bet,
        description="test bet for match team A vs team B",
        results=["1", "X", "2"],
        bet_lenght=120,
        oracle=creator.address,
    )
    wait_for_confirmation(algod_client, result.tx_id, 10)
    print(f"====> call start bet: ** {result.return_value} **")

print(
    f"App created [{acct1.address}] with app id "
    + f"{app_client.app_id} and addr [{app_client.app_addr}]"
)


def create_extra_account() -> sandbox.SandboxAccount:  # type: ignore
    private_key, address = account.generate_account()
    acct = sandbox.SandboxAccount(  # type: ignore
        address, private_key, AccountTransactionSigner(private_key)
    )  # type: ignore
    print(f"===> new account [{acct.address}]")
    return acct


def get_addr_balance(addr: str) -> int:
    return algod_client.account_info(addr)["amount"]


def send_payment(
    sender: sandbox.SandboxAccount, reciever: str, amount: int  # type: ignore
) -> None:
    bal = get_addr_balance(reciever)
    print(f"[send payment] original bal is {bal}")
    # call the method place bet method
    params = algod_client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    # params.flat_fee = True
    # params.fee = constants.MIN_TXN_FEE
    receiver = reciever
    note = f"Pay {amount} to {receiver}"  # .encode()
    amount = amount
    unsigned_txn = transaction.PaymentTxn(
        sender.address, params, receiver, amount, None, note
    )
    signed_txn = unsigned_txn.sign(sender.private_key)
    pay_txn_id = algod_client.send_transaction(signed_txn)
    wait_for_confirmation(algod_client, pay_txn_id, 10)
    bal = get_addr_balance(reciever)
    print(f"[send payment] new bal is {bal}")
    return


# acct3 = create_extra_account()
# send_payment(creator, acct3.address, 10_000_000)


def make_tws(
    account: sandbox.SandboxAccount, amount: int  # type: ignore
) -> TransactionWithSigner:
    params = algod_client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    # params.flat_fee = True
    # params.fee = constants.MIN_TXN_FEE
    receiver = app_client.app_addr
    note = f"payment to {app_client.app_id} for {amount}"  # .encode()
    amount = amount
    unsigned_txn = transaction.PaymentTxn(
        account.address, params, receiver, amount, None, note
    )
    signer = AccountTransactionSigner(account.private_key)
    tws = TransactionWithSigner(unsigned_txn, signer)
    return tws


def place_bet(
    account: sandbox.SandboxAccount, amount: int, bet_result: int  # type: ignore
) -> Any:  # # noqa: ANN401
    result = app_client.call(
        Bet.place_bet,
        payment=make_tws(account, amount),
        result=bet_result,
        boxes=[
            [
                app_client.app_id,
                encoding.decode_address(account.address),
            ],  # type: ignore
        ],
        signer=account.signer,
        suggested_params=algod_client.suggested_params(),
    )
    wait_for_confirmation(algod_client, result.tx_id, 10)
    print(
        f"[place bet from {account.address}"
        f"for {amount} and result {bet_result} ] ==> {result.return_value}"
    )
    return result.return_value


## increase bet
def increment_bet(
    account: sandbox.SandboxAccount, amount: int  # type: ignore
) -> Any:  # # noqa: ANN401
    # call the method place bet method
    params = algod_client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = constants.MIN_TXN_FEE
    receiver = app_client.app_addr
    note = f"increment bet value with {amount} uAlgo"  # .encode()
    amount = amount
    unsigned_txn = transaction.PaymentTxn(
        account.address, params, receiver, amount, None, note
    )
    signer = AccountTransactionSigner(account.private_key)
    tws = TransactionWithSigner(unsigned_txn, signer)
    result = app_client.call(
        Bet.increase_bet,
        payment=tws,
        boxes=[
            [
                app_client.app_id,
                encoding.decode_address(account.address),  # type: ignore
            ]
        ],
        signer=account.signer,
    )
    wait_for_confirmation(algod_client, result.tx_id, 10)
    print(f"Increment bet for {account.address} ==> {result.return_value}")


# get total bets
def get_bet(account: sandbox.SandboxAccount):  # type: ignore
    result = app_client.call(
        Bet.get_bet,
        boxes=[
            [
                app_client.app_id,
                encoding.decode_address(account.address),
            ],  # type: ignore
        ],  # type: ignore
        signer=account.signer,
    )
    wait_for_confirmation(algod_client, result.tx_id, 10)
    print(f"acct[{account.address}] bet  ==> {result.return_value}")


def get_bettors_count() -> int:
    b_c = app_client.get_application_state()["bettors_count"]
    print(f"App[{app_client.app_id}] bettors count ==> {b_c}")
    return int(b_c)


def get_timestamp(blck: int) -> int:
    response = algoidx_client.block_info(block=blck)
    return response["timestamp"]


def get_bet_end() -> int:
    # 'bet_end'
    b_e = int(app_client.get_application_state()["bet_end"])
    print(f"App[{app_client.app_id} bet ends at {datetime.fromtimestamp(b_e)} [{b_e}]")
    return b_e


def wait_for_bet_end():
    spinner = Spinner("Waiting blck: ")
    # spinner.start()
    start_round = algod_client.status()["last-round"]
    current_round = start_round
    b_e = get_bet_end()
    t_s = get_timestamp(current_round)

    while t_s <= b_e:
        for _ in range(0, 10):
            spinner.next()
            sleep(1)
        current_round = algod_client.status()["last-round"]
        t_s = get_timestamp(current_round)
        print(f" blck {current_round} {datetime.fromtimestamp(t_s)}: {t_s} / {b_e}")
    spinner.finish()
    # print(f"App[{app_client.app_id}] => bet ended !")


def claim_bet(account: sandbox.SandboxAccount):  # type: ignore
    print("===== claim bet ===")
    wait_for_bet_end()
    bettors_before = int(app_client.get_application_state()["bettors_count"])
    total_beted = app_client.get_application_state()["total_amount"]
    print(f"total beted ==>  {total_beted}")
    bal_before = algod_client.account_info(account.address)["amount"]
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = constants.MIN_TXN_FEE * 2  # should pay inner txn
    result = app_client.call(
        Bet.claim_bet,
        boxes=[
            [
                app_client.app_id,
                encoding.decode_address(account.address),  # type: ignore
            ]
        ],
        signer=account.signer,
        suggested_params=params,
    )
    wait_for_confirmation(algod_client, result.tx_id, 10)
    print(f"[{account.address}] claim result ==> {result.return_value}")
    bal_new = algod_client.account_info(account.address)["amount"]
    print(f"effective earnings {bal_new - bal_before}")
    expected = result.return_value[1]
    txn_fee = expected - (bal_new - bal_before)
    bettors_after = int(app_client.get_application_state()["bettors_count"])
    print(f"txn fee check {txn_fee}")
    print(f"Removed {bettors_before - bettors_after}")
    print("===== end claim bet ===")


def set_bet_result(oracle: sandbox.SandboxAccount, bet_result: int):  # type: ignore
    print("===== set bet result  ===")
    wait_for_bet_end()
    result = app_client.call(
        Bet.set_bet_result,
        result=bet_result,
        signer=oracle.signer,
        suggested_params=algod_client.suggested_params(),
    )
    print(f"Bet result set to {result.return_value} from oracle {oracle.address}")
    print("===== end set bet result  ===")


def get_boxes() -> list[tuple[int, bytes]]:
    boxes: list[dict[str, str]] = algoidx_client.application_boxes(app_client.app_id)[
        "boxes"
    ]
    boxes_array: list[tuple[int, bytes]] = []
    for b_ in boxes:
        box: tuple[int, bytes] = (app_client.app_id, base64.b64decode(b_["name"]))
        boxes_array.append(box)
    return boxes_array


def delete_loosing_bets(
    account: sandbox.SandboxAccount,  # type: ignore
):  # type: ignore
    boxes = get_boxes()
    addrs = []
    for e in boxes:
        addrs.append(encoding.encode_address(e[1]))
    result = app_client.call(
        Bet.remove_loosing_bets,
        bettors=addrs,
        signer=account.signer,
        suggested_params=algod_client.suggested_params(),
        boxes=boxes,
    )
    print(f"Deleted {result.return_value} records from {account.address}")


def delete_app():
    bet_fee = 100_000  # 0.1 Algo fee
    num_bets = 3
    txn_fee = constants.MIN_TXN_FEE * 2
    benef = bet_fee * num_bets - txn_fee
    bal_before = algod_client.account_info(creator.address)["amount"]
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = txn_fee
    app_client.delete(
        sender=creator.address,
        signer=creator.signer,
        suggested_params=params,
    )
    bal_after = algod_client.account_info(creator.address)["amount"]
    real_benef = bal_after - bal_before
    diff = real_benef - benef
    print(f" benefit: {real_benef} should be {benef} diff {diff}")


def get_array_with_prefix(prefix: str) -> dict[int, str]:
    state = app_client.get_application_state()
    keys = state.keys()
    dict_from_prefix: dict[int, str] = {}
    for k in keys:
        if prefix in str(k):
            index_b = bytes(str(k).replace(prefix, ""), "utf-8")
            index = int.from_bytes(index_b, "big")
            dict_from_prefix[index] = str(state[k])
    return dict(sorted(dict_from_prefix.items()))


def get_result_descriptions() -> dict[int, str]:
    dict_desc = get_array_with_prefix("results_desc")
    print(f"Result descriptions {dict_desc}")
    return dict_desc


def get_result_amounts() -> dict[int, str]:
    dict_amounts = get_array_with_prefix("results_amount")
    print(f"Result amounts {dict_amounts}")
    return dict_amounts


def show_earnings():
    result = app_client.call(
        Bet.get_earnings,
        signer=creator.signer,
        # suggested_params=params,
    )
    print(f"Earning result ==> {result.return_value}")


# bet for acct1 1 Algo
place_bet(acct1, 1_000_000, 1)

# should fail
try:
    place_bet(acct1, 1_000_0000, 1)
except Exception:  #noqa
    print("second bet failed its ok !")

# bet for acct2 10 Algo
place_bet(acct2, 1_000_000, 2)

# bet for acct3 7 Algo
place_bet(acct3, 700_000, 1)

# increment bet by 10 algos
increment_bet(acct1, 1_000_000)

get_bet(acct1)
get_bet(acct2)
get_bet(acct3)

print("=== get bet status ====")
print(f"Description: {app_client.get_application_state()['bet_description']}")
get_result_descriptions()
get_result_amounts()
print("=== end bet status ====")

show_earnings()

try:
    set_bet_result(acct1, 1)
except:  # noqa Exception as e:
    print(f"Account {acct1.address} cannot set result.")
    print("===== end claim bet ===")

try:
    set_bet_result(acct2, 2)
except:  # noqa Exception as e:
    print(f"Account {acct2.address} cannot set result.")
    print("===== end claim bet ===")

try:
    set_bet_result(creator, 5)
except:  # noqa Exception as e:
    print(f"Account {creator.address} cannot set result to invalid number.")
    print("===== end claim bet ===")

set_bet_result(creator, 1)  # this is ok !

try:
    set_bet_result(creator, 2)
except:  # noqa Exception as e:
    print(f"Account {creator.address} cannot reset result to anything.")
    print("===== end claim bet ===")

claim_bet(acct1)
claim_bet(acct3)


print(
    f"after claims bettors count {app_client.get_application_state()['bettors_count'] }"
)

print(f"{algoidx_client.application_boxes(app_client.app_id)}")


result = app_client.call(
    Bet.get_earnings,
    signer=creator.signer,
    suggested_params=algod_client.suggested_params(),
)
wait_for_confirmation(algod_client, result.tx_id, 10)
print(f"===> get earnings result: ** {result.return_value} **")

delete_loosing_bets(creator)

print(f"after delete {algoidx_client.application_boxes(app_client.app_id)}")

print(
    f"after delete bettors count {app_client.get_application_state()['bettors_count'] }"
)

delete_app()
