# Knowledge Inbox

> `${KNOWLEDGE_ROOT}/inbox/` 是唯一、簡單的投遞入口；不是 queue、來源庫、分析區或正式知識庫。

## 受理格式

一般投入檔使用 `YYYY-MM-DD-short-slug.md`；slug 為小寫英數與連字號。最低 metadata：

```yaml
---
title: 原始標題或簡短描述
captured: 2026-07-27
kind: url
source_url: https://example.com/item
status: new
---
```

`kind` 可為 `url`、`document`、`idea`、`excerpt`；`status` 在 inbox 僅使用 `new`。無網址時省略 `source_url`。不得在投遞時改寫來源、猜測 metadata 或宣稱已查證。

## Inbox capture 邊界

本節適用於單純的 Inbox 投遞。Capture 只能建立一份 `status: new` 的直接子層 Markdown，或在另案明確授權時原位升級同一來源的既有 lightweight artifact。

寫入前必須以 resolved 的 knowledge root、Inbox root 與 target 做機械驗證：`${KNOWLEDGE_ROOT}/inbox/` 本身不得是 symlink，resolved Inbox 必須仍位於 resolved knowledge root 之下；target 必須是絕對路徑、直接位於 `inbox/`、符合 `YYYY-MM-DD-short-slug.md`、不是 `README.md`；一般 full/lightweight capture 不得覆寫既有檔案，只有明確的 in-place upgrade 可使用既有同一路徑。

下方 Frozen ZIP 規則屬於獨立的 no-touch 邊界。

## 後續分流程序（不屬於 Inbox 投遞）

本節只適用於另案啟動的 promotion／正式知識庫分流；**不得在「收錄進 Inbox／僅入庫」的 Inbox capture 時執行，也不得阻止建立 Inbox 檔案**。Inbox capture 僅依上方「受理格式」、「Inbox capture 邊界」與 Frozen ZIP 規則建立一份 `status: new` 的投遞檔。

1. 先做安全、授權、敏感資料與重複來源 preflight；失敗即停止並留下可讀說明，不自動刪除。
2. 可保存的來源先依 [[sources/README]] 建立 canonical source；轉換內容只可作 deterministic projection。
3. 分類、抽取、去重與候選內容只進 [[staging/README]]，不得直接寫入正式層。
4. 經 promotion authority 核准後，才可發布到 `domains/`、`projects/` 或 `entities/`；已知但不再活躍的正式知識才可進 `archive/`。
5. 成功分流須由工具通過 schema、hash、link 與 manifest gate（失敗回傳 non-zero），並留下 import run；Inbox 不保留人工副本。

分流不確定時保持原檔不動；不要增加優先級、負責人或多階段 queue 欄位。

## Frozen ZIP

`<frozen-artifact>` 固定凍結於原位。禁止開啟、列出 entry、解壓、搬移、重新命名、解析、分類、索引或匯入；scanner 必須按精確路徑排除。只有另案明確授權與新的 migration manifest 才能解除凍結。
