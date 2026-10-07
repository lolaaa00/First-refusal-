#!/usr/bin/env node

import keytar from "keytar";
import {createAccount, createClient} from "genlayer-js";
import {studionet} from "genlayer-js/chains";
import {CalldataAddress} from "genlayer-js/types";

const RPC = "https://studio.genlayer.com/api";

function option(name) {
  const index = process.argv.indexOf(name);
  if (index < 0 || index + 1 >= process.argv.length) {
    throw new Error(`missing ${name}`);
  }
  return process.argv[index + 1];
}

function decode(value) {
  if (Array.isArray(value)) return value.map(decode);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, decode(item)]));
  }
  if (typeof value === "string" && /^addr#[0-9a-fA-F]{40}$/.test(value)) {
    return new CalldataAddress(Buffer.from(value.slice(5), "hex"));
  }
  return value;
}

const accountName = option("--account");
const address = option("--address");
const method = option("--method");
const args = decode(JSON.parse(option("--args-json")));
const privateKey = await keytar.getPassword("genlayer-cli", `account:${accountName}`);
if (!privateKey) throw new Error(`account ${accountName} is not unlocked`);

const client = createClient({
  chain: studionet,
  endpoint: RPC,
  account: createAccount(privateKey),
});
await client.initializeConsensusSmartContract();
const hash = await client.writeContract({
  address,
  functionName: method,
  args,
  value: 0n,
});
const receipt = await client.waitForTransactionReceipt({
  hash,
  retries: 100,
  interval: 5000,
});

const leaderResult = receipt?.consensus_data?.leader_receipt?.[0]?.result ?? null;
console.log(JSON.stringify({
  transaction_hash: hash,
  status: receipt?.status_name ?? receipt?.status ?? null,
  consensus_result: receipt?.result_name ?? receipt?.result ?? null,
  leader_result: leaderResult,
}, (_, value) => typeof value === "bigint" ? value.toString() : value, 2));
