require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/** Hedera is EVM-compatible via the JSON-RPC relay (Hashio).
 *  Testnet chainId = 296, Mainnet = 295, Previewnet = 297.
 *  Gas is paid in HBAR but fees are USD-pegged — the fee-predictability property
 *  the whole micropayment design depends on (deck §3).
 */
module.exports = {
  solidity: {
    version: "0.8.24",
    settings: { optimizer: { enabled: true, runs: 200 } },
  },
  networks: {
    hederaTestnet: {
      url: process.env.HEDERA_RPC_URL || "https://testnet.hashio.io/api",
      chainId: 296,
      accounts: process.env.OPERATOR_PRIVATE_KEY ? [process.env.OPERATOR_PRIVATE_KEY] : [],
    },
    uzhEthereum: {
      // course PoC platform — fill in from course materials
      url: process.env.UZH_RPC_URL || "",
      chainId: Number(process.env.UZH_CHAIN_ID || 0),
      accounts: process.env.OPERATOR_PRIVATE_KEY ? [process.env.OPERATOR_PRIVATE_KEY] : [],
    },
  },
};
