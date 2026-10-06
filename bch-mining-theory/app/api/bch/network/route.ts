import { NextResponse } from "next";
import type { BchNetwork } from "../../../../types/bch";

export const dynamic = "force-dynamic";

const rpcUrl = process.env.BCH_RPC_URL;
const rpcUser = process.env.BCH_RPC_USER;
const rpcPassword = process.env.BCH_RPC_PASSWORD;

async function rpc<T>(method: string, params: unknown[] = []): Promise<T> {
  if (!rpcUrl || !rpcUser || !rpcPassword) {
    throw new Error("BCH RPC environment is not configured");
  }

  const response = await fetch(rpcUrl, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      authorization: `Basic ${Buffer.from(`${rpcUser}:${rpcPassword}`).toString("base64")}`,
    },
    body: JSON.stringify({ jsonrpc: "1.0", id: "bch-theory", method, params }),
    cache: "no-store",
  });

  if (!response.ok) throw new Error(`BCH RPC returned HTTP ${response.status}`);

  const payload = (await response.json()) as { result?: T; error?: { message?: string } };
  if (payload.error) throw new Error(payload.error.message ?? "Unknown BCH RPC error");
  return payload.result as T;
}

type MiningInfo = {
  chain?: string;
  blocks?: number;
  difficulty?: number;
  networkhashps?: number;
};

type BlockchainInfo = {
  bestblockhash?: string;
};

export async function GET() {
  try {
    const [miningInfo, blockchainInfo, measuredHashrate] = await Promise.all([
      rpc<MiningInfo>("getmininginfo"),
      rpc<BlockchainInfo>("getblockchaininfo"),
      rpc<number>("getnetworkhashps", [120, -1]),
    ]);

    const result: BchNetwork = {
      chain: miningInfo.chain ?? "main",
      blocks: miningInfo.blocks ?? 0,
      difficulty: miningInfo.difficulty ?? 0,
      networkHashrate: measuredHashrate || miningInfo.networkhashps || 0,
      bestBlockHash: blockchainInfo.bestblockhash ?? "",
      fetchedAt: new Date().toISOString(),
    };

    if (!result.difficulty || !result.networkHashrate) {
      throw new Error("BCH node returned incomplete mining data");
    }

    return NextResponse.json(result, {
      headers: { "cache-control": "no-store" },
    });
  } catch (error) {
    console.error("BCH network API error:", error);
    return NextResponse.json(
      {
        error: "BCH network data unavailable",
        detail: process.env.NODE_ENV === "development" && error instanceof Error ? error.message : undefined,
      },
      { status: 503 },
    );
  }
}
