import zipfile
from pathlib import Path
import tempfile

zip_path = Path(r"D:/Vigil/ngrok-v3-stable-windows-amd64 (1).zip")
dest = Path(tempfile.gettempdir()) / "ngrok_extracted"
dest.mkdir(parents=True, exist_ok=True)

print(f"Extracting {zip_path} -> {dest}")
with zipfile.ZipFile(zip_path, 'r') as z:
    for info in z.infolist():
        name = info.filename
        target = dest / name
        try:
            print(f"Writing {target}")
            data = z.read(name)
            with open(target, 'wb') as f:
                f.write(data)
        except Exception as e:
            print(f"Failed to write {target}: {e}")

print("Done. Listing contents:")
for p in dest.iterdir():
    print(p.name, p.stat().st_size)
print('User temp path:', dest)
