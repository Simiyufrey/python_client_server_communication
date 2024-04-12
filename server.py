import socket
import threading
import json

# Define host and port
HOST =  '0.0.0.0'  # Loopback address for localhost
PORT = 12345        # Arbitrary port number

# List to store connected client sockets
client_sockets = []
super_clients=[]
previous_clients_length=0

# Function to handle client connections
def handle_client(conn, addr):
    global client_sockets,previous_clients_length,super_clients
    with conn:
        print('Connected by', addr)
        client_sockets.append({"conn":conn,"data":{}})
        
        while True:
            try:
            # Receive data from the client
                data = conn.recv(1024)
                if not data:
                    break
                
                print("Received:", data.decode())
                received_data=json.loads(data.decode())
                if received_data['action']=="connected" and received_data['type'] =="client":
                    for i  in range(len(client_sockets)):
                        if client_sockets[i]['conn'] ==conn:
                            print("LENGTH  CLIENTS AND SUPER ",len(client_sockets),len(super_clients))
                            client_sockets[i]['data']=received_data['data']
                            break
                elif received_data['action']=="connected" and  received_data['type']=="super":
                    for i  in range(len(client_sockets)):
                        client=client_sockets[i]
                        if client['conn'] ==conn:
                            del client_sockets[i]
                            super_clients.append({"conn":conn,data:received_data['data']})
                            conn.sendall(json.dumps({"source":"server",
                                                     "target":"super",
                                                     'data':{"clients":[client['data']['Machine Name'] for client in client_sockets ]}}).encode())
        
                            break
                elif received_data['action'] =="message":
                    if received_data['source'] =="super":
                        handle_gui_messages(received_data)
                    else:
                        if received_data['target'] =="super":
                            for super in super_clients:
                                if super['conn'] != conn:  # Exclude the sender
                                    data={
                                        "action":"message",
                                        "source":"client",
                                        "target":"super",
                                        "data":{
                                            "message":received_data['data']['message']
                                        }
                                     }
                                    super['conn'].sendall(json.dumps(data).encode())
                        elif received_data['source'] =="client":
                            for client_conn in client_sockets:
                                if client_conn['conn'] != conn:  # Exclude the sender
                                    data={
                                        "action":"message",
                                        "source":"server",
                                        "target":"client",
                                        "data":{
                                            "message":received_data['data']['message']
                                        }
                                     }
                                    client_conn['conn'].sendall(json.dumps(received_data).encode())
                            
                    
                # Broadcast the message to all connected clients
            
                if len(super_clients) > 0 and previous_clients_length < len(client_sockets) :
                    for super in super_clients:
                          super['conn'].sendall(json.dumps({"source":"server",
                                                     "target":"super",
                                                     'data':{"clients":[client['data']['Machine Name'] for client in client_sockets ]}}).encode())
        
                    previous_clients_length = len(client_sockets)
            except Exception as e:
               if(str(e).__contains__("forcibly")):
                   
                   for i in range(len(client_sockets)):
                       if client_sockets[i]['conn']== conn:
                           del client_sockets[i]
                           previous_clients_length =len(client_sockets)
                           break
                   for i in range(len(super_clients)):
                       if super_clients[i]['conn']== conn:
                           del super_clients[i]
                           break
                   print(len(client_sockets),len(client_sockets))
                   break
               print(e)
                    
            # Send client information to the GUI
# Function to send client information to the GUI
def handle_gui_messages(received_data):
    try:
        for client in client_sockets:
        
                if client['data']['Machine Name']  == received_data['data']['client']:
                    message={
                        "action":"message",
                        "source":received_data['source'],
                        "data":{
                        "shutdown":received_data['data']['shutdown'],
                        "shell":received_data['data']['shell'],
                        "message":received_data['data']['message']
                        }
                    }
                    
                    client['conn'].sendall(json.dumps(message).encode())
    except Exception as e:
            print(e,"HERREEEEEEEEEEEEEEEEEEEEEEEEE")
def send_client_info_to_gui():
    global client_sockets
    gui_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gui_socket.connect(('127.0.0.1', 12346))  # Connect to GUI server
    client_info = [{"address": client['conn'].getpeername(), "data": client['data']} for client in client_sockets]
    gui_socket.sendall(json.dumps(client_info).encode())
    gui_socket.close()

# Create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Bind the socket to the host and port
    server_socket.bind((HOST, PORT))
    
    # Listen for incoming connections
    server_socket.listen()

    print("Server is listening for connections...")

    while True:
        try:
        # Accept a client connection
            conn, addr = server_socket.accept()
            
            # Start a new thread to handle the client connection
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
        except Exception as e:
            print(e)
