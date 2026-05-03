import subprocess
import sys

def main() -> None:
    print("Launching Streamlit App...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/presentation/app.py"])

if __name__ == "__main__":
    main()
