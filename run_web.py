"""Start the showcase web interface: http://127.0.0.1:8257. Install first: pip install -r requirements-web.txt"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("web.app:app", host="127.0.0.1", port=8257)
