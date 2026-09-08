#!/usr/bin/env python3
"""homerepairledger.com 의 sitemap.xml 을 읽어 ?m=1 URL 목록(sitemap-m1.txt)을 만든다.

왜: 블로거는 Googlebot-스마트폰을 글 URL 에서 ?m=1 로 302 시키는데, 구글이 그 302 를
못 따라가 "리디렉션 오류"를 낸다. ?m=1 URL 을 직접 주면 색인된다(2026-09-07 실측).
블로그 자체 sitemap.xml 은 깨끗한 URL 만 적으므로 여기서 ?m=1 을 붙인다.

원칙:
- 가져오기에 실패하면 파일을 건드리지 않는다 (좋은 파일을 빈 파일로 덮지 않는다).
- 종료코드는 항상 0 — 예약 실행이 실패 메일을 보내지 않게 한다.
"""
import re
import sys
import urllib.request

SRC = "https://www.homerepairledger.com/sitemap.xml"
OUT = "sitemap-m1.txt"
POST = re.compile(r"^https://www\.homerepairledger\.com/20\d\d/\d\d/[^/?#]+\.html$")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "hrl-sitemap/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def locs(xml: str) -> list[str]:
    return [u.strip() for u in re.findall(r"<loc>\s*([^<]+?)\s*</loc>", xml)]


def main() -> int:
    try:
        xml = fetch(SRC)
        urls = []
        if "<sitemapindex" in xml:
            for sm in locs(xml):
                urls += locs(fetch(sm))
        else:
            urls = locs(xml)
    except Exception as e:
        print(f"fetch failed, leaving {OUT} untouched: {e!r}")
        return 0
    posts: list[str] = []
    for u in urls:
        if POST.match(u) and u not in posts:
            posts.append(u)
    if not posts:
        print(f"no post urls in {SRC}, leaving {OUT} untouched")
        return 0
    text = "\n".join(u + "?m=1" for u in posts) + "\n"
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"{len(posts)} urls -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
