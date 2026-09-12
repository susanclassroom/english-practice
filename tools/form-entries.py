#!/usr/bin/env python3
"""
從 Google 表單的公開網址抓出題目與 entry 代號，直接印成可以貼進練習頁的設定區塊。

用法：
    python3 tools/form-entries.py "https://docs.google.com/forms/d/e/XXXX/viewform"

表單網址從「傳送 → 連結」那裡複製即可（不是 /edit 編輯網址，那個要登入抓不到）。
複製別的表單產生的副本，entry 代號會重新產生，所以每建一份新表單就重跑一次。
"""
import json
import re
import sys
import urllib.request

# 練習頁 GFORM.f 的七個鍵，對應表單題目的順序
KEYS = ["seat", "lesson", "stage", "right", "total", "wrong", "hw"]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return r.geturl(), r.read().decode("utf-8", "replace")


def check_open(final_url, html):
    """學生不會登入 Google，所以表單一定要「任何人都能填」。
    需要登入的表單，學生按送出不會有錯誤訊息（no-cors 拿不到回應），
    紀錄卻一筆都收不到——這是最難發現的失敗，所以先擋在這裡。"""
    if "accounts.google.com" in final_url or "ServiceLogin" in final_url:
        sys.exit(
            "✗ 這份表單需要登入才能填。\n"
            "  學生不會登入，送出會靜靜地失敗，你在試算表裡一筆都看不到。\n"
            "  修法：開啟表單 → 設定（齒輪）→ 回覆 →\n"
            "        關閉「限制為 <機構> 使用者」與「收集電子郵件地址」。\n"
            "  用學校或機關的 Google Workspace 帳號建表單時，這兩項常常預設是開的。")
    if "FB_PUBLIC_LOAD_DATA_" not in html:
        sys.exit("✗ 這一頁看起來不是公開的表單。確認網址是「傳送 → 連結」複製到的那個。")


def parse(html):
    m = re.search(r"FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.*?\]);\s*</script>", html, re.S)
    if not m:
        sys.exit("這一頁找不到表單資料。確認網址是公開的 viewform 連結，不是 /edit。")
    data = json.loads(m.group(1))
    title = data[3] if len(data) > 3 else "(無標題)"
    out = []
    for item in data[1][1]:
        name = item[1]
        for field in (item[4] or []):
            out.append((name, "entry.%s" % field[0]))
    return title, out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    url = sys.argv[1].split("?")[0]
    if url.endswith("/edit"):
        sys.exit("這是編輯網址，抓不到。請用「傳送 → 連結」那個 viewform 網址。")
    final_url, html = fetch(url)
    check_open(final_url, html)
    title, fields = parse(html)
    print("✓ 不需要登入就能填，學生送得出去\n")
    print("表單：%s" % title)
    print("題目數：%d\n" % len(fields))
    for name, entry in fields:
        print("  %-14s %s" % (name, entry))

    if len(fields) != len(KEYS):
        print("\n⚠ 題目數不是 %d 題，請確認表單結構跟其他練習一致再接。" % len(KEYS))
        return

    post = url.rsplit("/", 1)[0] + "/formResponse"
    print("\n可以直接貼進練習頁的設定區塊：\n")
    print("const GFORM = {")
    print('  url: "%s",' % post)
    print("  f: { " + ", ".join(
        '%s:"%s"' % (k, e) for k, (_n, e) in zip(KEYS, fields)) + " }")
    print("};")


if __name__ == "__main__":
    main()
