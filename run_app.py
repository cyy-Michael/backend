import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    # 获取脚本所在目录 (即项目根目录)
    root = Path(__file__).parent.absolute()
    print(f"Project root: {root}")
    
    os.chdir(root)
    sys.path.insert(0, str(root))
    
    # Check .env
    env_file = root / ".env"
    env_example = root / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            print("Creating .env from .env.example...")
            shutil.copy(env_example, env_file)
        else:
            print("Warning: .env not found and .env.example not found.")
            # Create a minimal .env
            with open(env_file, "w", encoding="utf-8") as f:
                f.write("MONGO_URI=mongodb://localhost:27017\n")
                f.write("DB_NAME=teacher_query\n")
                f.write("SECRET_KEY=dev_secret_key\n")
                f.write("ALGORITHM=HS256\n")
                f.write("ACCESS_TOKEN_EXPIRE_MINUTES=30\n")
    
    print("Starting application...")
    try:
        # 使用 python -m uvicorn 启动
        cmd = [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
        print(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Application failed to start: {e}")
    except KeyboardInterrupt:
        print("Application stopped.")

if __name__ == "__main__":
    main()
