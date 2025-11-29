import pickle
import socket
import threading
import json
import sys
import os
from tools import *
from operate import OperateServidor
from TADs import Pila
from datetime import datetime

class Servidor:
    def __init__(self, port: int):
        self.port = port
        self.service = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client_states = {}
        self.lock = threading.Lock()
        self.dir_name = os.path.join(os.path.dirname(__file__), 'datos_server')
        self.make_dir(self.dir_name)
        self.pilas_dict = {}
    
    def make_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def deal_json_info(self, path:str, tipo:str, data=None):
        if tipo == 'r':
            with open(path, 'r') as f:
                return json.load(f)
        elif tipo == 'w':
            with open(path, 'w') as f:
                json.dump(data, f)

    def check_name_is_using(self, client, name:str):
        with self.lock:
            if self.client_states.get(name, 0):
                client.sendall('The user is using.'.encode())
                return False
            self.client_states[name] = 1
            client.sendall('Welcome.'.encode())
        return True
               
    def transmit_data(self, client, client_path, name):        
        # 传输元数据
        info = self.deal_json_info(client_path, 'r')
        send_data(pickle.dumps(info), client)
        funcion_cancion_send(client, os.path.join(self.dir_name, name), self.lock)

    def receive_data(self, client, name: str, path: str, path_dir) -> list: # 接受客户端数据，只需要接受元数据
        print(f'\nBegin receiving information from {name}...')
        data = pickle.loads(recv_data(client))
        old_data = self.deal_json_info(path, 'r')
        operate = OperateServidor(old_data, data, path_dir, self.lock)
        new_data = operate.get_data()
        self.deal_json_info(path, 'w', new_data)
        print(f'End of receiving information from {name}\n')
        return list(data['canciones']['anadir'].values())

    def close_client(self, name: str, client, data_path: str, vers_path: str):
        client.close()
        print(f'{name} is closed.')
        data = self.deal_json_info(data_path, 'r')
        file_name = datetime.now().strftime('%Y_%m_%d_%H_%M_%S.json')
        path = os.path.join(vers_path, file_name)
        self.deal_json_info(path, 'w', data)
        with self.lock:
            self.pilas_dict[name].enpilar(path)
            self.client_states[name] = 0

    def load_version(self, path: str, name) -> str:
        self.make_dir(path)
        with self.lock:
            if not self.pilas_dict.get(name, 0):
                files = os.listdir(path)
                files.reverse()
                self.pilas_dict[name] = Pila()
                self.pilas_dict[name].pilar_lista(files, path)

    def deal_client(self, name: str, client):
        path = os.path.join(self.dir_name, name)
        version_path = os.path.join(path, 'Version')
        client_path = os.path.join(path, f'{name}.json')
        self.load_version(version_path, name)
        if not os.path.exists(client_path):
            self.deal_json_info(client_path, 'w', {'canciones': {}, 'listas': {}})
        try:
            self.transmit_data(client, client_path, name) # 初始化数据
            canciones_new = self.receive_data(client, name, client_path, path)
            funcion_cancion_receive(client, canciones_new, path, self.lock)
        except (ConnectionResetError, BrokenPipeError):
            print(f'Connection with {name} lost')
        except Exception as e:
            print(f'Error from {name} -> {e}.')
        finally:
            self.close_client(name, client, client_path, version_path)

    def main(self):
        self.service.bind(('127.0.0.1', self.port))
        self.service.listen()
        try:
            while True:
                client, addr = self.service.accept()
                name = client.recv(1024).decode().lower()
                print(f'Connection from {addr} with name {name}.')
                if self.check_name_is_using(client, name):
                    threading.Thread(target=self.deal_client, args=[name, client]).start()
                else:
                    client.close()
        except KeyboardInterrupt:
            print('Closing the service...')
        self.service.close()

if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except Exception as e:
        print(f'Error: {e}')
        exit(0)
    servidor = Servidor(port)
    servidor.main()
