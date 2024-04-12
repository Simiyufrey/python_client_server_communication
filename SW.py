import tkinter as tk
from tkinter import ttk
import socket
import json
import platform
import threading
    # Function to handle sending data (to be implemented)
SERVER_ADDRESS = ('1.1.1.81', 12345)
client_socket=None
clients=set()
def connect(): 
    global client_socket
    client_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(SERVER_ADDRESS)  
    machine_name = socket.gethostname()
    system = platform.system()
    release = platform.release()
    version = platform.version()
    
    message={"action":"connected","type":"super","data":{
        "Machine Name": machine_name,
        "Operating System": system,
        "OS Release": release,
        "OS Version": version
    }}
    client_socket.sendall(json.dumps(message).encode())
    while True:
        
        response = client_socket.recv(1024)
        received_data=json.loads(response.decode())
        if received_data['source'] =="server":
            received_clients=received_data['data']['clients']
            for client in received_clients:
                clients.add(client)
            c_values=[]
            for _ in clients:
                c_values.append(_)
            option_combobox['values']=c_values
        else:
            text_area.insert(tk.END,str(received_data['data']['message']))
def on_enter(event):
    send_data()
def send_data():
    selected_option = option_combobox.get()
    entered_text = text_entry.get()
    use_shell = check_var1.get()
    is_shutdown= check_var.get()

    data = {
        'action':'message',
        "source":"super",
        "target":"client",
        'data':{
        'client': selected_option,
        'message': entered_text,
        'shell': True if use_shell ==1 else False,
        'shutdown': True if is_shutdown ==1 else False,
        }
        }
        
        # Send data to server
    client_socket.sendall(json.dumps(data).encode())

# Create main window
# Create main window
thread = threading.Thread(target=connect, args=())
thread.start()
window = tk.Tk()
window.title("Data Sender")
window.geometry("500x400")

# Create frame with grid layout
frame = tk.Frame(window, bg="white", borderwidth=2, relief="solid")
frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

# Add components to the frame
tk.Label(frame, text="Choose Client:", font=("Georgia", 10)).grid(row=0, column=0, padx=10, pady=10)
option_combobox = ttk.Combobox(frame, values=["Option 1", "Option 2", "Option 3"])
option_combobox.grid(row=0, column=1, padx=10, pady=10)

tk.Label(frame, text="Enter Message/Command:", font=("Georgia", 10)).grid(row=1, column=0, padx=5, pady=5)
text_entry = tk.Entry(frame, width=40)  # Span full row
text_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

text_entry.bind("<Return>", on_enter)



check_var1 = tk.IntVar()
check_button1 = tk.Checkbutton(frame, text="Use Shell", variable=check_var1)
check_button1.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

check_var = tk.IntVar()
check_button = tk.Checkbutton(frame, text="shutdown", variable=check_var)
check_button.grid(row=4, column=1, columnspan=2, padx=5, pady=5)

tk.Label(window, text="Output", font=("Georgia", 10)).grid(row=5, column=0, padx=5, pady=5)
text_area = tk.Text(window, font=("Georgia", 10), height=10, width=40)  # Height and width are in characters
text_area.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

# Create send button at the bottom
send_button = tk.Button(window, text="Send", bg="lightgreen", font=("Georgia", 12), relief="raised", command=send_data)
send_button.place(relx=0.5, rely=0.95, anchor="s")

# Run the main loop
window.mainloop()
