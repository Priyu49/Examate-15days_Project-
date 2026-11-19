import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE) if os.path.basename(HERE).lower() == "ui" else HERE
os.chdir(ROOT)
sys.path.insert(0, ROOT)

try:
    from streamlit import runtime
    if runtime.exists():
        print("Run this with `python verify_project.py`, not `streamlit run`.")
        sys.exit(1)
except ImportError:
    pass

passed = failed = 0


def report(ok, name, hint=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"PASS  {name}")
    else:
        failed += 1
        print(f"FAIL  {name}")
        if hint:
            print(f"      -> {hint}")


def section(title):
    print(f"\n== {title} ==")


UI_FILES = [p for p in ("ui/mitramaati_ui.py", "ui/app.py") if os.path.exists(p)]
CORE = ["main.py", "app/graph.py", "app/tools.py", "app/agent_loop.py", "test_graph.py",
        "data/records.json", "requirements.txt"]

section("1. Files exist")
for f in CORE:
    report(os.path.exists(f), f, f"missing in {ROOT}")
report(bool(UI_FILES), "UI file (ui/app.py or ui/mitramaati_ui.py)", "no UI file found")

section("2. Python syntax and pasted junk")
for f in [x for x in CORE if x.endswith(".py")] + UI_FILES:
    if not os.path.exists(f):
        continue
    src = open(f, encoding="utf-8").read()
    try:
        compile(src, f, "exec")
        report(True, f"{f} compiles")
    except SyntaxError as e:
        first = src.splitlines()[0] if src else ""
        report(False, f"{f} compiles", f"line {e.lineno}: {e.msg}. First line is: {first!r} "
                                       "(delete stray text copied from the chat)")
for f in UI_FILES:
    src = open(f, encoding="utf-8").read()
    report("== 1. Files exist ==" not in src, f"{f} is not the check script",
           "this file contains the check script; restore the real UI code")

section("3. Packages installed")
import importlib.util
for pkg in ("fastapi", "langgraph", "streamlit", "requests", "httpx", "pytest"):
    report(importlib.util.find_spec(pkg) is not None, pkg, f"pip install {pkg}")

section("4. requirements.txt")
req = open("requirements.txt", encoding="utf-8").read().lower() if os.path.exists("requirements.txt") else ""
for pkg in ("langgraph", "streamlit"):
    report(pkg in req, f"{pkg} in requirements.txt", f"add a line: {pkg}")

section("5. records.json")
try:
    recs = json.load(open("data/records.json", encoding="utf-8"))
    report(len(recs) == 12, f"{len(recs)} soil parameters (expected 12)")
    need = {"parameter_name", "unit", "low_below", "high_above", "what_it_means", "source_url"}
    bad = [r.get("parameter_name") for r in recs if not need <= set(r)]
    report(not bad, "every record has the required fields", f"missing fields in: {bad}")
except Exception as e:
    report(False, "records.json readable", str(e))

section("6. Unit tests")
r = subprocess.run([sys.executable, "-m", "pytest", "test_graph.py", "-q"],
                   capture_output=True, text=True, cwd=ROOT)
report(r.returncode == 0, "pytest test_graph.py", (r.stdout + r.stderr)[-600:])

section("7. API end-to-end (in-process)")
fb = os.path.join("data", "feedback.jsonl")
fb_before = os.path.getsize(fb) if os.path.exists(fb) else None
try:
    from fastapi.testclient import TestClient
    import main
    c = TestClient(main.app)
    report(c.get("/health").status_code == 200, "GET /health")

    vals = {r["parameter_name"]: 1.0 for r in recs}
    sc = c.post("/soil-card", json={"values": vals})
    report(sc.status_code == 200 and len(sc.json()["tiles"]) == 12, "POST /soil-card returns 12 tiles")

    t = "verify-project-thread"
    a1 = c.post("/agent", json={"query": "classify nitrogen 200", "thread_id": t}).json()
    report(a1.get("status") == "pending_approval", "/agent pauses for approval")
    a2 = c.post("/agent", json={"thread_id": t, "approve": True}).json()
    report(a2.get("status") == "done" and a2.get("approved") is True, "/agent resumes on approve")
    a3 = c.post("/agent", json={"query": "classify nitrogen 300", "thread_id": t}).json()
    report(a3.get("turns_remembered") == 2, "/agent remembers earlier turns")

    ask = c.post("/ask", json={"question": "What does low phosphorus mean?", "top_k": 3})
    report(ask.status_code == 200, "POST /ask")

    bad = c.post("/feedback", json={"question": "q", "answer": "a", "rating": "meh"})
    report(bad.status_code == 400, "/feedback rejects a bad rating")
except Exception as e:
    report(False, "API end-to-end", f"{type(e).__name__}: {e}")
finally:
    # keep test data out of the repo
    if os.path.exists(fb) and fb_before is None:
        os.remove(fb)

section("8. Streamlit UI loads without errors")
if UI_FILES:
    try:
        from streamlit.testing.v1 import AppTest
        path = os.path.join(ROOT, UI_FILES[0].replace("/", os.sep))
        at = AppTest.from_file(path, default_timeout=60).run()
        report(not at.exception, f"{UI_FILES[0]} loads",
               "; ".join(str(e.value) for e in at.exception) if at.exception else "")
    except Exception as e:
        report(False, "Streamlit UI", f"{type(e).__name__}: {e}")
else:
    report(False, "Streamlit UI", "no UI file")

total = passed + failed
print(f"\n{passed}/{total} checks passed.")
print("All good, you can commit." if failed == 0 else "Fix the FAIL lines above, then run this again.")
sys.exit(0 if failed == 0 else 1)
