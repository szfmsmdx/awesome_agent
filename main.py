from api.service_api import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import Config
import argparse
import logging
import uvicorn

CFG = Config()
app = FastAPI()

# Add CORS middleware
# Origins that are allowed to make cross-origin requests.
# You can use ["*"] to allow all origins, or be more specific
# e.g., ["http://localhost:8000", "http://127.0.0.1:8000"] if your frontend is served there.
origins = [
    "*"  # For development, allow all. For production, restrict this.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(router)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Awesome agent api")
    parser.add_argument("--host", type=str, default=CFG.host, help="服务器主机地址")
    parser.add_argument("--port", type=int, default=CFG.server_post, help="服务器端口")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")