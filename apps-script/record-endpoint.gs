/**
 * 單字練習紀錄收集器（Google Apps Script）
 * ------------------------------------------------------------
 * 用途：讓練習頁把每一筆作答紀錄直接寫進「這一份試算表」，
 *       而且送出成功與否，學生的畫面看得到、老師的資料不會默默掉。
 *
 * 怎麼用（約 3 分鐘，只有你能做，因為要用你的 Google 帳號）：
 *  1. 新建一份 Google 試算表，命名例如「單字庫練習紀錄」
 *  2. 上方選單「擴充功能」→「Apps Script」
 *  3. 把編輯器裡原本的內容全部刪掉，貼上這整個檔案，存檔
 *  4. 右上「部署」→「新增部署作業」→ 類型選「網頁應用程式」
 *       執行身分：我（你自己的帳號）
 *       access  ：知道連結的任何人（Anyone）    ← 一定要選這個
 *  5. 部署完會給你一個 .../exec 結尾的網址，把那個網址給我
 *
 * 之後每次改這支程式，記得要「部署 → 管理部署作業 → 編輯 → 版本：新版本」，
 * 否則線上跑的還是舊版。
 */

const SHEET_NAME = '練習紀錄';
const HEADERS = ['時間', '座號', '課次', '階段', '答對', '題數',
                 '完成狀況', '本回合錯的字', '累計還沒過的字', '作業狀態'];

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    // 全班同時送出時排隊寫入，避免兩筆搶同一列
    lock.waitLock(20000);
    const d = JSON.parse(e.postData.contents);
    sheet_().appendRow([
      new Date(),
      d.seat || '',
      d.lesson || '',
      d.stage || '',
      d.right,
      d.total,
      d.finished ? '做完整回合' : '沒做完就離開',
      d.roundWrong || '',
      d.leftWords || '',
      d.hw || ''
    ]);
    return out_({ ok: true });
  } catch (err) {
    return out_({ ok: false, error: String(err) });
  } finally {
    try { lock.releaseLock(); } catch (ignore) {}
  }
}

/* 用瀏覽器直接打開 /exec 網址時會看到這個，用來確認部署成功 */
function doGet() {
  return out_({ ok: true, msg: '紀錄收集器運作中' });
}

function sheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEADERS);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  return sh;
}

function out_(o) {
  return ContentService.createTextOutput(JSON.stringify(o))
    .setMimeType(ContentService.MimeType.JSON);
}
