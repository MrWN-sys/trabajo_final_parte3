import socket
import pickle
import os
import sys
from app import *
from tools import *
from operate import OperateClient

class Client:
    def __init__(self, host: str, port: int):
        self.name = self.ask_name()
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.info = None
        self.path = os.path.join(os.path.dirname(__file__), 'client_library', self.name)

    def ask_name(self):
        while True:
            name = input('Name (q to quit): ').strip()
            if name == 'q':
                print('Leave correctly.')
                exit(0)
            if name:
                return name

    def iniciar_canciones(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path, exist_ok=True)
        print('Begin loading songs...')
        funcion_cancion_receive(self.client, self.info['canciones'].values(), self.path)
        print('Loading songs correctly.')

    def iniciar_information(self):
        print('Initting information...')
        data = recv_data(self.client)
        self.info = pickle.loads(data) # diccionario

    def send_information(self): # json information
        operate = OperateClient(self.path)
        c, l = operate.iniciar_info(self.info['canciones'], self.info['listas'])
        operate.operation()
        operate.saving(self.path, c, l)
        print('Saving information...')
        send_data(pickle.dumps(operate.data), self.client)
        print('End of sending information\n')

    def main_client(self):
        self.client.connect((self.host, self.port))
        self.client.sendall(self.name.encode())
        info = self.client.recv(1024).decode()
        print(info)
        if info != 'The user is using.':
            try:
                self.iniciar_information()
                self.iniciar_canciones()
                self.send_information()
                funcion_cancion_send(self.client, self.path)
            
            except (ConnectionResetError, BrokenPipeError):
                print('Error from server.')
            except KeyboardInterrupt:
                print('Closing the client...')
            except Exception as e:
                print(f'Unexpected error {e}')
        self.client.close()
 
if __name__ == '__main__':
    try:
        host, port = sys.argv[1], int(sys.argv[2])
    except Exception as e:
        print(f'Error: {e}')
        exit(0)
    client = Client(host, port)
    client.main_client()