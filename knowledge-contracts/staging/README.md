# Staging

`staging/` 只保存可重建的分析與審查 reference，不是來源證據或正式知識。指定四個子目錄：

- `unclassified/`：尚未完成分類的分析、分類理由、抽取結果與必要 reference。
- `knowledge-candidates/`：待升格的 domain、project、decision 或 entity 候選稿。
- `duplicate-groups/`：重複／衝突群組的比對、定位與處置建議；不得改寫 canonical source。
- `domain-suggestions/`：建議新增或調整 domain 的審查資料；未經核准不得建立正式 domain。

每筆資料遵守 [[system/schemas/staging-record-schema]]，必須可追到 canonical source、deterministic projection 或正式頁面的固定 hash；reference 放在所屬 staging record，不另建全域 reference 目錄。Staging scanner 不得把內容納入正式搜尋、知識 map 或 domain／project index。

## 升格

Prompt 只能提出候選。Roy 或 Roy 明確委派的 maintainer 是 promotion authority；核准紀錄必須包含審查者、時間、目標路徑、來源 hash 與決定。發布工具先通過 schema、來源獨立性、路徑、link、hash 與測試 gate；任一失敗 non-zero 並保持正式層不變。發布後 staging record 可保留作稽核，但不得被視為第二份正式內容。
