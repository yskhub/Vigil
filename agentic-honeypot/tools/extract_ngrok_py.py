import zipfile
from pathlib import Path

zip_path = Path(r"D:/Vigil/ngrok-v3-stable-windows-amd64 (1).zip")
dest = Path(r"D:/Vigil/agentic-honeypot/tools/ngrok")
dest.mkdir(parents=True, exist_ok=True)

print(f"Extracting {zip_path} -> {dest}")
with zipfile.ZipFile(zip_path, 'r') as z:
    z.printdir()
    for info in z.infolist():
        name = info.filename
        target = dest / name
        try:
            print(f"Extracting {name} -> {target}")
            data = z.read(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, 'wb') as f:
                f.write(data)
        except Exception as e:
            print(f"Failed to write {target}: {e}")

print("Attempted extraction. Contents now:")
for p in dest.iterdir():
    try:
        print(p.name, p.stat().st_size)
    except Exception as e:
        print(p.name, "(stat failed)", e)
