# Knowledge System

`system/` 保存治理契約與可稽核操作紀錄，不保存 domain／project 正式內容。

## 元件

- `schemas/`：機器可驗證的文件契約；衝突時以適用的 schema 與 migration manifest 為準。
- `prompts/`：可重現的模型工作說明，**不是 enforcement**，也沒有 promotion authority。
- `scripts/`：驗證、匯入與遷移程式的責任契約；測試或驗證失敗必須 non-zero exit。
- `import-runs/`：每次匯入的唯讀 run record 與 manifest。
- `logs/maintenance.md`：治理層 append-only 維護紀錄。

## 不可跳過的 gate

所有批次寫入依序執行 preflight、dry-run、schema／hash／path 驗證、建立 migration manifest、核准、原子寫入、read-back。任何 script 或 test 出現錯誤、未知 schema、hash 不符、越界路徑或不平衡 frontmatter 時，必須以非零狀態終止；不得以 prompt 遵循、人工目測或「部分成功」取代。

## 相容性

Legacy raw body 不因新 schema 就地改寫。whole-file SHA-256 是 migration rollback authority；body SHA-256 必須連同明確 `hash_profile` 記錄。遇到雙層 frontmatter，只解析檔案開頭第一層；後續 `---` 與類 YAML 區塊全部視為 body bytes。

權責、索引與復原總則見根目錄 [[README]]。
