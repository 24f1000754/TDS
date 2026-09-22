# Q5 Code Interpreter API

FastAPI endpoint:
POST /code-interpreter

Request:
{"code": "x = 5\ny = 10\nprint(x + y)"}

Successful response:
{"error": [], "result": "15"}

For an exception, the response contains traceback-derived line numbers in `error`
and the exact traceback text in `result`.

## Deploy on Render

1. Create a new Web Service from this project.
2. Runtime: Python.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. After deployment, use:
   `https://YOUR-SERVICE.onrender.com/code-interpreter`
   in the Q5 answer box.
