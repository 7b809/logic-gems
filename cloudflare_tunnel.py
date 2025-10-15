import subprocess
import shutil
import re
import os

# ============================================
# 🌐 1️⃣ Install cloudflared if missing
# ============================================
def install_cloudflared():
    if not shutil.which("cloudflared"):
        print("⏳ Installing Cloudflare Tunnel (cloudflared)...\n")
        subprocess.run([
            "curl", "-fsSL",
            "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
            "-o", "cloudflared"
        ], check=True)
        subprocess.run(["chmod", "+x", "cloudflared"], check=True)
        print("✅ cloudflared installed successfully.\n")
    else:
        print("✅ cloudflared already installed.\n")

# ============================================
# 🌍 2️⃣ Start Cloudflare Tunnel
# ============================================
def start_cloudflare_tunnel(local_port):
    print(f"⏳ Starting Cloudflare tunnel for http://localhost:{local_port} ...\n")

    cf_proc = subprocess.Popen(
        ["./cloudflared", "tunnel", "--url", f"http://localhost:{local_port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    public_url = None
    for line in iter(cf_proc.stdout.readline, ""):
        if line:
            print(f"[Cloudflare] {line.strip()}")
            if "trycloudflare.com" in line and not public_url:
                match = re.search(r"https://[0-9a-zA-Z\-]+\.trycloudflare\.com", line)
                if match:
                    public_url = match.group(0)
                    print(f"\n✅ Public URL ready: {public_url}\n")
    return cf_proc, public_url

# ============================================
# ✅ MAIN EXECUTION
# ============================================
if __name__ == "__main__":
    # The local port your app.py runs on
    LOCAL_PORT = 8000

    install_cloudflared()
    cf_proc, public_url = start_cloudflare_tunnel(LOCAL_PORT)

    print("\n💡 Use this public URL to access your app remotely:\n", public_url)

    # Keep the tunnel running
    try:
        cf_proc.wait()
    except KeyboardInterrupt:
        print("\n🔴 Stopping Cloudflare tunnel...")
        cf_proc.terminate()
        cf_proc.wait()
        print("✅ Tunnel stopped.")
