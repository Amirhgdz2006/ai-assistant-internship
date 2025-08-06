from redis import Redis
from dotenv import load_dotenv
import os
load_dotenv()

redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")

r_client = Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)