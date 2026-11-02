# -*- coding: utf-8 -*-
"""用本机 Chrome 无头模式做 HTML 版面审计：越界 / 文本重叠。"""

import json
import os
import re
import subprocess

import build_preview as B
import deck_content as C

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SHOTS = os.path.join(HERE, "shots")

AUDIT_JS = r"""
<script>
window.addEventListener('load', function () {
  var out = [];
  var slide = document.querySelector('.slide');
  var sr = slide.getBoundingClientRect();
  var texts = [];
  document.querySelectorAll('.slide .txt, .slide img, .slide .card').forEach(function (el) {
    var r = el.getBoundingClientRect();
    var tag = el.tagName + '.' + (el.className || '').replace(/\s+/g, '.');
    if (r.left < sr.left - 1 || r.top < sr.top - 1 || r.right > sr.right + 1 || r.bottom > sr.bottom + 1) {
      out.push('OUT:' + tag + ':' + el.textContent.slice(0, 14) + ':' +
        [r.left - sr.left, r.top - sr.top, r.right - sr.right, r.bottom - sr.bottom].map(Math.round).join(','));
    }
    if (el.classList.contains('txt')) {
      texts.push([el, r]);
      if (el.scrollHeight > el.clientHeight + 3) {
        out.push('CLIP:' + el.textContent.slice(0, 14) + ':' + el.scrollHeight + '/' + el.clientHeight);
      }
    }
  });
  for (var i = 0; i < texts.length; i++) {
    for (var j = i + 1; j < texts.length; j++) {
      var a = texts[i][1], b = texts[j][1];
      var ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
      var oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (ox > 2 && oy > 2) {
        out.push('OVERLAP:' + texts[i][0].textContent.slice(0, 10) + '|' +
          texts[j][0].textContent.slice(0, 10) + ':' + Math.round(ox) + 'x' + Math.round(oy));
      }
    }
  }
  document.body.setAttribute('data-audit', out.length ? out.join(' ;; ') : 'OK');
});
</script>
"""


def main():
    os.makedirs(SHOTS, exist_ok=True)
    failed = 0
    for page in C.PAGES:
        n = page["n"]
        html = B.render([n]).replace("</body>", AUDIT_JS + "</body>")
        path = os.path.join(SHOTS, f"audit-{n}.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        url = "file:///" + os.path.abspath(path).replace("\\", "/")
        proc = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--virtual-time-budget=1500", "--dump-dom", url],
            capture_output=True, timeout=90,
        )
        dom = proc.stdout.decode("utf-8", errors="replace")
        match = re.search(r'data-audit="([^"]*)"', dom)
        result = match.group(1).replace("&quot;", '"') if match else "NO-AUDIT"
        status = "OK" if result == "OK" else "FAIL"
        if status == "FAIL":
            failed += 1
        print(f"P{n:02d}  {status}  {result}")
        if status == "FAIL":
            print("     dom-bytes:", len(dom), "stderr:", proc.stderr.decode("utf-8", "replace")[:200])
    print(f"\n{len(C.PAGES)} 页审计完成，异常页 {failed} 页")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()