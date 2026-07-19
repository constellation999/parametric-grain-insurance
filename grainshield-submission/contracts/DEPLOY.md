# GrainShield — Hedera PoC (DDiB 2026)

Dual-trigger parametric insurance の5コンポーネント(deck §3 アーキテクチャ)を Solidity で実装し、Hedera Testnet(EVM互換)にデプロイする PoC。

```
contracts/
  MockUSD.sol        テスト用ステーブルコイン(本番は Stablecoin Studio / HTS に置換)
  PolicyRegistry.sol アグリゲータ経由の加入、Buyer/Seller 2クラス、sum insured
  TriggerOracle.sol  2段階ステートマシン(衛星 Stage1 → エンタイトルメント中央値 Stage2)
  PremiumStream.sol  収入連動0.5%スキム + 危機時の自動プレミアム免除
  EscrowVault.sol    ドナー3トランシェ、トリガー拘束リリース(管理者引き出し関数なし)
  PayoutRouter.sol   pay = S·max(0, min(r,2.25)−1.25)、ウォーターフォール充当
scripts/
  deploy.js          6コントラクトのデプロイ + 循環参照の配線
  demo.js            加入→スキム→Stage1早期支払→免除→Stage2本支払 の一気通貫デモ
```

## デプロイ手順(Hedera Testnet)

### 0. 前提
- Node.js 18+
- Hedera Portal アカウント: https://portal.hedera.com

### 1. テストネットアカウント作成(重要: ECDSA)
1. Portal で Testnet アカウントを作成。**鍵タイプは ECDSA を選択**(ED25519 は EVM ツールチェーンで使えない)
2. HEX Encoded Private Key をコピー
3. Portal が 1000 test HBAR を自動付与(足りなければ faucet.hedera.com — ガスは数 HBAR で十分)

### 2. セットアップ
```bash
npm install
cp .env.example .env   # OPERATOR_PRIVATE_KEY を記入
npx hardhat compile
```

### 3. デプロイ
```bash
npx hardhat run scripts/deploy.js --network hederaTestnet
```
出力された6アドレスを `.env` の MOCKUSD/REGISTRY/... に記入。

### 4. 動作確認(HashScan で見せられるデモ)
```bash
npx hardhat run scripts/demo.js --network hederaTestnet
```
その後 https://hashscan.io/testnet でデプロイヤーアドレスを検索 →
`EarlyPayoutTriggered` / `PremiumWaived` / `MainPayoutConfirmed` / `MainPayout` の
イベント列がそのままプレゼンのスクリーンショット素材になる。

### トラブルシューティング
- `insufficient funds` → HBAR残高不足。faucet.hedera.com
- nonce エラー / タイムアウト → Hashio は公開リレー。数秒待ってリトライ、または `HEDERA_RPC_URL` を Arkhia 等の代替リレーに変更
- ED25519 鍵でデプロイ失敗 → ECDSA アカウントを作り直す(最頻出のハマりポイント)

## 設計上の対応関係(レポート/プレゼン用)
| デッキの主張 | コード上の実装 |
|---|---|
| "no admin function can divert funds" | EscrowVault に owner-withdraw が存在しない。release は immutable な router 宛のみ + `oracle.isCrisisActive` 必須 |
| "no single feed can fire a payout" | TriggerOracle: MIN_REPORTS=3 の中央値、かつ Stage1 が active でないと Stage2 を受理しない(conjunction) |
| premium-waiver-by-code | PremiumStream.onIncomeEvent が危機中は転送せず PremiumWaived を emit |
| "no claims, no adjusters" | PayoutRouter の execute* は permissionless(誰でも実行可能な keeper パターン) |
| ウォーターフォール | _fund(): 自己準備金 → Seed → PremiumMatch → ContingentCredit |
| Hedera 選定理由 | 手数料がUSD建て固定サブセント → $0.03/日のスキムが成立(fee-floor 論法) |

## 本番との差分(レポートの limitations に書く)
- MockUSD → Stablecoin Studio の HTS トークン(KYC/freeze フラグ)
- Reporter を管理者登録 → HCS トピックの順序付きアテステーション
- 手動 resetRegion / resetAnnual → epoch ベースの自動化
- ヘッジャーキャップ・再保険回収はオフチェーンレッグ(エスクロートランシェで代理)
