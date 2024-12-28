import time
import logging
from sqlalchemy.orm import Session
from utils import get_db
from models import Node

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_all_nodes():
    with next(get_db()) as db:
        nodes = db.query(Node).all()
        return nodes

def monitor_database():
    while True:
        nodes = fetch_all_nodes()
        logging.info(f"Fetched {len(nodes)} nodes from the database.")
        for node in nodes:
            logging.info(f"Node ID: {node.node_id}, Status: {node.status}, Resources: {node.resources}")
        time.sleep(10)
