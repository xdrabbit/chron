import sys
from PyPDF2 import PdfReader

pdf = sys.argv[1]
expected = sys.argv[2] if len(sys.argv) > 2 else None

text = ""
r = PdfReader(pdf)
for p in r.pages:
    try:
        text += p.extract_text() or ""
    except Exception:
        pass

if expected:
    ok = (expected in text)
    print(f"Footer contains '{expected}': {ok}")
    sys.exit(0 if ok else 1)
else:
    # print tail for manual inspection
    print(text[-500:])
