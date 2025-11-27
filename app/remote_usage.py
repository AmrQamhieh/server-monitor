import paramiko
import json
import os
from .logging_utils import get_logger, log_action

logger = get_logger(__name__)


HOST = os.getenv("HOST_IP", "10.0.3.15")
USER = os.getenv("HOST_USER", "root")
PASSWORD = os.getenv("HOST_PASSWORD", "root")

CPU_CMD = "vmstat 1 2 | tail -1 | awk '{print 100 - $15}'"
MEM_CMD = "free -m | awk '/Mem:/ {printf \"%.2f\", ($3/$2)*100}'"
DISK_CMD = "df -h / | awk 'NR==2 {print $5}' | tr -d \"%\""

@log_action
def main():
#Create an SSH client object
    client = paramiko.SSHClient()
    
#Automatically aceept unkown hosts (like "yes" on first ssh)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#Connect using our privacy key
    logger.info(f"Connecting to {HOST} as {USER}")
    client.connect(
        hostname=HOST,
        username=USER,
        password=PASSWORD,
        timeout=10,
    )
    
    
    def run(cmd: str)-> str:
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        if err:
            # for now just raise; later we can log instead
            raise RuntimeError(f"Command failed: {cmd}\n{err}")
        return out

   # Run the three commands on the remote machine
    cpu_str = run(CPU_CMD)
    mem_str = run(MEM_CMD)
    disk_str = run(DISK_CMD)


    # Convert String values into Numbers(float)
    cpu = float(cpu_str)
    mem = float(mem_str)
    disk = float(disk_str)

    usage = {
    "cpu": cpu,
    "mem": mem,
    "disk":disk,
    }    


# Close the connection
    client.close()
    logger.info("SSH connection closed")

    print(json.dumps(usage))


if __name__ == "__main__":
    main()











