# vani-knowledge-llm-wiki

Vani 的公開版知識庫治理契約與 Hermes Agent skills 集合。

本 repository 只保存可公開、可版控的治理規則與 runtime skill；**不包含任何實際收錄的知識、Inbox 內容、來源正文、私人對話、audit manifest、credentials 或 backup corpus**。

## 內容範圍

### Skills

- `skills/research/llm-wiki/`
- `skills/note-taking/knowledge-inbox-capture/`
- `skills/knowledge/governed-batch-knowledge-ingestion/`
- `skills/note-taking/knowledge-archive-ingestion/`

每個 skill 會保留其 `SKILL.md`、`references/` 與 `scripts/`（若原始 skill 有提供）。

### Knowledge contracts

- `knowledge-contracts/README.md`
- `knowledge-contracts/inbox/README.md`
- `knowledge-contracts/system/README.md`
- `knowledge-contracts/sources/README.md`
- `knowledge-contracts/staging/README.md`

這些是 knowledge 的基礎結構與治理契約，不是實際知識內容。

## 不包含的內容

- `${KNOWLEDGE_ROOT}` 底下的實際文章、對話、來源與正式知識。
- `inbox/` 內除契約 README 外的任何投遞材料。
- `sources/`、`staging/`、`domains/`、`projects/`、`entities/`、`archive/` 的實際資料。
- 個人 backup、audit run、migration manifest、private archive 或 frozen artifact。
- API keys、tokens、passwords、credentials 或其他秘密。

公開版本會把本機絕對路徑、部署 instance identifier、GCP generation 與 frozen artifact 識別泛化為 placeholder；詳見 `PUBLICIZATION.json` 與 `SOURCE-MANIFEST.json`。

## 目標

這個 repo 的目標是讓治理規則可以：

1. 透過 Git 追蹤修正與版本演進。
2. 以 pull request 審查制度級變更。
3. 被其他 Hermes Agent 使用或 fork。
4. 在不攜帶私人知識資料的前提下，更新本機 skills 與 knowledge contracts。

## 使用方式

先閱讀：

1. `skills/note-taking/knowledge-inbox-capture/SKILL.md`
2. `knowledge-contracts/inbox/README.md`
3. `knowledge-contracts/README.md`
4. `knowledge-contracts/system/README.md`
5. `knowledge-contracts/sources/README.md`
6. `knowledge-contracts/staging/README.md`

本機同步流程見 [`docs/sync.md`](docs/sync.md)。不要直接用未審查的遠端內容覆蓋本機 runtime；先 fetch、檢查 diff、驗證，再進行受控同步。

## 版本與變更

- 使用 Git commit、tag 與 pull request 保存治理變更。
- 修改 contract 或 skill 時，必須在 PR 中說明 scope、相容性、migration 影響與驗證結果。
- 不在這個 repo 裡建立實際知識資料來做測試；測試資料應放在外部暫存目錄或 CI fixture，且不得含私人內容。
- 目前公開套件採 MIT License，見 [`LICENSE`](LICENSE)。

## Status

目前是第一個公開集合版本，內容來源是 Vani 本機 Hermes runtime 的四個相關 skill 與五份 knowledge 基礎契約的公開化投影。
