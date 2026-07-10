import os
p = 'frontend/pages/1_Plan_Trip.py'
c = open(p, 'r', encoding='utf-8').read()

old_block = """        except requests.exceptions.ConnectionError:
            st.error(
                "❌ Cannot connect to backend. Make sure the FastAPI server is running:\\n\\n"
                "`cd backend && uvicorn app.main:app --reload --port 8505`"
            )"""

new_block = """        except requests.exceptions.ConnectionError:
            log_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'backend_cloud.log')
            logs = "No log found."
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8") as f:
                        logs = f.read()
                except: pass
            st.error(f"❌ Cannot connect to backend. The backend auto-launcher failed or is still starting up.\\n\\n**Backend Logs:**\\n```text\\n{logs[-1500:]}\\n```")"""

if old_block in c:
    c = c.replace(old_block, new_block)
    open(p, 'w', encoding='utf-8').write(c)
    print("Replaced old block.")
elif new_block in c:
    print("Already has new block.")
else:
    print("Could not find old block.")
