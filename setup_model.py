"""
One-time setup: registers the AEGIS fine-tuned model with Ollama.
Run this before launching the app: python setup_model.py
"""

import subprocess
import sys
import os
from pathlib import Path


def find_ollama() -> str:
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Ollama", "ollama.exe"),
        "ollama",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
        try:
            subprocess.run([c, "--version"], capture_output=True, timeout=5)
            return c
        except Exception:
            pass
    return None


def main():
    print("=" * 60)
    print("  AEGIS Model Setup")
    print("=" * 60)

    ollama = find_ollama()
    if not ollama:
        print("\n❌  Ollama not found.")
        print("   Install from https://ollama.com/download and re-run.\n")
        sys.exit(1)

    print(f"\n✅  Ollama found: {ollama}")

    gguf_dir = Path(__file__).parent / "resources" / "resources" / "gguf"
    modelfile = gguf_dir / "Modelfile"
    gguf_file = gguf_dir / "gemma-4-e4b-it.Q4_K_M.gguf"

    if not modelfile.exists():
        print(f"\n❌  Modelfile not found: {modelfile}\n")
        sys.exit(1)

    if not gguf_file.exists():
        print(f"\n❌  GGUF model not found: {gguf_file}\n")
        print("   Ensure the resources/resources/gguf/ folder contains the model file.\n")
        sys.exit(1)

    print(f"✅  Modelfile found: {modelfile}")
    print(f"✅  GGUF model found: {gguf_file} ({gguf_file.stat().st_size / 1e9:.1f} GB)")

    print("\n🔄  Creating AEGIS model in Ollama...")
    print("   (This may take 30-60 seconds on first run)\n")

    result = subprocess.run(
        [ollama, "create", "aegis", "-f", "Modelfile"],
        cwd=str(gguf_dir),
        capture_output=False,
        timeout=300,
    )

    if result.returncode == 0:
        print("\n✅  AEGIS model registered successfully!")
        print("\n   Run the app with:")
        print("   python app.py")
        print("\n   Then open http://localhost:5001\n")
    else:
        print("\n❌  Model creation failed. Check Ollama logs.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
