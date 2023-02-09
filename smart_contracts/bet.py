from typing import Final

from beaker.application import Application
from beaker.decorators import Authorize, create, delete, external, internal
from beaker.lib.storage.mapping import Mapping
from beaker.state import (
    ApplicationStateValue,
    ReservedApplicationStateValue,
    prefix_key_gen,
)
from pyteal import (
    AppParam,
    Approve,
    Assert,
    Balance,
    Bytes,
    Expr,
    For,
    Global,
    If,
    InnerTxnBuilder,
    Int,
    Itob,
    Not,
    Pop,
    ScratchVar,
    Seq,
    TealType,
    Txn,
    TxnField,
    TxnType,
)
from pyteal.ast import abi

# APP_CREATOR ADDRESS
APP_CREATOR = Seq(creator := AppParam.creator(Int(0)), creator.value())

# Bettors record Box format
class BettorRecord(abi.NamedTuple):
    result: abi.Field[abi.Uint64]
    amount: abi.Field[abi.Uint64]


"""
Bet Contract
"""


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

    # bettors count incremented when a bet is placed, d
    # decrement when claime or deleted lossing bets
    bettors_count: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64,
        default=Int(0),
        descr="bettor count",
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
        stack_type=TealType.uint64, default=Int(0), descr="bet end timestamp"
    )

    bet_description: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.bytes,
        default=Bytes(""),
        descr="Bet Description ie match A vs B - YYYY/MM/DD HH:MM",
    )

    # Min bet amount to cover MBR cost
    _bettor_record_box_size = abi.size_of(BettorRecord)
    _bettor_record_key_box_size = abi.size_of(abi.Address)
    BoxFlatMinBalance = 2500
    BoxByteMinBalance = 400
    _flat_fee = 100000  # Creator fee 0.1 algo per bet
    _min_balance_per_box = (
        BoxFlatMinBalance
        + (_bettor_record_box_size + _bettor_record_key_box_size) * BoxByteMinBalance
    )
    min_bet_amount: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64,
        static=True,
        default=Int(_min_balance_per_box + _flat_fee),
        descr="min bet must cover box creation MDB + fee",
    )

    # bet possible results with a desciption
    # for example [ "1", "X", "2" ] or
    # [ "player 1 wins", "player 2 wins", "player 3 wins", "draw", ... ]
    bet_possible_results: Final[
        ReservedApplicationStateValue
    ] = ReservedApplicationStateValue(
        stack_type=TealType.bytes,
        max_keys=8,
        key_gen=prefix_key_gen("results_desc"),
        descr="App state variable storing possible results, with 8 possible keys",
    )

    # Stores total amount betted useful for bet claim amount
    # computation
    results_amounts: Final[
        ReservedApplicationStateValue
    ] = ReservedApplicationStateValue(
        stack_type=TealType.uint64,
        max_keys=8,
        key_gen=prefix_key_gen("results_amount"),
        descr=
        "App state variable storing bet results total amount, with 8 possible keys",
    )

    # Total amount betted
    total_amount: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64,
        default=Int(0),
        descr="total amount betted",
    )

    # earnings for app creator from flat_fee
    total_earnings: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64,
        default=Int(0),
        descr="total collected fees",
    )

    # Boxes
    bettor_records = Mapping(
        abi.Address,
        BettorRecord,
    )

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
                Seq(
                    results[i.load()].use(
                        lambda value: self.bet_possible_results[Itob(i.load())].set(
                            value.get()
                        )
                    ),
                    self.results_amounts[Itob(i.load())].set(Int(0)),
                )
            ),
            self.latest_bettor_account.set(Global.zero_address()),
            self.bettors_count.set(Int(0)),
            self.total_amount.set(Int(0)),
        )

    @external(authorize=Authorize.only(oracle_account))
    def set_bet_result(self, result: abi.Uint64, *, output: abi.Uint64) -> Expr:
        return Seq(
            Assert(
                Global.latest_timestamp() > self.bet_end,
                comment="bet must be closed before setting the result",
            ),
            Assert(
                self.result == Int(0),
                comment="Result must be 0 ie TBD - avoids reentry",
            ),
            Assert(
                self.bet_possible_results[Itob(result.get())].exists(),
                comment="Result should be in possible results array",
            ),
            self.result.set(result.get() + Int(1)),
            output.set(self.result.get() - Int(1)),
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
                Txn.sender() != APP_CREATOR, comment="App creator account cannot bet"
            ),
            Assert(
                Txn.sender() != Global.current_application_address(),
                comment="App cannot bet !",
            ),
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
                self.bet_possible_results[Itob(result.get())].exists(),
                comment="Ressult must be in possible results",
            ),
            Assert(
                amount.get() > self.min_bet_amount,
                comment="bet amount must cover box creation MBR + flat_fee",
            ),
            Assert(
                Global.latest_timestamp() < self.bet_end,
                comment="bet windows must be open",
            ),
            Assert(
                Not(self.bettor_records[payment.get().sender()].exists()),
                comment="Cannot re bet with place_bet function! use increase_bet",
            ),
            amount.set(amount.get() - Int(self._flat_fee)),
            output.set(result, amount),
            self.bettor_records[payment.get().sender()].set(output),
            self.latest_bettor_account.set(Txn.sender()),
            self.results_amounts[result].increment(amount.get()),
            self.total_earnings.increment(Int(self._flat_fee)),
            self.total_amount.increment(amount.get()),
            self.bettors_count.increment(),
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
            # Assert(payment.get().amount() > self.min_bet_amount),
            Assert(
                Global.latest_timestamp() < self.bet_end,
                comment="bet window must be open",
            ),
            Assert(
                self.bettor_records[payment.get().sender()].exists(),
                comment="bettor must have place a initial bet",
            ),
            self.bettor_records[payment.get().sender()].store_into(output),
            output.result.store_into(result),
            output.amount.store_into(old_amount),
            (amount := abi.Uint64()).set(payment.get().amount() + old_amount.get()),
            output.set(result, amount),
            self.bettor_records[payment.get().sender()].set(output),
            self.results_amounts[result].set(
                self.results_amounts[result].get() + payment.get().amount()
            ),
            self.total_amount.increment(payment.get().amount()),
        )

    @internal(TealType.none)
    def pay(self, receiver: Expr, amount: Expr) -> Expr:
        return InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: receiver,
                TxnField.amount: amount,
                TxnField.fee: Int(0),
            }
        )

    @external(authorize=Authorize.only(APP_CREATOR))
    def get_earnings(self, *, output: abi.Uint64) -> Expr:
        return Seq(
            Assert(
                self.total_earnings <= Balance(Global.current_application_address()),
                comment="teoric amount should be equal to balance",
            ),
            output.set(self.total_earnings.get()),
        )

    """
    Claim bet
    Minimal fee = MIN_TXN_FEE * 2 
    """

    @external
    def claim_bet(self, *, output: BettorRecord) -> Expr:
        result = abi.Uint64()
        amount = abi.Uint64()
        a_t_pay = abi.Uint64()
        return Seq(
            Assert(
                Global.latest_timestamp() > self.bet_end,
                comment="bet must have ended",
            ),
            Assert(
                self.bettor_records[Txn.sender()].exists(),
                comment="record should exist",
            ),
            Assert(self.result.get() > Int(0), comment="result should not be 0"),
            self.bettor_records[Txn.sender()].store_into(output),
            output.result.store_into(result),
            If(
                result.get() == self.result.get() - Int(1),
                Seq(  # then compute amount, pay txn, and remove box
                    output.amount.store_into(amount),
                    a_t_pay.set(
                        amount.get()
                        * self.total_amount.get()
                        / self.results_amounts[result].get()
                    ),
                    Assert(
                        a_t_pay.get() < Balance(Global.current_application_address()),
                        comment="App balance must be greater to send ammount",
                    ),
                    # Log(Itob(a_t_pay.get())),
                    Pop(self.bettor_records[Txn.sender()].delete()),
                    self.pay(Txn.sender(), a_t_pay.get()),
                    output.set(result, a_t_pay),
                    self.bettors_count.decrement(),
                ),
                Seq(  # else no payment just remove box ...
                    amount.set(0),
                    output.set(result, amount),
                    Pop(self.bettor_records[Txn.sender()].delete()),
                    self.bettors_count.decrement(),
                ),
            ),
        )

    @external
    def get_bet(self, *, output: BettorRecord) -> Expr:
        return Seq(
            self.bettor_records[Txn.sender()].store_into(output),
        )

    """
    Deletes all loosing bets boxes
    """

    @external
    def remove_loosing_bets(
        self, bettors: abi.DynamicArray[abi.Address], *, output: abi.Uint64
    ) -> Expr:
        i = ScratchVar(TealType.uint64)
        addr = abi.Address()
        br = BettorRecord()  # type: ignore
        result = abi.Uint64()
        return Seq(
            Assert(
                Global.latest_timestamp() > self.bet_end,
                comment="bet must have ended",
            ),
            Assert(self.result != Int(0), comment="Bet result should be resolved"),
            output.set(0),
            For(
                i.store(Int(0)),
                i.load() < bettors.length(),
                i.store(i.load() + Int(1)),
            ).Do(
                bettors[i.load()].store_into(addr),
                Assert(
                    self.bettor_records[addr.get()].exists(),
                    comment="Bettor record should exist",
                ),
                self.bettor_records[addr.get()].store_into(br),
                br.result.store_into(result),
                If(
                    result.get() != (self.result - Int(1)),
                    Seq(
                        Pop(self.bettor_records[addr.get()].delete()),
                        self.bettors_count.decrement(),
                        output.set(output.get() + Int(1)),
                    ),
                ),
            ),
        )

    @internal(TealType.none)
    def pay_creator(
        self,
    ) -> Expr:
        return InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.Payment,
                TxnField.fee: Int(0),
                TxnField.receiver: APP_CREATOR,
                TxnField.amount: Int(0),
                TxnField.close_remainder_to: APP_CREATOR,
            }
        )

    # Delete app
    # Send MBR funds to creator and delete app
    @delete
    def delete(self) -> Expr:
        return Seq(
            Assert(
                self.bettors_count == Int(0),
                comment="Remaining bettors data close them before",
            ),
            self.pay_creator(),
            Approve(),
        )
