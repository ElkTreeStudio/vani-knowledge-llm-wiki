---
name: knowledge-inbox-capture
description: "Use when Roy sends material for Inbox; full by default."
version: 1.9.0
---

# Knowledge Inbox Capture

## Overview

Roy 的 Inbox 收錄固定 SOP。當 Roy 把網頁、X 長文、電子報、文件、摘錄、想法或其他 material 提供給 Vani，並在語意上要求將它轉換／收錄至 `${KNOWLEDGE_ROOT}/inbox/`，預設就是**完整 capture**：保留可取得的全文／全部提供內容；原文不是台灣正體中文時完整翻譯，已是台灣正體中文則不另建翻譯；並產生 `Vani 摘要` 與 `Vani 心得與延伸見解`。輸出維持待整理狀態。

這裡的「僅入庫」是指**只投入 Inbox**，不是正式知識庫 promotion：不得建立 canonical source、分類到 domains/projects/entities、更新索引、搬移原檔或執行 ingestion pipeline。

## When to Use

當 Roy 要求：

- 將他提供的 material 轉換、收錄、保存或留存到 Inbox；
- 把文章、文件、摘錄、想法或其他內容放進 Inbox；
- 附上來源、翻譯、原文、摘要與心得／說明；
- 先投入 Inbox，但不要直接進正式知識庫。

### Stage A 兩種模式的語意分流

**凡是「把 Roy 提供的 material 轉換至 Inbox」的語意，都預設是完整 capture。**這不是對某個固定詞組做比對，也不是因為訊息中出現「收進 Inbox」才成立；active model 必須理解整則訊息、附件、連結與上下文，判斷 Roy 是否要把該 material 交付為 Inbox 內容。若判定是，完整保留可取得的全文／全部提供內容；原文不是台灣正體中文時完整翻譯，已是台灣正體中文則不另建翻譯；並產生 `Vani 摘要` 與 `Vani 心得與延伸見解`。

- `stage-a-inbox-only`（default）：任何語意上要把 Roy 提供的 material 轉換／收錄到 Inbox 的請求，以及明確要求完整原文、翻譯、摘要、心得或說明的請求。依 material 類型執行完整來源取得與固定完整 capture 章節。
- `stage-a-inbox-only-lightweight`（explicit exception only）：只有 Roy 在**當下訊息以自然語意明確指定**「只留連結／只收 metadata／不要抓正文／不要翻譯／不要摘要／輕量收錄」等其他做法時，才使用此模式。此模式只保存使用者已提供的標題／描述、canonical URL、收錄日期與「待後續完整整理」備註；**不得擅自 fetch、翻譯、摘要或宣稱已完成文章收錄**。

這是整則請求的自然語意分流，不是關鍵字分類器；不得用字串、固定詞表、正則或單一短語代替模型理解。active model 先判定「是否要把 material 轉換到 Inbox」及是否存在明確例外，再交給 `route_inbox_intent.py` 驗證 category 與邊界。若完整 capture 語意成立，不要降級成只有連結的輕量檔；若 lightweight 例外語意未明確成立，就使用完整 capture。

詳細的 semantic routing、長文 packet、structured-source coverage 與 wrapper-aware verification 見 `references/default-full-capture-semantic-routing.md`。

## Source of Truth
每次寫入前先讀 `${KNOWLEDGE_ROOT}/inbox/README.md`，以它當下的**投遞儲存契約**（檔名、最低 metadata、`status: new`、Frozen ZIP 排除）為準。不得拿舊收錄檔反推現行格式。

**Inbox-only 判定規則：**先由 active model 依整則訊息的自然語意判斷 Roy 是否要把已提供的 material 轉換／收錄至 Inbox，以及是否同時提出 promotion 或其他後續處理。若判定是 Inbox-only 且沒有語意上的 promotion 要求，README 中描述後續 canonical source、staging、promotion、索引或 pipeline 的一般分流程序屬於後續作業，**不適用於本次 Stage A capture**。此時必須直接建立唯一 Inbox Markdown；不得把後續分流程序誤判為與本 skill 衝突、不得要求 Roy 逐次裁示。只有 active model 語意判定要求 promotion，或 README 的投遞儲存契約本身無法判定時，才停止詢問。

## Stage A 執行者與模型政策

每一次 Inbox material capture 都**必須先由 active main brain 依下列規則選定整個 Stage A executor**：若 active main brain 的模型等級不高於 `GPT-5.6-luna max`，由 active main brain 親自執行完整 Stage A；若高於 `GPT-5.6-luna max`，由 active main brain 固定指派 `GPT-5.6-luna max` 執行完整 Stage A。選定的 executor 負責來源取得、deterministic rendering、翻譯、摘要／心得、固定格式組裝與唯一 Inbox artifact 寫入；若主腦本身是選定 executor，主 session 在 boundary／allowlist gate 通過後執行上述工作；若已指派 Luna Max，主 session 只負責語意路由、建立邊界、選模與獨立 deterministic verification。**Terra 不再是 Stage A executor，也不得作為翻譯或完整 capture 的 fallback。**選定 executor 的模型 provenance 只記錄在 knowledge 之外的 usage／audit，不擅增 README 未支援的 frontmatter。

### Stage A executor 固定規則

- 若 active main brain 的模型等級**不高於** `GPT-5.6-luna max`，由 active main brain **親自處理完整 Stage A**，包括來源取得、rendering、翻譯、摘要／心得、組裝與唯一 Inbox artifact 寫入。
- 若 active main brain 的模型等級**高於** `GPT-5.6-luna max`，由 active main brain **固定指派 `GPT-5.6-luna max` 處理完整 Stage A**；不得改派 Terra，也不得改派更低等級模型。
- 同一份 material 的所有 Stage A 工作與翻譯 batches 必須由同一個選定 executor 完成，不得中途混用主腦、Luna Max、Terra 或未經模型等級判定的 fallback。
- active main brain 必須能提出目前模型身分與「高於／不高於 `GPT-5.6-luna max`」的可驗證判定；若模型等級、目標模型路由或使用狀態無法確認，立即停止並回報 blocker。
- `GPT-5.6-luna max` 的 provider/model identifier 必須從當下已配置且可驗證的路由取得，不得自行猜測命令或只在 prompt 聲稱模型身分。

1. **先由 active model 做語意意圖判定，再由 deterministic validator 驗證邊界；禁止預讀正文。**收到 raw user request 後，active model 必須依完整自然語言、附件、連結與上下文判定是否是 material-to-Inbox conversion，以及是否有明確 lightweight override 或 promotion 要求；不得以任何 token、字串、空白、大小寫、固定短語、同義詞表或正則取代語意理解。在建立任何 Stage A task packet 或 dispatcher `--dry-run` **之前**，Sol 必須將該語意決定以 validator 執行：

   ```text
   python3 ${HERMES_HOME}/skills/note-taking/knowledge-inbox-capture/scripts/route_inbox_intent.py --text <raw-user-request> --model-intent <semantic-category>
   ```

   僅 active model 語意判為 `stage-a-inbox-only` 或 `stage-a-inbox-only-lightweight`，且 validator 通過時，才可建立 Stage A task boundary 或開始 Stage A；其他 category 都不得啟動 Stage A executor。不得用關鍵字、空白、大小寫、固定詞表或正則表達式自行取代模型對自然語言請求的意圖理解；validator 只負責驗證 category、來源存在性與輸出邊界。不得因 README 中提到 canonical source、staging、promotion、索引或 pipeline 而把模型已明確辨識的 Inbox-only request 改路由。validator 不得 fetch URL、讀取來源正文或依賴 filesystem state；其 canonical JSON 結果應直接保存為 packet 的 `intent_router_result` 行，而不是由 caller 重述或轉譯。Sol 在 dispatch 前不得擷取 URL 正文、把正文帶入 tool output，或對正文做語意審閱；只建立明確的 Stage A task boundary。若來源 material 的正文已在目前對話出現，Sol 必須如實揭露主 session 已接觸該正文，不得宣稱資訊隔離或零接觸。
2. **選定 Stage A executor。**若 active main brain 不高於 `GPT-5.6-luna max`，在 validator 通過後由主 session 依 task boundary 親自執行；若高於 `GPT-5.6-luna max`，由 active main brain 透過已配置且可驗證的 model dispatch path 指派精確的 `GPT-5.6-luna max` executor。不得使用 `run-role-worker.py --role terra`、Terra 或任何未經模型等級判定的替代 role 來處理 Stage A；若選定 executor 或 runtime 不可用，立即停止。
3. **Stage A task packet 是完整邊界。**packet 必須明示 `stage A`、精確一行 `intent_router_result: <category>`（category 只能是 `stage-a-inbox-only` 或 `stage-a-inbox-only-lightweight`）、唯一來源／artifact path、允許讀取範圍、選定的 Stage A executor 與其 provider/model、所需輸出格式、write allowlist 與 stop conditions。若需要指派 Luna Max，選定的 model dispatch path 必須先以相同 packet 做 dry-run；主腦直接執行時，也必須在開始來源取得前完成同樣的 boundary／model／allowlist 檢查。write allowlist **只能**是 `${KNOWLEDGE_ROOT}/inbox/` 內的單一 Markdown 絕對路徑；在 packet 中必須以唯一、無標題層級前綴的單行精確寫成 `write allowlist: ${KNOWLEDGE_ROOT}/inbox/<target-file>.md`，以通過機械 gate；**該行不可加上 Markdown 標題前綴（例如 `## `）或其他前綴。**不得包含 README、任何 audit artifact、索引或正式知識庫路徑。read allowlist 必須明確容納 duplicate preflight：允許只用 canonical URL 對 `${KNOWLEDGE_ROOT}/inbox/*.md` 做機械式精確搜尋，同時明示排除 README 指定的 frozen ZIP，且不得藉此語意閱讀其他文章。若選定 executor runtime 強制要求讀取 Agent OS canonical governance，task boundary 也須列入其實際必讀檔，避免治理要求與 read allowlist 自相矛盾。對 `stage-a-inbox-only-lightweight`，boundary 必須明確禁止來源 fetch、翻譯、摘要與心得，並把輸出限縮為單一 Markdown 的最低 metadata、使用者已提供的標題／描述、`日期`、可用的來源識別（有 URL 才寫 `來源網址`）與待後續完整 material capture 備註；不要把完整 capture 章節或來源完整性要求偷偷帶回 lightweight 模式。對 `stage-a-inbox-only` 才要求完整來源、翻譯與固定章節。
packet 缺漏、模糊或互相矛盾時，選定的 Stage A executor 必須停止且不寫入。
4. **Stage A executor 的權限。**選定的 executor 可自行取得完整來源、執行 deterministic rendering、完整翻譯、摘要／心得與固定格式組裝，並只建立 allowlist 指定的一份 Inbox Markdown。不得 promotion、分類、更新索引、改動正式知識庫、呼叫其他未授權角色、擴張 allowlist 或自我核准；也不得把 audit artifacts 放進 knowledge。
5. **嚴格停止，不得降級或偷換 executor。**選定 executor 不可用、Stage A model/provider/usage 任一驗證不符、存在未授權 fallback、來源不完整、來源已重複，或 Inbox README 契約無法明確判定時，立即停止並回報 blocker；不得改由 Terra、較低等級模型或其他未經模型等級判定的角色完成 Stage A。
6. **usage 與無 fallback 證據。**若由主腦直接執行，主 session 必須保存當下 active main brain 的可驗證模型身分、provider 與完成結果；若指派 `GPT-5.6-luna max`，必須保留該 exact model/provider、`completed: true`、`failed: false` 的 usage report。不能依啟動命令推定成功，也不能只因 runtime 綠燈就回報完成；沒有合格 artifact、存在 blocker 或 write allowlist 未命中時，必須以「未完成收錄」處理。來源取得的明示備援（例如 FxTwitter structured endpoint）不是模型 fallback，必須用不同詞彙清楚區分。usage/report 與其他 audit artifacts 不得寫入 `${KNOWLEDGE_ROOT}/`。
7. **只做 deterministic 收尾。**主 session 可以驗證 usage、YAML、檔案路徑、必要章節、block count 與原文精確比對，但不得另找模型重做選定 executor 的正文、翻譯、摘要或心得；選定 executor 必須自行完成並組裝固定章節順序。
8. **metadata 契約。**只有 Inbox README 明確支援 `capture_model` 時，才可在 frontmatter 寫入已驗證的 `provider/model`；README 未支援或契約不明時，不得擅增 frontmatter，模型 provenance 僅記錄在 knowledge 之外的 usage/report。

此模式的完成證據為：符合上述 selected-executor usage／無 fallback 驗證、單一 allowlisted Inbox 檔讀回、deterministic 結構與原文完整性驗證。若任一停止條件成立，沒有收錄檔即為正確結果。

## 固定完整收錄 SOP

### Stage A 修正／升級既有輕量檔

當 Roy 在一筆已完成的輕量 Inbox 收錄後，以預設的 material-to-Inbox 完整 capture 語意再次要求處理同一 material，或明確補充要求「全文、翻譯、摘要或心得」，這是**同一 material 的完整化升級**，不是新來源，也不是建立第二份檔案；依本節的 rollback 程序原地升級。

1. Roy 的一般 material-to-Inbox 完整 capture 意圖本身即包含完整 capture；只有當下訊息明確要求保留輕量／只留連結等例外時，才維持 lightweight。不必要求 Roy 另外使用「原地升級／覆寫既有輕量檔」字樣，但必須遵守後續備份、單一 allowlist 與失敗還原程序。
2. 只讀取指定的既有目標檔，機械驗證它確實是同一 material／穩定來源識別、`status: new` 的輕量檔，且內容是本 skill／本次流程建立的輕量投遞；不得對 Inbox 做遞迴搜尋，也不得觸碰 no-touch 子目錄或 Frozen ZIP。
3. 在建立 packet 前，把既有檔案移到 `${HERMES_AUDIT_ROOT}/knowledge-inbox/` 下的 rollback backup，確認原目標路徑不存在；backup 不得列入 worker 的 read allowlist，也不得讓 worker 讀取或修改。這是為了讓唯一的 `write allowlist` 仍是同一路徑、同一份最終 Markdown，而非新增 `-full`、`-v2` 或第二份來源檔。
4. packet 必須明示目前語意判定已授權這次 in-place upgrade（預設完整 material capture 或當下明確完整化要求皆可）；不要求 Roy 使用固定「in-place upgrade」短語。選定的 Stage A executor 只寫回原本的單一 allowlisted path。不要把 backup、packet 或 usage report 放進 knowledge。
5. 若選定 executor 停止、usage 雖綠燈但沒有合格 artifact、或 deterministic 驗證失敗，立即用 rollback backup 還原原輕量檔，並回報「完整升級未完成」；不得留下半成品或把摘要／部分翻譯當完整 capture。
6. 只有在完整 Markdown、原文機械比對、翻譯範圍、摘要／心得與 usage 都驗證通過後，才能刪除 rollback backup 與本次 packet；usage audit 應保留在 knowledge 之外。

詳細的 backup、失敗還原與清理順序見 `references/in-place-lightweight-upgrade.md`。

長文批次 Stage A、selected executor contract、rollback 與主 session deterministic 驗證的具體 packet／驗證模式見 `references/long-article-batch-translation.md`。

### 0. 明確指定的輕量 Inbox 投遞 SOP（`stage-a-inbox-only-lightweight`）

本分支只在 Roy 當下訊息的自然語意明確要求輕量、只留連結／metadata、不要抓正文、不要翻譯、不要摘要或等價做法時使用；若整則請求屬於預設的 material-to-Inbox 完整 capture，本分支不適用。

1. 只使用 Roy 當下訊息已提供的標題／描述與可用的來源識別；不 fetch 原文，不把預覽或附件卡片當成已驗證正文。
2. 依 README 建立一份 `status: new` Markdown，至少保留 `title`、`captured`、`kind`、可用時的 `source_url`、`status`，以及 `日期`、可用的來源識別與輕量備註。
3. 備註必須明示「待後續完整 material 擷取／翻譯／摘要」或等價語意；不得建立空洞的 `原文`、`中文翻譯`、`Vani 摘要` 或 `Vani 心得與延伸見解` 章節來製造完整感。
4. 收尾只驗證 YAML、標題、日期、可用的來源識別、`status: new` 與單一檔案；usage 綠燈仍須搭配檔案 read-back，不能單靠 worker 自述。
5. 完成後回報「已輕量收錄，尚未擷取完整 material／翻譯／摘要」，不要把這筆資料描述成完整 capture。

### 1. 來源取得與完整性確認

1. 若 Roy 已直接貼出 material，將整個提供內容視為來源，完整保留，不得只擷取其中摘要；若有原始網址，優先讀取原始網址，不要用搜尋摘要取代來源正文。
2. 若來源是文章，取得完整文章，包括標題、作者（若來源有提供）、正文、標題層級、清單、程式碼、引文、連結與有內容意義的圖片位置；若來源是文件、摘錄、想法或其他 material，取得／保留其全部可用內容與結構。
3. 若一般頁面只顯示預覽、登入牆或空白內容，改用適合該來源的結構化資料、官方 API 或公開擷取介面。X Article 依 `references/x-article-structured-capture.md` 處理。
4. 對文件網站先探測官方 Markdown 表示法，再解析大型 HTML：可嘗試原網址加 `.md`，或以 `Accept: text/markdown` 請求原網址；必須確認 HTTP 成功、`Content-Type` 確為 Markdown，且正文標題與目標頁一致。這是同一官方來源的內容協商，不是搜尋摘要。
5. 在 Stage A 的單一輸出 allowlist 下，來源取得與 renderer 暫存資料必須留在記憶體或由 pipe 串接；不得在 `/tmp`、工作目錄、knowledge 或其他路徑建立 HTML、JSON、圖片、manifest、cache 或任何其他暫存檔。若某個取得方式必須落盤，改用不落盤的結構化請求方式或停止回報 blocker，不得擴張 write allowlist。
6. 若仍無法取得全文，停止並明確回報缺少哪一部分；不得把摘要、片段或自行補寫的文字冒充完整原文。
7. 記錄來源區塊數、來源字元數或其他可檢查的完整性基準，確保每個來源區塊都被走訪。

**完成條件：**已取得足以重建完整 material 的來源內容，或已誠實回報無法完整取得。

### 2. 重複與安全 preflight

1. 以 canonical URL 或 material 的穩定識別資訊搜尋 Inbox，避免不知情地重複收錄；duplicate preflight 必須限定在 Inbox 根目錄的 `*.md`，採非遞迴、機械式精確比對。不要對整個 `${KNOWLEDGE_ROOT}/inbox/` 做遞迴搜尋或列舉，避免碰觸受保護子目錄。
2. `${KNOWLEDGE_ROOT}/inbox/gpt-message-import-abandon/` 與 `${KNOWLEDGE_ROOT}/inbox/gpt-message-import-pending/` 是 Roy 指定的 no-touch 範圍：不得讀取、列舉、搜尋、雜湊、搬移、分類、驗證或修改。
3. 不讀取或處理 Inbox README 指定凍結、排除或禁止開啟的檔案；尤其不得開啟、列舉或處理 Frozen ZIP。
4. 不把憑證、token、私密個資或登入資料寫進收錄檔。
5. 若已有同一 material 的完整 capture，先停下回報既有檔案，不自行覆寫或建立第二份；若已有同一 material 的 lightweight intake，且當下請求的語意是預設完整 capture，依「Stage A 修正／升級既有輕量檔」流程處理；若當下明確指定 lightweight，才保持現狀。

**完成條件：**確認沒有既有同一 material／來源檔，且來源可安全保存。

### 2A. 重複訊息與已完成投遞

同一 material／來源的重複訊息（例如 Slack 重送、thread 重播，或 Roy 再次提供相同 material）不是新的 capture 工作：

1. 先以 canonical URL 或 material 的穩定識別資訊做 Inbox 根目錄、非遞迴的機械式 duplicate preflight；若已知上次的 allowlisted target，也可只讀回該單一檔案確認來源與 `status`。
2. 若已存在同一 material 的完整 capture，停止啟動 Stage A executor、不要重新 fetch、不要覆寫，也不要建立 `-v2`、`-full` 或其他第二份檔案；回報既有的精確路徑與目前狀態即可。
3. 若既有檔是 lightweight，而當下訊息的自然語意是預設完整 material-to-Inbox capture，依預設完整 capture 規則進入「Stage A 修正／升級既有輕量檔」流程；只有當下明確指定 lightweight，才保持現狀。

這個分支的完成條件是：確認既有同一 material 的檔案仍可讀、未產生第二份檔案，且沒有不必要的 worker 或來源擷取副作用。

### 3. 語言判斷與翻譯

1. 若原文已是自然的台灣正體中文，不另做翻譯，也不建立 `中文翻譯` 章節。
2. 若原文不是台灣正體中文，完整翻譯成自然、準確的台灣正體中文。
3. 翻譯範圍包含所有實質正文、標題、清單、引文、程式碼註解、圖說與提示文字；程式碼本體、URL、專有名詞及必要技術術語依語意保留。
4. 保留原始段落、順序、標題層級、連結、程式碼區塊與媒體位置，不得只翻譯摘要或擅自刪節。
5. 若圖片內有決策相關且正文沒有的文字，實務可行時 OCR 並翻譯；未 OCR 時必須明確註明「翻譯涵蓋正文，圖片內文字未另行翻譯」，不得宣稱圖片文字也已完整翻譯。
6. 若來源 material 是長文或含有大量 blocks，不能僅因篇幅或 block 數量高就停止或改寫成摘要；應以 deterministic renderer 保留全部原文，再由選定的 Stage A executor 分段、逐段完成翻譯並回填固定章節。對超過 200 個 blocks 或 20,000 個字元的文章，**選定的 Stage A executor** 必須按來源順序採批次執行：處理明確的 block range，必要時縮小 batch 後繼續，並由同一 executor 組裝同一個 allowlisted 最終檔；不得中途改派 Terra 或其他模型。block count、字元數或「無法可靠完成」的自我判斷本身都不是合法 stop reason。只有來源實際不完整、翻譯／context／output 有具體可重現的技術錯誤，且已依較小 batch 重試仍失敗，或其他明列 stop condition 成立時，才停止且不寫入；blocker 回報必須附具體錯誤、已處理的 range 與已嘗試的 batch 大小。

**完成條件：**非台灣正體中文的所有實質文字均有對應翻譯；任何未涵蓋範圍都已揭露。

### 4. 吸收後摘要與心得

完整理解全部 material 後再撰寫，不能只根據標題、預覽或前幾段推測。

`Vani 摘要` 至少要：

- 提煉來源 material 的核心主張、結構與主要結論；若是想法、摘錄或備忘，說清楚其脈絡與原始目的；
- 區分「來源聲稱」與已知事實，不把來源主張寫成已查證結果；
- 讓沒有讀完整來源 material 的人也能掌握重點。

`Vani 心得與延伸見解` 至少要：

- 說明最值得吸收與實務採用的觀點；
- 指出可能過度簡化、證據不足、適用範圍或需要保留懷疑之處；
- 連結到 Roy 的工作情境、工程實務或可採取的下一步，但不要為了湊字數做空泛延伸；
- 明確區分來源 material 與 Vani 自己的判斷。

**完成條件：**摘要忠實、心得有辨識度，且沒有把個人推論偽裝成原文內容。

### 5. 建立單一 Inbox Markdown

檔名遵循 README，通常為：

```text
YYYY-MM-DD-short-slug.md
```

metadata 僅使用 README 支援的欄位；`kind` 依 material 類型填寫 `url`、`document`、`idea` 或 `excerpt`。有來源網址才寫 `source_url`；無網址時省略。文章 URL 的典型 metadata 為：

```yaml
---
title: 原始標題或清楚的中文標題
captured: YYYY-MM-DD
kind: url
source_url: https://example.com/canonical-url
status: new
---
```

完整 capture 的內容採用以下**固定格式與順序**；文章、文件、摘錄、想法或其他 material 都必須保留完整提供內容，非文章 material 可依其性質調整日期／來源欄位，但不得省略原始內容、摘要或說明：

```markdown
# 標題

## 日期
- 收錄日期：YYYY-MM-DD
- 原文發布日期：來源有明示時填寫；沒有則寫「來源未標示」，不得猜測

## 來源網址
https://example.com/canonical-url

## 中文翻譯
僅在原文不是台灣正體中文時出現，放入完整翻譯。

## 原文
完整原文，不濃縮、不改寫、不截斷。

## Vani 摘要
忠實摘要。

## Vani 心得與延伸見解
吸收後的判斷、保留意見與實務延伸。
```

固定要求：

- `日期` 每次完整 capture 都必須有；有來源 URL 時必須有 `來源網址`，無 URL 時省略 `source_url`，改以清楚的 `來源` 描述 material，不得虛構 URL。
- `中文翻譯` 是條件式章節：原文不是台灣正體中文時必須有；原文已是台灣正體中文時不建立此章節。
- `原文`、`Vani 摘要`、`Vani 心得與延伸見解` 每次完整 capture 都必須有。
- 作者與原文標題可附在標題下方或原文前，但來源沒有明示時省略，不得猜測。
- 有 `source_url` 時，使用去除追蹤參數後仍可識別原文的 canonical URL；不確定時保留 Roy 提供的原始網址。

**完成條件：**只產生一個可讀的 Inbox Markdown，`status: new`，固定章節齊全，條件式翻譯規則正確。

### 6. 輕量驗證與收尾

1. 讀回檔案開頭，確認 YAML 與標題正確。
2. 完整 capture 確認 `日期`、有 URL 時的 `來源網址`（無 URL 時的 `來源`）、`原文`、`Vani 摘要`、`Vani 心得與延伸見解` 一定存在；lightweight 確認最低 metadata、可用的來源識別與待整理備註。
3. 完整 capture 若原文不是台灣正體中文，確認 `中文翻譯` 存在且涵蓋全部實質內容；若原文已是台灣正體中文，確認沒有多餘的翻譯章節。lightweight 不執行來源語言或翻譯完整性宣稱。
4. 只有完整 capture 才將收錄檔 `## 原文` 與 `## Vani 摘要` 之間的內容抽出，依同一個明確的邊界正規化規則（通常只去除區段首尾空白）與擷取來源做機械式精確比對；若不相等，先修復，不得只憑字數或人工掃讀宣稱完整。多篇批次可用同一支短驗證腳本逐篇檢查。
5. 若使用結構化 block rendering，確認所有來源 blocks 都已走訪；未知 block 必須保留明確 placeholder 或解析後補回。
6. 清除本次產生的暫存檔，只留下最終 Inbox Markdown。
7. 回報精確路徑、翻譯範圍、原文完整性，以及「尚未整理或進入正式知識庫」。

對單次、可逆的 material capture，完成上述一次 read-back、選定 Stage A executor 的模型／provider／完成證據驗證即可；不要啟動額外的多代理語意審查、hash pipeline、分類器或 promotion 流程。

## X Article Note

X 貼文正文可能只有 `t.co` 連結，真正內容在 X Article 的結構化 payload。此時不得把空貼文或預覽文字當成全文；應依 `references/x-article-structured-capture.md` 走訪 blocks、entityMap、媒體與嵌入貼文，按來源順序 deterministic rendering。

可使用 `scripts/render_fxtwitter_x_article.py` 將 FxTwitter status JSON deterministic rendering 成原文 Markdown 與 manifest：

```text
python3 scripts/render_fxtwitter_x_article.py payload.json article.md manifest.json
```

renderer 只負責完整、可重現的來源投影，不負責翻譯、摘要或事實查證。X Article 偶爾會出現沒有 `entityRanges`、沒有文字與資料的空 `atomic` block；不得自行推測其內容，應保留 `[Unresolved block: atomic entity=missing]` placeholder，並在翻譯範圍說明中揭露。完成後仍須依第 6 節，把最終檔的 `## 原文` 與 renderer 產物做精確比對。

## Common Pitfalls

1. **把 Inbox capture 當正式入庫：** Inbox 只是待整理入口，不得直接 promotion。
2. **只有翻譯或摘要，沒有完整原文：** Roy 的固定格式要求保留完整原文。
3. **原文非台灣正體中文卻未完整翻譯：**不得用重點翻譯冒充全文翻譯。
4. **圖片或程式碼被遺漏：**保留媒體位置、程式碼與有意義的圖說；未翻譯圖片內文字要揭露。
5. **用搜尋摘要取代來源：**搜尋結果只能協助定位，不能證明原文內容。
6. **心得只是重述摘要：**心得要包含適用邊界、疑點與實務判斷。
7. **自行猜 metadata：**作者、日期、標題等只採來源可支持的資訊。
8. **留下暫存副本：**完成後 Inbox 只留下最終收錄檔。
9. **把不同層級的限制混稱：**回報 blocker 時要指出它來自哪一層：Inbox README 儲存契約、capture skill SOP、selected-executor 的機械 gate，或 selected executor 的具體 runtime/tool error。不得把 executor 的自我判斷說成 SOP 禁止，也不得說 SOP 不允許分段處理，若 SOP 本身明確要求分段處理。
10. **把一般 Inbox material capture 誤判成輕量：**只要 active model 依整則請求的自然語意判斷 Roy 要把貼給 Vani 的 material 轉換到 Inbox，預設就是完整內容、必要翻譯、摘要與說明；不得用字串、固定短語或正則判斷；只有 Roy 當下明確指定輕量做法時，才可建立最低 metadata 投遞。

## Verification Checklist

- [ ] 已讀取當下的 Inbox README
- [ ] 已檢查同來源是否重複
- [ ] 若為 `stage-a-inbox-only`，已從直接來源取得完整 material；若為 lightweight，確認未擅自 fetch／宣稱完整來源
- [ ] 每次完整 capture 都有 `日期`；有 URL 時有 `來源網址`，無 URL 時有清楚的來源識別
- [ ] 若為完整 capture：非台灣正體中文內容已完整翻譯；台灣正體中文原文未建立多餘翻譯章節
- [ ] 完整 capture 的 Stage A executor 符合模型政策：主腦等級不高於 `GPT-5.6-luna max` 時由主腦完整處理；主腦更高時有 `GPT-5.6-luna max` 的指派與完成證據；不得使用 Terra
- [ ] 若為完整 capture：`原文`、`Vani 摘要`、`Vani 心得與延伸見解` 固定存在；若為 lightweight，確認只保留最低 metadata 與待整理備註
- [ ] YAML 與檔名符合 Inbox 契約
- [ ] `status: new`
- [ ] 只有一個最終 Markdown，無本次暫存檔
- [ ] 未建立 canonical source、分類、更新索引或 promotion
- [ ] 已回報精確路徑與未進正式知識庫
