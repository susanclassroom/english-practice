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
        return r.read().decode("utf-8", "replace")


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
    title, fields = parse(fetch(url))
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
