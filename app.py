from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import sys
import tempfile
import os
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

def execute_python_code(code: str) -> dict:
    # Run submitted code in a separate Python process so failures/timeouts
    # do not crash the API process itself.
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        path = f.name

    try:
        completed = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if completed.returncode == 0:
            return {
                "success": True,
                "output": completed.stdout,
            }

        # Python traceback lines look like: File "...", line 3, in ...
        combined = completed.stderr
        lines = [int(x) for x in re.findall(r'File ".*?", line (\d+)', combined)]

        return {
            "success": False,
            "output": combined,
            "error_lines": sorted(set(lines)),
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "Traceback: execution timed out",
            "error_lines": [],
        }
    finally:
        try:
            os.remove(path)
        except OSError:
            pass

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/code-interpreter")
def code_interpreter(request: CodeRequest):
    result = execute_python_code(request.code)

    if result["success"]:
        return {
            "error": [],
            "result": result["output"].rstrip("\n"),
        }

    return {
        "error": result["error_lines"],
        "result": result["output"],
    }
