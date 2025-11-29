import os

def send_data(data: bytes, client):
        length = len(data)
        client.sendall(str(length).encode())
        client.recv(len(b'True'))
        for i in range(0, length, 2048):
            client.sendall(data[i:2048 + i])
        confirm = client.recv(len(b'True')).decode()
        if confirm != 'True':
            print("Did not receive expected confirmation")
            exit(0)

def recv_data(client):
        length = int(client.recv(1024).decode())
        client.sendall(b'True')
        data = b''
        remaining = length
        while remaining > 0:
            info = client.recv(min(2048, remaining))
            data += info
            remaining -= len(info)
        client.sendall(b'True') 
        return data

def funcion_cancion_receive(client, canciones:list, path, lock=None):
        client.sendall(b'Yes')
        for i in canciones:
            print(f'Receiving 《{i["titulo"]}》 ......')
            client.sendall(i['archivo'].encode())
            data = recv_data(client)
            if lock:
                with lock:
                    with open(os.path.join(path, i['archivo']), 'wb') as f:
                        f.write(data)
            else:
                 with open(os.path.join(path, i['archivo']), 'wb') as f:
                        f.write(data)
        client.sendall(b'final')

def funcion_cancion_send(client, path, lock=None):
    client.recv(len(b'Yes'))
    print('\nBegin sending canciones')
    # begin to send music
    while True:
        song_path = client.recv(1024).decode()
        if song_path == 'final':
            break
        if lock and path:
            with lock:
                with open(os.path.join(path, song_path), 'rb') as f:
                    info = f.read()
        elif path and not lock:
            with open(os.path.join(path, song_path), 'rb') as f:
                info = f.read()
        else:
             print('Error NoneType cant be path')
        send_data(info, client)
    print('End of sending canciones')
    