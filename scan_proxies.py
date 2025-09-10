import os

site_packages = os.path.join("venv", "Lib", "site-packages")
for root, dirs, files in os.walk(site_packages):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if "proxies" in line:
                            print(path, ":", line.strip())
            except Exception:
                pass
