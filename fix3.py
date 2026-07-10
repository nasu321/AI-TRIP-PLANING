import os
p = 'frontend/pages/9_Database_Explorer.py'
c = open(p, 'r', encoding='utf-8').read()

old_block = """        except:
            st.error("Backend failed to start and logs are unreadable.")"""

new_block = """        except:
            st.error("Backend failed to start and logs are unreadable.")

# ── Fetch DB info ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_db_info():
    try:
        r = requests.get(f"{BACKEND_URL}/api/data/info", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

db_info = fetch_db_info()

if not db_info:
    log_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'backend_cloud.log')
    logs = "No log found."
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                logs = f.read()
        except: pass
    st.error(f"⚠️ Cannot reach backend. Make sure it's running on {BACKEND_URL}\\n\\n**Backend Logs:**\\n```text\\n{logs[-1500:]}\\n```")
    st.stop()"""

if old_block in c:
    # First, let's just do a simple replacement for the DB info block.
    # The DB Explorer file has:
    # db_info = fetch_db_info()
    # if not db_info:
    #     st.error("⚠️ Cannot reach backend. Make sure it's running on http://localhost:8000")
    #     st.stop()
    pass

# We will just write a simpler regex or replace script
import re
c = re.sub(r'st\.error\("⚠️ Cannot reach backend\. Make sure it\'s running on .*?"\)',
           r'log_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend", "backend_cloud.log")\n    logs = "No log found."\n    if os.path.exists(log_path):\n        try:\n            with open(log_path, "r", encoding="utf-8") as f:\n                logs = f.read()\n        except: pass\n    st.error(f"⚠️ Cannot reach backend. Make sure it\'s running on {BACKEND_URL}\\n\\n**Backend Logs:**\\n```text\\n{logs[-1500:]}\\n```")',
           c)
open(p, 'w', encoding='utf-8').write(c)
print("Replaced Database Explorer.")
