# AI assisted development
import os
import urllib.request

# Crear carpeta de assets
os.makedirs("assets", exist_ok=True)

# Descargar Assets Limpios de alta calidad
assets = {
    "assets/background.png": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=1024&q=80",
    "assets/customer.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/trainers/1.png",
}

print("Descargando imágenes base para Slime Lab...")
for path, url in assets.items():
    try:
        urllib.request.urlretrieve(url, path)
        print(f"✓ Guardado: {path}")
    except Exception as e:
        print(f"❌ Error al descargar {path}: {e}")

print("¡Listo! Ahora dale el prompt a Cursor.")
