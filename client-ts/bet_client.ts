import algosdk from "algosdk";
import * as bkr from "beaker-ts";
export class Bet extends bkr.ApplicationClient {
    desc: string = "";
    override methods: algosdk.ABIMethod[] = [
        new algosdk.ABIMethod({ name: "start_bet", desc: "", args: [{ type: "string", name: "description", desc: "" }, { type: "string[]", name: "results", desc: "" }, { type: "uint64", name: "bet_lenght", desc: "" }, { type: "address", name: "oracle", desc: "" }], returns: { type: "void", desc: "" } }),
        new algosdk.ABIMethod({ name: "set_bet_result", desc: "", args: [{ type: "uint64", name: "result", desc: "" }], returns: { type: "uint64", desc: "" } }),
        new algosdk.ABIMethod({ name: "place_bet", desc: "", args: [{ type: "pay", name: "payment", desc: "" }, { type: "uint64", name: "result", desc: "" }], returns: { type: "(uint64,uint64)", desc: "" } }),
        new algosdk.ABIMethod({ name: "increase_bet", desc: "", args: [{ type: "pay", name: "payment", desc: "" }], returns: { type: "(uint64,uint64)", desc: "" } }),
        new algosdk.ABIMethod({ name: "get_earnings", desc: "", args: [], returns: { type: "uint64", desc: "" } }),
        new algosdk.ABIMethod({ name: "claim_bet", desc: "", args: [], returns: { type: "(uint64,uint64)", desc: "" } }),
        new algosdk.ABIMethod({ name: "get_bet", desc: "", args: [], returns: { type: "(uint64,uint64)", desc: "" } }),
        new algosdk.ABIMethod({ name: "remove_loosing_bets", desc: "", args: [{ type: "address[]", name: "bettors", desc: "" }], returns: { type: "uint64", desc: "" } })
    ];
    async start_bet(args: {
        description: string;
        results: string[];
        bet_lenght: bigint;
        oracle: string;
    }, txnParams?: bkr.TransactionOverrides): Promise<bkr.ABIResult<void>> {
        const result = await this.execute(await this.compose.start_bet({ description: args.description, results: args.results, bet_lenght: args.bet_lenght, oracle: args.oracle }, txnParams));
        return new bkr.ABIResult<void>(result);
    }
    async set_bet_result(args: {
        result: bigint;
    }, txnParams?: bkr.TransactionOverrides): Promise<bkr.ABIResult<bigint>> {
        const result = await this.execute(await this.compose.set_bet_result({ result: args.result }, txnParams));
        return new bkr.ABIResult<bigint>(result, result.returnValue as bigint);
    }
    async place_bet(args: {
        payment: algosdk.TransactionWithSigner | algosdk.Transaction;
        result: bigint;
    }, txnParams?: bkr.TransactionOverrides): Promise<bkr.ABIResult<[
        bigint,
        bigint
    ]>> {
        const result = await this.execute(await this.compose.place_bet({ payment: args.payment, result: args.result }, txnParams));
        return new bkr.ABIResult<[
            bigint,
            bigint
        ]>(result, result.returnValue as [
            bigint,
            bigint
        ]);
    }
    async increase_bet(args: {
        payment: algosdk.TransactionWithSigner | algosdk.Transaction;
    }, txnParams?: bkr.TransactionOverrides): Promise<bkr.ABIResult<[
        bigint,
        bigint
    ]>> {
        const result = await this.execute(await this.compose.increase_bet({ payment: args.payment }, txnParams));
        return new bkr.ABIResult<[
            bigint,
            bigint
        ]>(result, result.returnValue as [
            bigint,
            bigint
        ]);
    }
    async get_earnings(txnParams?: bkr.TransactionOverrides): Promise<bkr.ABIResult<bigint>> {
        const result = await this.execute(await this.compose.get_earnings(txnParams));
        return new bkr.ABIResult<bigint>(result, result.returnValue as bigint);
    }
    async claim_bet(txnParams?: bkr.TransactionOverrides): Promise<bkr.ABIResult<[
        bigint,
        bigint
    ]>> {
        const result = await this.execute(await this.compose.claim_bet(txnParams));
        return new bkr.ABIResult<[
            bigint,
            bigint
        ]>(result, result.returnValue as [
            bigint,
            bigint
        ]);
    }
    async get_bet(txnParams?: bkr.TransactionOverrides): Promise<bkr.ABIResult<[
        bigint,
        bigint
    ]>> {
        const result = await this.execute(await this.compose.get_bet(txnParams));
        return new bkr.ABIResult<[
            bigint,
            bigint
        ]>(result, result.returnValue as [
            bigint,
            bigint
        ]);
    }
    async remove_loosing_bets(args: {
        bettors: string[];
    }, txnParams?: bkr.TransactionOverrides): Promise<bkr.ABIResult<bigint>> {
        const result = await this.execute(await this.compose.remove_loosing_bets({ bettors: args.bettors }, txnParams));
        return new bkr.ABIResult<bigint>(result, result.returnValue as bigint);
    }
    compose = {
        start_bet: async (args: {
            description: string;
            results: string[];
            bet_lenght: bigint;
            oracle: string;
        }, txnParams?: bkr.TransactionOverrides, atc?: algosdk.AtomicTransactionComposer): Promise<algosdk.AtomicTransactionComposer> => {
            return this.addMethodCall(algosdk.getMethodByName(this.methods, "start_bet"), { description: args.description, results: args.results, bet_lenght: args.bet_lenght, oracle: args.oracle }, txnParams, atc);
        },
        set_bet_result: async (args: {
            result: bigint;
        }, txnParams?: bkr.TransactionOverrides, atc?: algosdk.AtomicTransactionComposer): Promise<algosdk.AtomicTransactionComposer> => {
            return this.addMethodCall(algosdk.getMethodByName(this.methods, "set_bet_result"), { result: args.result }, txnParams, atc);
        },
        place_bet: async (args: {
            payment: algosdk.TransactionWithSigner | algosdk.Transaction;
            result: bigint;
        }, txnParams?: bkr.TransactionOverrides, atc?: algosdk.AtomicTransactionComposer): Promise<algosdk.AtomicTransactionComposer> => {
            return this.addMethodCall(algosdk.getMethodByName(this.methods, "place_bet"), { payment: args.payment, result: args.result }, txnParams, atc);
        },
        increase_bet: async (args: {
            payment: algosdk.TransactionWithSigner | algosdk.Transaction;
        }, txnParams?: bkr.TransactionOverrides, atc?: algosdk.AtomicTransactionComposer): Promise<algosdk.AtomicTransactionComposer> => {
            return this.addMethodCall(algosdk.getMethodByName(this.methods, "increase_bet"), { payment: args.payment }, txnParams, atc);
        },
        get_earnings: async (txnParams?: bkr.TransactionOverrides, atc?: algosdk.AtomicTransactionComposer): Promise<algosdk.AtomicTransactionComposer> => {
            return this.addMethodCall(algosdk.getMethodByName(this.methods, "get_earnings"), {}, txnParams, atc);
        },
        claim_bet: async (txnParams?: bkr.TransactionOverrides, atc?: algosdk.AtomicTransactionComposer): Promise<algosdk.AtomicTransactionComposer> => {
            return this.addMethodCall(algosdk.getMethodByName(this.methods, "claim_bet"), {}, txnParams, atc);
        },
        get_bet: async (txnParams?: bkr.TransactionOverrides, atc?: algosdk.AtomicTransactionComposer): Promise<algosdk.AtomicTransactionComposer> => {
            return this.addMethodCall(algosdk.getMethodByName(this.methods, "get_bet"), {}, txnParams, atc);
        },
        remove_loosing_bets: async (args: {
            bettors: string[];
        }, txnParams?: bkr.TransactionOverrides, atc?: algosdk.AtomicTransactionComposer): Promise<algosdk.AtomicTransactionComposer> => {
            return this.addMethodCall(algosdk.getMethodByName(this.methods, "remove_loosing_bets"), { bettors: args.bettors }, txnParams, atc);
        }
    };
}
