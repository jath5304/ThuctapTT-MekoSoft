import subprocess
import sys
import time
import os

# Đảm bảo UTF-8 cho Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

print("""
======================================================================
   HE THONG DEMO SINGLE SIGN-ON (SSO) & SINGLE LOGOUT (SLO)
                    Mo hinh chuan 3 thanh phan
======================================================================
1. Identity Provider (IdP) : http://localhost:5000 (MekoID)
2. Service Provider 1 (SP1): http://localhost:5001 (Moodle LMS)
3. Service Provider 2 (SP2): http://localhost:5002 (MekoBook Reader)
======================================================================
""")

current_dir = os.path.dirname(os.path.abspath(__file__))

procs = []
try:
    print("[1/3] Khoi dong MekoID IdP Server (:5000)...")
    p1 = subprocess.Popen([sys.executable, os.path.join(current_dir, "idp_server.py")])
    procs.append(p1)
    time.sleep(1)

    print("[2/3] Khoi dong Moodle LMS App (:5001)...")
    p2 = subprocess.Popen([sys.executable, os.path.join(current_dir, "app_moodle.py")])
    procs.append(p2)
    time.sleep(1)

    print("[3/3] Khoi dong MekoBook Reader App (:5002)...")
    p3 = subprocess.Popen([sys.executable, os.path.join(current_dir, "app_mekobook.py")])
    procs.append(p3)
    time.sleep(1)

    print("\n[OK] CA 3 HE THONG DA SAN SANG HOAT DONG!")
    print(">> Hay mo trinh duyet va truy cap: http://localhost:5001 de bat dau thu nghiem.")
    print(">> Nhan Ctrl + C tai cua so nay de tat toan bo he thong demo.\n")

    # Giữ tiến trình chạy
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n\n[DUNG] Dang dung toan bo 3 server...")
    for p in procs:
        p.terminate()
    print("Da tat an toan he thong demo.")
