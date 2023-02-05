from typing import Final, Literal

from beaker.application import Application
from beaker.decorators import Authorize, create, delete, external, internal
from beaker.lib.storage.mapping import Mapping
from beaker.state import (
    ApplicationStateValue,
    ReservedApplicationStateValue,
    identity_key_gen,
    prefix_key_gen,
)
from pyteal import (
    # App,
    AppParam,
    Approve,
    Assert,
    Btoi,
    Bytes,
    Expr,
    For,
    Global,
    If,
    Int,
    Itob,
    Not,
    ScratchVar,
    Seq,
    TealType,
    Txn,
    While,
)
from pyteal.ast import abi

APP_CREATOR = Seq(creator := AppParam.creator(Int(0)), creator.value())

# Bettors record Box
class BettorRecord(abi.NamedTuple):
    result: abi.Field[abi.Uint64]
    amount: abi.Field[abi.Uint64]


class Bet(Application):

    ## Global State variables

    # oracle account address
    oracle_account: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.bytes,
        default=Bytes(""),
        descr="oracle account to set end result",
    )

    # latest bettor account address
    latest_bettor_account: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.bytes,
        default=Bytes(""),
        descr="latest bettor account",
    )

    # - Bet Result encoded as 0 => TBD, 1 => result 0,
    #   2 => result 1 , 3 => result 2, ...
    result: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64, default=Int(0)
    )

    # - Bet End: The timestamp when the betting ends,
    # should be ~5min before match kickoff
    # to avoid bettor advantage over timestamp from blockchain
    bet_end: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64, default=Int(0)
    )

    bet_description: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.bytes,
        default=Bytes(""),
        descr="Bet Description ie match A vs B - YYYY/MM/DD HH:MM",
    )

    # - Min bet amount to cover MBR cost
    _member_box_size = abi.size_of(BettorRecord)
    BoxFlatMinBalance = 2500
    BoxByteMinBalance = 400
    _min_balance = BoxFlatMinBalance + (_member_box_size * BoxByteMinBalance)
    min_bet_amount: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64, static=True, default=Int(_min_balance)
    )

    # results
    bet_possible_results: Final[
        ReservedApplicationStateValue
    ] = ReservedApplicationStateValue(
        stack_type=TealType.bytes,
        max_keys=8,
        key_gen=prefix_key_gen("results_desc"),
        descr="App state variable storing possible results, with 8 possible keys",
    )

    results_amounts: Final[
        ReservedApplicationStateValue
    ] = ReservedApplicationStateValue(
        stack_type=TealType.uint64,
        max_keys=8,
        key_gen=prefix_key_gen("results_amount"),
        descr="App state variable storing bet results total amount, with 8 possible keys",
    )

    # Boxes
    bettor_records = Mapping(abi.Address, BettorRecord,)

    ####

    @create
    def create(self) -> Expr:
        return Seq(
            self.initialize_application_state(),
        )

    @external(authorize=Authorize.only(APP_CREATOR))
    def start_bet(
        self,
        description: abi.String,
        results: abi.DynamicArray[abi.String],
        bet_lenght: abi.Uint64,
        oracle: abi.Address,
    ) -> Expr:
        i = ScratchVar(TealType.uint64)
        return Seq(
            Assert(self.bet_end.get() == Int(0), comment="bet length not 0"),
            Assert(
                description.get() != Bytes(""), comment="description cannot be empty"
            ),
            Assert(bet_lenght.get() > Int(0), comment="bet lenght must be > 0"),
            Assert(
                results.length() < Int(9),
                comment="posssible results length must be less than 8",
            ),
            Assert(
                oracle.get() != Global.zero_address(),
                comment="oracle cannot be 0 address",
            ),
            self.bet_end.set(bet_lenght.get() + Global.latest_timestamp()),
            self.bet_description.set(description.get()),
            self.oracle_account.set(oracle.get()),
            For(
                i.store(Int(0)),
                i.load() < results.length(),
                i.store(i.load() + Int(1)),
            ).Do(
                results[i.load()].use(
                    lambda value: self.bet_possible_results[Itob(i.load())].set(
                        value.get()
                    )
                )
            ),
            For(
                i.store(Int(0)),
                i.load() < results.length(),
                i.store(i.load() + Int(1)),
            ).Do(
                self.results_amounts[Itob(i.load())].set(Int(0)),
            ),
            self.latest_bettor_account.set(Global.zero_address()),
        )

    @external
    def place_bet(
        self,
        payment: abi.PaymentTransaction,
        result: abi.Uint64,
        *,
        output: BettorRecord,
    ) -> Expr:

        return Seq(
            Assert(
                Txn.sender() == payment.get().sender(),
                comment="Txn Sender must be the payment sender",
            ),
            Assert(
                payment.get().receiver() == Global.current_application_address(),
                comment="Payment receiver must be this app address",
            ),
            (amount := abi.Uint64()).set(payment.get().amount()),
            Assert(
                result.get() > Int(0),
                comment="result cannot be 0 [non ended bet]",
            ),
            Assert(
                amount.get() > self.min_bet_amount,
                comment="bet amount must cover box creation MBR",
            ),
            Assert(
                Global.latest_timestamp() < self.bet_end,
                comment="bet windows must be open",
            ),
            Assert(
                Not(self.bettor_records[payment.get().sender()].exists()),
                comment="Cannot re bet with place_bet function! use increase_bet",
            ),
            output.set(result, amount),
            self.bettor_records[payment.get().sender()].set(output),
            self.latest_bettor_account.set(Txn.sender()),
            self.results_amounts[result].set(
                self.results_amounts[result].get() + amount.get()
            ),
        )

    @external
    def increase_bet(
        self,
        payment: abi.PaymentTransaction,
        *,
        output: BettorRecord,
    ) -> Expr:
        old_amount = abi.Uint64()
        result = abi.Uint64()
        return Seq(
            Assert(Txn.sender() == payment.get().sender()),
            Assert(payment.get().receiver() == Global.current_application_address()),
            Assert(payment.get().amount() > self.min_bet_amount),
            Assert(Global.latest_timestamp() < self.bet_end),
            Assert(self.bettor_records[payment.get().sender()].exists()),
            self.bettor_records[payment.get().sender()].store_into(output),
            output.result.store_into(result),
            output.amount.store_into(old_amount),
            (amount := abi.Uint64()).set(payment.get().amount() + old_amount.get()),
            output.set(result, amount),
            self.bettor_records[payment.get().sender()].set(output),
             self.results_amounts[result].set(
                self.results_amounts[result].get() + payment.get().amount())
        )

    @external
    def get_bet(self, *, output: BettorRecord) -> Expr:
        return Seq(
            self.bettor_records[Txn.sender()].store_into(output),
        )

    @delete(authorize=Authorize.only(Global.creator_address()))
    def delete(self) -> Expr:
        return Approve()
