# 貢獻指南

感謝協助改善 `vani-knowledge-llm-wiki`。

## Pull request 範圍

每個 PR 應該只處理一個清楚的目標，例如：

- 修正 Inbox capture 規則。
- 修正 knowledge source 或 staging contract。
- 補充跨平台同步說明。
- 修正 skill script 的可攜性問題。
- 補充測試或公開化檢查。

請不要在同一個 PR 混入實際 knowledge、個人設定、未核准的治理改寫或無關的 runtime 變更。

## 公開內容要求

不得提交：

- 私人對話、文章正文、Inbox 檔案或來源資料。
- token、API key、password、cookie、credential、private key。
- 個人電腦絕對路徑、backup location、audit manifest 或 cloud instance identifier。
- 真實 frozen archive 或任何未公開授權的二進位檔。

本 repository 使用 placeholder 表示 runtime-specific 值。若新增需要部署環境的設定，請把它寫成環境變數或泛化 placeholder，並在 README 說明取得方式。

## 變更與驗證

提交前請執行：

```sh
git diff --check
python3 -m compileall skills
```

並確認：

```sh
git status --short --branch
git diff --name-only
```

所有變更路徑都必須屬於 PR 說明的 scope。若修改了 skill 的 `SKILL.md`，請同步檢查其 `references/` 與 `scripts/` 是否仍然一致。

## Commit 與 PR

- Commit message 使用清楚、短而具體的描述，例如：
  - `docs: clarify inbox capture boundary`
  - `fix: make intent router path portable`
- PR 使用臺灣正體中文，說明：
  - 變更摘要。
  - 影響的 skill 或 contract。
  - 是否有相容性或 migration 影響。
  - 實際驗證指令與結果。
  - 是否需要同步本機 runtime。

## License

本 repo 採 MIT License。提交內容必須由提交者擁有或具有足夠授權，且不得把未授權的第三方或私人內容帶入 repository。
