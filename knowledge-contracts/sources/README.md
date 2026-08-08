# Sources

`sources/` 是來源證據層，不是綜整知識。新資料依來源類型進入下列指定目錄：

- `chatgpt/exports/`：只有另案核准將 ChatGPT export 放進 knowledge root 時，保存該 export 的 canonical source bytes 與 provenance。
- `chatgpt/conversations/`：預設保存 conversation-level deterministic projections；若 authority 明確決定 upstream export 留在 knowledge root 外，則每份由核准 deterministic converter 產生的 Markdown 可各自作為 immutable `canonical_source`。兩種 record kind 不得混稱或事後改標。
- `articles/`：文章來源的 canonical captures，以及依文章來源型別約定位置保存的 deterministic projections。
- `repositories/`：repository 來源的 canonical captures，以及依 repository 來源型別約定位置保存的 deterministic projections。
- `social/`：社群來源的 canonical captures，以及依社群來源型別約定位置保存的 deterministic projections。
- `transcripts/`：逐字稿來源的 canonical captures，以及依逐字稿來源型別約定位置保存的 deterministic projections。

同一 capture 只有一份 canonical source。Projection 不是第二個來源、不是獨立證據，也不得取代 canonical bytes；投影必須放在各來源類型約定的位置，不另建全域 `canonical/` 或 `projections/`。每份 projection 必須記 `canonical_source_id`、輸入 whole-file SHA-256、transform 名稱／版本／參數及輸出 SHA-256；相同輸入與設定必須得到相同輸出。模型或人工分析不具 deterministic 性，只能放 `staging/` 的對應審查目錄。

## Raw-source sidecar 命名

Canonical 規則是 `sidecar_path = payload_path + '.source.md'`。Sidecar 必須與 payload 同目錄，且先保留 payload 的完整原檔名與副檔名，再附加 `.source.md`：`sources/articles/example.html` 對應 `sources/articles/example.html.source.md`，`x.md` 對應 `x.md.source.md`。禁止 `<stem>.source.md`、basename-only 比對、移到其他目錄或其他模糊變體。

## 寫入程序

1. 取得授權與安全 preflight；拒絕 secret、無法安全去識別資料與不明授權二進位。
2. 先寫暫存檔並計算 whole-file SHA-256；驗證後原子移入上述來源類型的指定目錄，不得覆寫既有 canonical capture。
3. 需要 projection 時以已驗證 canonical hash 為輸入；產物通過重跑一致性測試才可落地。
4. 建立 import-run／migration manifest，再由 scanner 納入允許的文字來源。

Legacy raw 保留原路徑與 bytes，不因本目錄建立而搬移。Hash 與 frontmatter 規則見 [[system/schemas/raw-source-schema]]。
