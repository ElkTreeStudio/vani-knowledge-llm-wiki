# Agent 協作規則

## 1. Repository 邊界

本 repository 是公開的 skills 與 knowledge-contracts 集合，不是知識資料庫本身。

允許納入：

- 指定的四個 Hermes skills。
- 指定的五份 knowledge 基礎契約。
- 公開化所需的 README、同步說明、測試與授權檔。

禁止納入：

- 實際文章、對話、來源正文或 Inbox 投遞資料。
- `sources/`、`domains/`、`projects/`、`entities/`、`archive/` 的實際內容。
- 私人路徑、audit manifest、backup corpus、frozen artifact、token、API key、password 或其他秘密。

## 2. 修改前檢查

```sh
git status --short --branch
git remote -v
git diff --check
```

修改前要確認：

- 變更仍在本 repo 的 allowlist 內。
- 沒有把實際 knowledge root 或本機 runtime 資料複製進來。
- 公開化 placeholder 沒有被換回真實本機路徑或 instance identifier。
- source 與 generated/public projection 的關係可追溯。

## 3. 變更流程

1. 先修改 skill 或 contract 的公開版本。
2. 補充 `PUBLICIZATION.json` 或相關 manifest。
3. 執行 repository checks。
4. 以 Traditional Chinese 撰寫 commit 與 pull request 說明，除非另有要求。
5. 讓變更經過 review 後，才同步到本機 Hermes runtime。

## 4. 同步安全

- 不直接覆蓋本機 skill 或 knowledge contract。
- 同步前先保留外部 rollback backup，並讀回 remote revision。
- 先使用 dry-run 與 diff，確認 allowlist、版本與檔案數量一致。
- 不因公開 repo 的內容而自動改寫實際 knowledge。
- 不刪除本機額外檔案，除非有明確 allowlist 與獨立授權。

## 5. 驗證

至少執行：

```sh
git diff --check
python3 -m compileall skills
```

另外要檢查：

- `git status --short --branch`。
- 只存在預期的 skill、contract 與 repo 文件。
- 沒有 `*.env`、secret、credential、實際知識檔或 audit artifact。
- Markdown 沒有工具 transcript、`OUTPUT TRUNCATED`、模型內部訊息或錯誤 code fence。

## 6. 外部副作用

建立公開 repo、push、建立 release、邀請 collaborator、修改 branch protection 或發佈 tag 都是獨立的外部副作用；必須有明確授權，並在操作後讀回 GitHub 狀態。
