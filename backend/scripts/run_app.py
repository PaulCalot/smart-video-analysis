import logging

logging.basicConfig(filename="LOGS/app.log", level=logging.DEBUG)

import uvicorn

from sva.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
