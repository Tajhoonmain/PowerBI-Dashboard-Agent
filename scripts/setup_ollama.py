"""Setup script for Ollama."""
import requests
import sys

def check_ollama():
    """Check if Ollama is available."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama is running")
            models = response.json().get("models", [])
            if models:
                print(f"✓ Found {len(models)} model(s):")
                for model in models:
                    print(f"  - {model.get('name', 'unknown')}")
            else:
                print("⚠ No models found. Run: ollama pull llama2")
            return True
        else:
            print("✗ Ollama is not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Ollama is not running")
        print("  Please install Ollama from https://ollama.ai/")
        print("  Then start it with: ollama serve")
        return False
    except Exception as e:
        print(f"✗ Error checking Ollama: {e}")
        return False

def pull_model(model_name="llama2"):
    """Pull a model from Ollama."""
    try:
        print(f"Pulling model: {model_name}...")
        response = requests.post(
            "http://localhost:11434/api/pull",
            json={"name": model_name},
            stream=True,
            timeout=300
        )
        if response.status_code == 200:
            print(f"✓ Successfully pulled {model_name}")
            return True
        else:
            print(f"✗ Failed to pull {model_name}")
            return False
    except Exception as e:
        print(f"✗ Error pulling model: {e}")
        return False

if __name__ == "__main__":
    print("Ollama Setup Check")
    print("=" * 40)
    
    if check_ollama():
        print("\n✓ Setup complete!")
    else:
        print("\n⚠ Setup incomplete. Please install and start Ollama.")
        sys.exit(1)


