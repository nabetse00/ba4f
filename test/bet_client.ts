import algosdk from "algosdk";
import * as bkr from "beaker-ts";
export class BettorRecord {
    result: bigint = BigInt(0);
    amount: bigint = BigInt(0);
    prev_bettor: string = "";
    static codec: algosdk.ABIType = algosdk.ABIType.from("(uint64,uint64,address)");
    static fields: string[] = ["result", "amount", "prev_bettor"];
    static decodeResult(val: algosdk.ABIValue | undefined): BettorRecord {
        return bkr.decodeNamedTuple(val, BettorRecord.fields) as BettorRecord;
    }
    static decodeBytes(val: Uint8Array): BettorRecord {
        return bkr.decodeNamedTuple(BettorRecord.codec.decode(val), BettorRecord.fields) as BettorRecord;
    }
}
export class Bet extends bkr.ApplicationClient {
    desc: string = "";
    override appSchema: bkr.Schema = { declared: { oracle_account: { type: bkr.AVMType.bytes, key: "oracle_account", desc: "", static: false }, latest_bettor_account: { type: bkr.AVMType.bytes, key: "latest_bettor_account", desc: "", static: false }, result: { type: bkr.AVMType.uint64, key: "result", desc: "", static: false }, bet_end: { type: bkr.AVMType.uint64, key: "bet_end", desc: "", static: false }, min_bet_amount: { type: bkr.AVMType.uint64, key: "min_bet_amount", desc: "", static: false } }, reserved: { bet_possible_results: { type: bkr.AVMType.bytes, desc: "", max_keys: 8 } } };
    override acctSchema: bkr.Schema = { declared: {}, reserved: {} };
    override approvalProgram: string = "I3ByYWdtYSB2ZXJzaW9uIDgKaW50Y2Jsb2NrIDAgMSAzMiA4CmJ5dGVjYmxvY2sgMHggMHgxNTFmN2M3NSAweDZjNjE3NDY1NzM3NDVmNjI2NTc0NzQ2ZjcyNWY2MTYzNjM2Zjc1NmU3NCAweDZkNjk2ZTVmNjI2NTc0NWY2MTZkNmY3NTZlNzQgMHg2MjY1NzQ1ZjY1NmU2NAp0eG4gTnVtQXBwQXJncwppbnRjXzAgLy8gMAo9PQpibnogbWFpbl9sMTAKdHhuYSBBcHBsaWNhdGlvbkFyZ3MgMApwdXNoYnl0ZXMgMHgwMjJlZTk4ZSAvLyAicGxhY2VfYmV0KHBheSx1aW50NjQpKHVpbnQ2NCx1aW50NjQsYWRkcmVzcykiCj09CmJueiBtYWluX2w5CnR4bmEgQXBwbGljYXRpb25BcmdzIDAKcHVzaGJ5dGVzIDB4MDFiNjRhOTggLy8gImluY3JlYXNlX2JldChwYXkpKHVpbnQ2NCx1aW50NjQsYWRkcmVzcykiCj09CmJueiBtYWluX2w4CnR4bmEgQXBwbGljYXRpb25BcmdzIDAKcHVzaGJ5dGVzIDB4ZTNhYzgwOWEgLy8gImdldF9iZXQoKSh1aW50NjQsdWludDY0LGFkZHJlc3MpIgo9PQpibnogbWFpbl9sNwp0eG5hIEFwcGxpY2F0aW9uQXJncyAwCnB1c2hieXRlcyAweGI2ZmRhZjcwIC8vICJnZXRfdG90YWxfYmV0cyh1aW50NjQpdWludDY0Igo9PQpibnogbWFpbl9sNgplcnIKbWFpbl9sNjoKdHhuIE9uQ29tcGxldGlvbgppbnRjXzAgLy8gTm9PcAo9PQp0eG4gQXBwbGljYXRpb25JRAppbnRjXzAgLy8gMAohPQomJgphc3NlcnQKdHhuYSBBcHBsaWNhdGlvbkFyZ3MgMQpidG9pCmNhbGxzdWIgZ2V0dG90YWxiZXRzXzYKc3RvcmUgNgpieXRlY18xIC8vIDB4MTUxZjdjNzUKbG9hZCA2Cml0b2IKY29uY2F0CmxvZwppbnRjXzEgLy8gMQpyZXR1cm4KbWFpbl9sNzoKdHhuIE9uQ29tcGxldGlvbgppbnRjXzAgLy8gTm9PcAo9PQp0eG4gQXBwbGljYXRpb25JRAppbnRjXzAgLy8gMAohPQomJgphc3NlcnQKY2FsbHN1YiBnZXRiZXRfNQpzdG9yZSA1CmJ5dGVjXzEgLy8gMHgxNTFmN2M3NQpsb2FkIDUKY29uY2F0CmxvZwppbnRjXzEgLy8gMQpyZXR1cm4KbWFpbl9sODoKdHhuIE9uQ29tcGxldGlvbgppbnRjXzAgLy8gTm9PcAo9PQp0eG4gQXBwbGljYXRpb25JRAppbnRjXzAgLy8gMAohPQomJgphc3NlcnQKdHhuIEdyb3VwSW5kZXgKaW50Y18xIC8vIDEKLQpzdG9yZSAzCmxvYWQgMwpndHhucyBUeXBlRW51bQppbnRjXzEgLy8gcGF5Cj09CmFzc2VydApsb2FkIDMKY2FsbHN1YiBpbmNyZWFzZWJldF80CnN0b3JlIDQKYnl0ZWNfMSAvLyAweDE1MWY3Yzc1CmxvYWQgNApjb25jYXQKbG9nCmludGNfMSAvLyAxCnJldHVybgptYWluX2w5Ogp0eG4gT25Db21wbGV0aW9uCmludGNfMCAvLyBOb09wCj09CnR4biBBcHBsaWNhdGlvbklECmludGNfMCAvLyAwCiE9CiYmCmFzc2VydAp0eG5hIEFwcGxpY2F0aW9uQXJncyAxCmJ0b2kKc3RvcmUgMQp0eG4gR3JvdXBJbmRleAppbnRjXzEgLy8gMQotCnN0b3JlIDAKbG9hZCAwCmd0eG5zIFR5cGVFbnVtCmludGNfMSAvLyBwYXkKPT0KYXNzZXJ0CmxvYWQgMApsb2FkIDEKY2FsbHN1YiBwbGFjZWJldF8zCnN0b3JlIDIKYnl0ZWNfMSAvLyAweDE1MWY3Yzc1CmxvYWQgMgpjb25jYXQKbG9nCmludGNfMSAvLyAxCnJldHVybgptYWluX2wxMDoKdHhuIE9uQ29tcGxldGlvbgppbnRjXzAgLy8gTm9PcAo9PQpibnogbWFpbl9sMTQKdHhuIE9uQ29tcGxldGlvbgpwdXNoaW50IDUgLy8gRGVsZXRlQXBwbGljYXRpb24KPT0KYm56IG1haW5fbDEzCmVycgptYWluX2wxMzoKdHhuIEFwcGxpY2F0aW9uSUQKaW50Y18wIC8vIDAKIT0KYXNzZXJ0CmNhbGxzdWIgZGVsZXRlXzIKaW50Y18xIC8vIDEKcmV0dXJuCm1haW5fbDE0Ogp0eG4gQXBwbGljYXRpb25JRAppbnRjXzAgLy8gMAo9PQphc3NlcnQKY2FsbHN1YiBjcmVhdGVfMAppbnRjXzEgLy8gMQpyZXR1cm4KCi8vIGNyZWF0ZQpjcmVhdGVfMDoKcHJvdG8gMCAwCnB1c2hieXRlcyAweDZmNzI2MTYzNmM2NTVmNjE2MzYzNmY3NTZlNzQgLy8gIm9yYWNsZV9hY2NvdW50IgpieXRlY18wIC8vICIiCmFwcF9nbG9iYWxfcHV0CmJ5dGVjXzIgLy8gImxhdGVzdF9iZXR0b3JfYWNjb3VudCIKYnl0ZWNfMCAvLyAiIgphcHBfZ2xvYmFsX3B1dApwdXNoYnl0ZXMgMHg3MjY1NzM3NTZjNzQgLy8gInJlc3VsdCIKaW50Y18wIC8vIDAKYXBwX2dsb2JhbF9wdXQKYnl0ZWMgNCAvLyAiYmV0X2VuZCIKaW50Y18wIC8vIDAKYXBwX2dsb2JhbF9wdXQKaW50Y18wIC8vIDAKYnl0ZWNfMyAvLyAibWluX2JldF9hbW91bnQiCmFwcF9nbG9iYWxfZ2V0X2V4CnN0b3JlIDgKc3RvcmUgNwpsb2FkIDgKIQphc3NlcnQKYnl0ZWNfMyAvLyAibWluX2JldF9hbW91bnQiCnB1c2hpbnQgMjE3MDAgLy8gMjE3MDAKYXBwX2dsb2JhbF9wdXQKcmV0c3ViCgovLyBhdXRoX29ubHkKYXV0aG9ubHlfMToKcHJvdG8gMSAxCmZyYW1lX2RpZyAtMQpnbG9iYWwgQ3JlYXRvckFkZHJlc3MKPT0KcmV0c3ViCgovLyBkZWxldGUKZGVsZXRlXzI6CnByb3RvIDAgMAp0eG4gU2VuZGVyCmNhbGxzdWIgYXV0aG9ubHlfMQovLyB1bmF1dGhvcml6ZWQKYXNzZXJ0CmludGNfMSAvLyAxCnJldHVybgoKLy8gcGxhY2VfYmV0CnBsYWNlYmV0XzM6CnByb3RvIDIgMQpieXRlY18wIC8vICIiCmludGNfMCAvLyAwCmJ5dGVjXzAgLy8gIiIKaW50Y18wIC8vIDAKZHVwCmJ5dGVjXzAgLy8gIiIKZHVwCmZyYW1lX2RpZyAtMgpndHhucyBTZW5kZXIKdHhuIFNlbmRlcgo9PQphc3NlcnQKZnJhbWVfZGlnIC0yCmd0eG5zIFJlY2VpdmVyCmdsb2JhbCBDdXJyZW50QXBwbGljYXRpb25BZGRyZXNzCj09CmFzc2VydApmcmFtZV9kaWcgLTIKZ3R4bnMgQW1vdW50CmZyYW1lX2J1cnkgMQpmcmFtZV9kaWcgLTEKaW50Y18wIC8vIDAKPgphc3NlcnQKZnJhbWVfZGlnIDEKYnl0ZWNfMyAvLyAibWluX2JldF9hbW91bnQiCmFwcF9nbG9iYWxfZ2V0Cj4KYXNzZXJ0Cmdsb2JhbCBMYXRlc3RUaW1lc3RhbXAKYnl0ZWMgNCAvLyAiYmV0X2VuZCIKYXBwX2dsb2JhbF9nZXQKPAphc3NlcnQKZnJhbWVfZGlnIC0yCmd0eG5zIFNlbmRlcgpib3hfZ2V0CnN0b3JlIDEwCnN0b3JlIDkKbG9hZCAxMAohCmFzc2VydApieXRlY18yIC8vICJsYXRlc3RfYmV0dG9yX2FjY291bnQiCmFwcF9nbG9iYWxfZ2V0CmZyYW1lX2J1cnkgMgpmcmFtZV9kaWcgMgpsZW4KaW50Y18yIC8vIDMyCj09CmFzc2VydApmcmFtZV9kaWcgLTEKaXRvYgpmcmFtZV9kaWcgMQppdG9iCmNvbmNhdApmcmFtZV9kaWcgMgpjb25jYXQKZnJhbWVfYnVyeSAwCmZyYW1lX2RpZyAtMgpndHhucyBTZW5kZXIKYm94X2RlbApwb3AKZnJhbWVfZGlnIC0yCmd0eG5zIFNlbmRlcgpmcmFtZV9kaWcgMApib3hfcHV0CmJ5dGVjXzIgLy8gImxhdGVzdF9iZXR0b3JfYWNjb3VudCIKdHhuIFNlbmRlcgphcHBfZ2xvYmFsX3B1dApyZXRzdWIKCi8vIGluY3JlYXNlX2JldAppbmNyZWFzZWJldF80Ogpwcm90byAxIDEKYnl0ZWNfMCAvLyAiIgppbnRjXzAgLy8gMApkdXAKYnl0ZWNfMCAvLyAiIgppbnRjXzAgLy8gMApkdXBuIDIKYnl0ZWNfMCAvLyAiIgpkdXAKZnJhbWVfZGlnIC0xCmd0eG5zIFNlbmRlcgp0eG4gU2VuZGVyCj09CmFzc2VydApmcmFtZV9kaWcgLTEKZ3R4bnMgUmVjZWl2ZXIKZ2xvYmFsIEN1cnJlbnRBcHBsaWNhdGlvbkFkZHJlc3MKPT0KYXNzZXJ0CmZyYW1lX2RpZyAtMQpndHhucyBBbW91bnQKYnl0ZWNfMyAvLyAibWluX2JldF9hbW91bnQiCmFwcF9nbG9iYWxfZ2V0Cj4KYXNzZXJ0Cmdsb2JhbCBMYXRlc3RUaW1lc3RhbXAKYnl0ZWMgNCAvLyAiYmV0X2VuZCIKYXBwX2dsb2JhbF9nZXQKPAphc3NlcnQKZnJhbWVfZGlnIC0xCmd0eG5zIFNlbmRlcgpib3hfZ2V0CnN0b3JlIDEyCnN0b3JlIDExCmxvYWQgMTIKYXNzZXJ0CmZyYW1lX2RpZyAtMQpndHhucyBTZW5kZXIKYm94X2dldApzdG9yZSAxNApzdG9yZSAxMwpsb2FkIDE0CmFzc2VydApsb2FkIDEzCmZyYW1lX2J1cnkgMApmcmFtZV9kaWcgMAppbnRjXzAgLy8gMApleHRyYWN0X3VpbnQ2NApmcmFtZV9idXJ5IDIKZnJhbWVfZGlnIDAKaW50Y18zIC8vIDgKZXh0cmFjdF91aW50NjQKZnJhbWVfYnVyeSAxCmZyYW1lX2RpZyAwCmV4dHJhY3QgMTYgMApmcmFtZV9idXJ5IDMKZnJhbWVfZGlnIC0xCmd0eG5zIEFtb3VudApmcmFtZV9kaWcgMQorCmZyYW1lX2J1cnkgNApmcmFtZV9kaWcgMgppdG9iCmZyYW1lX2RpZyA0Cml0b2IKY29uY2F0CmZyYW1lX2RpZyAzCmNvbmNhdApmcmFtZV9idXJ5IDAKZnJhbWVfZGlnIC0xCmd0eG5zIFNlbmRlcgpib3hfZGVsCnBvcApmcmFtZV9kaWcgLTEKZ3R4bnMgU2VuZGVyCmZyYW1lX2RpZyAwCmJveF9wdXQKcmV0c3ViCgovLyBnZXRfYmV0CmdldGJldF81Ogpwcm90byAwIDEKYnl0ZWNfMCAvLyAiIgp0eG4gU2VuZGVyCmJveF9nZXQKc3RvcmUgMTYKc3RvcmUgMTUKbG9hZCAxNgphc3NlcnQKbG9hZCAxNQpmcmFtZV9idXJ5IDAKcmV0c3ViCgovLyBnZXRfdG90YWxfYmV0cwpnZXR0b3RhbGJldHNfNjoKcHJvdG8gMSAxCmludGNfMCAvLyAwCmR1cG4gMgpieXRlY18wIC8vICIiCmR1cAppbnRjXzAgLy8gMApkdXAKYnl0ZWNfMCAvLyAiIgpkdXAKaW50Y18wIC8vIDAKZnJhbWVfYnVyeSAxCmludGNfMCAvLyAwCmZyYW1lX2J1cnkgMgpnbG9iYWwgWmVyb0FkZHJlc3MKZnJhbWVfYnVyeSAzCmZyYW1lX2RpZyAzCmxlbgppbnRjXzIgLy8gMzIKPT0KYXNzZXJ0CmludGNfMCAvLyAwCmZyYW1lX2J1cnkgMApmcmFtZV9kaWcgMgppdG9iCmZyYW1lX2RpZyAxCml0b2IKY29uY2F0CmZyYW1lX2RpZyAzCmNvbmNhdApmcmFtZV9idXJ5IDQKYnl0ZWNfMiAvLyAibGF0ZXN0X2JldHRvcl9hY2NvdW50IgphcHBfZ2xvYmFsX2dldApmcmFtZV9idXJ5IDMKZnJhbWVfZGlnIDMKbGVuCmludGNfMiAvLyAzMgo9PQphc3NlcnQKZ2V0dG90YWxiZXRzXzZfbDE6CmZyYW1lX2RpZyAzCmdsb2JhbCBaZXJvQWRkcmVzcwohPQpieiBnZXR0b3RhbGJldHNfNl9sNApmcmFtZV9kaWcgMwpib3hfZ2V0CnN0b3JlIDE4CnN0b3JlIDE3CmxvYWQgMTgKYXNzZXJ0CmxvYWQgMTcKZnJhbWVfYnVyeSA0CmZyYW1lX2RpZyA0CmludGNfMyAvLyA4CmV4dHJhY3RfdWludDY0CmZyYW1lX2J1cnkgMQpmcmFtZV9kaWcgNApleHRyYWN0IDE2IDAKZnJhbWVfYnVyeSAzCmZyYW1lX2RpZyA0CmludGNfMCAvLyAwCmV4dHJhY3RfdWludDY0CmZyYW1lX2J1cnkgMgpmcmFtZV9kaWcgMgpmcmFtZV9kaWcgLTEKPT0KYnogZ2V0dG90YWxiZXRzXzZfbDEKZnJhbWVfZGlnIDAKZnJhbWVfZGlnIDEKKwpmcmFtZV9idXJ5IDAKYiBnZXR0b3RhbGJldHNfNl9sMQpnZXR0b3RhbGJldHNfNl9sNDoKcmV0c3Vi";
    override clearProgram: string = "I3ByYWdtYSB2ZXJzaW9uIDgKcHVzaGludCAwIC8vIDAKcmV0dXJu";
    override methods: algosdk.ABIMethod[] = [
        new algosdk.ABIMethod({ name: "place_bet", desc: "", args: [{ type: "pay", name: "payment", desc: "" }, { type: "uint64", name: "result", desc: "" }], returns: { type: "(uint64,uint64,address)", desc: "" } }),
        new algosdk.ABIMethod({ name: "increase_bet", desc: "", args: [{ type: "pay", name: "payment", desc: "" }], returns: { type: "(uint64,uint64,address)", desc: "" } }),
        new algosdk.ABIMethod({ name: "get_bet", desc: "", args: [], returns: { type: "(uint64,uint64,address)", desc: "" } }),
        new algosdk.ABIMethod({ name: "get_total_bets", desc: "", args: [{ type: "uint64", name: "result", desc: "" }], returns: { type: "uint64", desc: "" } })
    ];
    async place_bet(args: {
        payment: algosdk.TransactionWithSigner | algosdk.Transaction;
        result: bigint;
    }, txnParams?: bkr.TransactionOverrides): Promise<bkr.ABIResult<BettorRecord>> {
        const result = await this.execute(await this.compose.place_bet({ payment: args.payment, result: args.result }, txnParams));
        return new bkr.ABIResult<BettorRecord>(result, BettorRecord.decodeResult(result.returnValue));
    }
    async increase_bet(args: {
        payment: algosdk.TransactionWithSigner | algosdk.Transaction;
    }, txnParams?: bkr.TransactionOverrides): Promise<bkr.ABIResult<BettorRecord>> {
        const result = await this.execute(await this.compose.increase_bet({ payment: args.payment }, txnParams));
        return new bkr.ABIResult<BettorRecord>(result, BettorRecord.decodeResult(result.returnValue));
    }
    async get_bet(txnParams?: bkr.TransactionOverrides): Promise<bkr.ABIResult<BettorRecord>> {
        const result = await this.execute(await this.compose.get_bet(txnParams));
        return new bkr.ABIResult<BettorRecord>(result, BettorRecord.decodeResult(result.returnValue));
    }
    async get_total_bets(args: {
        result: bigint;
    }, txnParams?: bkr.TransactionOverrides): Promise<bkr.ABIResult<bigint>> {
        const result = await this.execute(await this.compose.get_total_bets({ result: args.result }, txnParams));
        return new bkr.ABIResult<bigint>(result, result.returnValue as bigint);
    }
    compose = {
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
        get_bet: async (txnParams?: bkr.TransactionOverrides, atc?: algosdk.AtomicTransactionComposer): Promise<algosdk.AtomicTransactionComposer> => {
            return this.addMethodCall(algosdk.getMethodByName(this.methods, "get_bet"), {}, txnParams, atc);
        },
        get_total_bets: async (args: {
            result: bigint;
        }, txnParams?: bkr.TransactionOverrides, atc?: algosdk.AtomicTransactionComposer): Promise<algosdk.AtomicTransactionComposer> => {
            return this.addMethodCall(algosdk.getMethodByName(this.methods, "get_total_bets"), { result: args.result }, txnParams, atc);
        }
    };
}
