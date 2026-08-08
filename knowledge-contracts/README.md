# Vani Knowledge

> `${KNOWLEDGE_ROOT}/` 是長期知識的 canonical root。

## 頂層結構

- `inbox/`：唯一簡單投遞入口；尚未受理的材料。
- `system/`：schema、prompt、script、import run 與維護規則。
- `sources/`：canonical source 與其 deterministic projection。
- `staging/`：分析、候選與審查 reference；不是正式知識。
- `domains/`：跨專案可重用、經策展的正式知識。
- `projects/`：只對特定專案成立、經策展的正式知識。
- `entities/`：跨 domain／project 且由多個獨立來源支持的共享實體。
- `archive/`：已知、曾正式採用、現已不活躍的正式知識。

治理入口見 [[system/README]]；來源契約見 [[sources/README]]；暫存契約見 [[staging/README]]。

## 權責與發布

- `knowledge-map.md` 由人工策展，工具不得覆寫。
- domain／project 的 `index.md` 維持精簡策展導航；本次遷移只更新路徑，不導入額外 generator。
- 內容升格（promotion）必須由 Roy 或 Roy 明確委派的 maintainer 核准；prompt 或模型輸出不能自行發布。
- `system/prompts/` 只是可重現操作指引，**不是 enforcement**。真正 gate 必須由 `system/scripts/` 的程式與測試執行，任何檢查失敗均以 non-zero exit 阻擋寫入／升格。

## 安全與復原

本庫的版本保存與復原只使用已驗證的 GCP backup、manifest 與逐檔 hash。破壞性批次前必須同時鎖定：

1. 已驗證 GCP baseline：generation `<verified-gcp-generation>`；
2. 外部 manifest：`${KNOWLEDGE_BASELINE_MANIFEST}`；
3. manifest 記錄的逐檔 SHA-256。

復原以該 GCP generation 與 manifest 為一組，不接受「最新物件」替代固定 generation。任何 migration 必須另產生 manifest，先驗證再切換；失敗時停止、保留現況並依固定 generation 復原。

## Scanner 排除

掃描、索引、嵌入、統計與 map 產生器必須排除：任意層級的 `.git/`、`.DS_Store`、`.backups/`、`backups/`、外部 backup corpus、binary／archive（含 ZIP、tarball）、`system/import-runs/`、`system/logs/`，以及 staging 中未升格內容。不得追蹤 symlink 離開 knowledge root。

`inbox/<frozen-artifact>` 是 frozen ZIP：不得開啟、列出 entry、解壓、搬移、解析、分類、索引或匯入；只有另案明確授權、通過 preflight 與可回復 manifest 後才可處理。
