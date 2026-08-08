# 本機同步指南

這個 repo 是公開的 skill／knowledge-contract projection；它不攜帶實際 knowledge。同步時必須分開處理：

```text
public repository
  ├── skills/                 → Hermes runtime skills
  └── knowledge-contracts/    → knowledge root 的基礎契約

實際 knowledge content 不在同步範圍內。
```

## 1. 設定路徑

在自己的環境指定：

```sh
export HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
export KNOWLEDGE_ROOT="${KNOWLEDGE_ROOT:-$HOME/knowledge}"
```

不要把含有真實本機路徑、token 或 audit location 的設定提交到 repository。

## 2. 取得更新

```sh
git clone https://github.com/vanimancini/vani-knowledge-llm-wiki.git
cd vani-knowledge-llm-wiki
git fetch origin --tags --prune
git log --oneline --decorate -5
```

既有 checkout 則使用：

```sh
git fetch origin --tags --prune
git checkout main
git pull --ff-only origin main
```

同步前先確認 remote 是預期的 `vanimancini/vani-knowledge-llm-wiki`，且 worktree 沒有未提交變更。

## 3. 對照本機 runtime

先做 dry-run，不要直接覆蓋：

```sh
rsync -a --dry-run --itemize-changes \
  skills/research/llm-wiki/ \
  "$HERMES_HOME/skills/research/llm-wiki/"

rsync -a --dry-run --itemize-changes \
  skills/note-taking/knowledge-inbox-capture/ \
  "$HERMES_HOME/skills/note-taking/knowledge-inbox-capture/"

rsync -a --dry-run --itemize-changes \
  skills/knowledge/governed-batch-knowledge-ingestion/ \
  "$HERMES_HOME/skills/knowledge/governed-batch-knowledge-ingestion/"

rsync -a --dry-run --itemize-changes \
  skills/note-taking/knowledge-archive-ingestion/ \
  "$HERMES_HOME/skills/note-taking/knowledge-archive-ingestion/"
```

Knowledge contract 的對照位置是：

```sh
diff -u "$KNOWLEDGE_ROOT/README.md" knowledge-contracts/README.md || true
diff -u "$KNOWLEDGE_ROOT/inbox/README.md" knowledge-contracts/inbox/README.md || true
diff -u "$KNOWLEDGE_ROOT/system/README.md" knowledge-contracts/system/README.md || true
diff -u "$KNOWLEDGE_ROOT/sources/README.md" knowledge-contracts/sources/README.md || true
diff -u "$KNOWLEDGE_ROOT/staging/README.md" knowledge-contracts/staging/README.md || true
```

公開版本使用 `${KNOWLEDGE_ROOT}` 等 placeholder；因此對照時要區分「公開化路徑差異」與「真正的契約內容差異」。

## 4. 套用更新的安全要求

只有在以下條件全部成立後，才可套用經審查的更新：

1. 確認 upstream commit、tag 或 PR 已經是預期版本。
2. 確認變更仍只落在四個 skill 與五份 contract 的 allowlist。
3. 先在外部 audit／rollback 位置保存目前本機檔案與 hash。
4. 再次執行 dry-run，確認沒有誤碰實際 knowledge。
5. 套用後執行 `git diff --check`、`python3 -m compileall` 與指定 skill tests。
6. 逐檔 read-back，確認檔案內容、權限與版本一致。

不要直接使用未檢查的 `rsync --delete`。本機額外檔案不應因公開 repo 同步而被刪除；若要刪除，必須另有明確 allowlist 與授權。

## 5. 更新方向

公開 repo 的治理變更應先在 GitHub PR 中審查，再同步到本機 runtime。反過來若先在本機發現修正，應整理成不含私人資料的 patch，提交到公開 repo，而不是把本機整個 `.hermes` 或 knowledge root 推上去。
