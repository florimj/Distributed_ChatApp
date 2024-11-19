import time

def monitor_heartbeat(server):
    while True:
        time.sleep(10)
        if server.is_leader:
            server.broadcast_message({"type": "heartbeat", "id": str(server.id)})
