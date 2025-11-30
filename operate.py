from musica.plataforma import *
from app import mostrar_choices, pedir_int, menu_canciones, menu_listas, menu_reproduccion
from TADs import ListaEnlazada
import copy
import os

class OperateClient:
    def __init__(self, path):
        self.ini_cancion = []
        self.ini_lista = []
        self.ini_ids = []
        self.plata = None
        self.path = path
        self.lista_enlazar = ListaEnlazada()
        self.data = {'canciones':{'eliminar': {}, 'anadir': {}, 'modificar': {}},
                     'listas':{'eliminar': [], 'nuevo': {}}}

    def iniciar_cancion(self, cancion_info: dict):
        for id, c in cancion_info.items():
            cancion = Cancion(c['titulo'], c['artista'], int(c['duracion']), c['genero'], c['archivo'])
            cancion.cambia_id(int(id))
            cancion.archivo = os.path.join(self.path, cancion.archivo)
            self.ini_cancion.append(cancion)
        self.ini_ids = [int(i) for i in cancion_info.copy().keys()]
    
    def iniciar_lista(self, lista_info: dict):
        for nombre, c in lista_info.items():
            lista = ListaReproduccion(nombre)
            lista.anadir_lista_de_cancion(c)
            self.ini_lista.append(lista)

    def iniciar_info(self, canciones: dict, listas: dict):
        self.iniciar_cancion(canciones)
        self.iniciar_lista(listas)
        return self.ini_cancion.copy(), self.ini_lista.copy()
    
    def hacer(self, tipo):
        if tipo == 'deshacer':
            result = self.lista_enlazar.deshacer()
        elif tipo == 'rehacer':
            result = self.lista_enlazar.rehacer()
        if result:
            self.plata = copy.deepcopy(self.lista_enlazar.current.data)
            print(f'{tipo} exito!')
        else:
            print(f'No puede {tipo}.')

    def operation(self):
        cancion_ids = [c.id for c in self.ini_cancion]
        self.plata = PlataformaMusical(self.ini_cancion, self.ini_lista, cancion_ids)
        self.lista_enlazar.enlazar(copy.deepcopy(self.plata))
        while True:
            choices = {1: 'Gestionar canciones', 2: 'Gestionar listas', 3: 'Reproducción',
                       4: 'Deshacer última acción', 5: 'Rehacer última acción deshecha', 0: 'Volver'}
            mostrar_choices('\n=== Plataforma Musical ===', choices)
            opc = pedir_int('> ')
            funciones = [menu_canciones, menu_listas, menu_reproduccion, 'deshacer', 'rehacer']
            if opc != 0:
                try:
                    if 0 < opc < 4:
                        funciones[opc - 1](self.plata, self.lista_enlazar)
                    else:
                        self.hacer(funciones[opc - 1])
                except Exception:
                    print('Opción inválida')
            else:
                print('Hasta luego')
                break

    def deal_with_cancion(self, c_total, dir_path):
        cancion_ids = self.plata.cancion_ids
        for c in c_total:
            if c.id in cancion_ids and c.id not in self.ini_ids:
                self.data['canciones']['anadir'][str(c.id)] = c.mostrar_data_parte2()
                path = os.path.join(dir_path, os.path.basename(c.archivo))
                with open(path, 'wb') as f:
                    with open(c.archivo, 'rb') as f1:
                        f.write(f1.read())
            elif c.id in self.ini_ids and c.id not in cancion_ids:
                self.data['canciones']['eliminar'][str(c.id)] = {'titulo': c.titulo, 'archivo': os.path.basename(c.archivo)}
                path = os.path.join(dir_path, os.path.basename(c.archivo))
                if os.path.exists(path):
                    os.remove(path)
            elif c.changed:
                self.data['canciones']['modificar'][str(c.id)] = c.changed

    def deal_with_lista(self, l_old):
        # Robustly compute deleted, added and changed lists by comparing names
        old_names = [i.nombre for i in l_old]
        new_names = [i.nombre for i in self.plata.listas]
        # deleted lists: in old but not in new
        for name in old_names:
            if name not in new_names:
                if name not in self.data['listas']['eliminar']:
                    self.data['listas']['eliminar'].append(name)
        # added or changed lists: in new but not in old OR changed flag set
        for lista in self.plata.listas:
            if lista.nombre not in old_names or lista.changed:
                self.data['listas']['nuevo'][lista.nombre] = lista.canciones
    
    def saving(self, path: str, c_old: list[Cancion], l_old: list[ListaReproduccion]):
        print('Saving information...')
        c_total = [i for i in c_old if i not in self.plata.canciones] + self.plata.canciones
        l_total = [i for i in l_old if i not in self.plata.listas] + self.plata.listas
        self.deal_with_cancion(c_total, path)
        self.deal_with_lista(l_old)


class OperateServidor:
    def __init__(self, old_data: dict, changed: dict, path: str, lock):
        self.old_data = old_data
        self.changed = changed
        self.path = path
        self.lock = lock

    def ope_cancion(self):
        for key, value in self.changed['canciones'].items():
            if key == 'anadir':
                for i, j in value.items():
                    self.old_data['canciones'][i] = j
            elif key == 'eliminar':
                for i, j in value.items():
                    self.old_data['canciones'].pop(i, None)
                    with self.lock:
                        try:
                            os.remove(os.path.join(self.path, j['archivo']))
                        except FileNotFoundError:
                            # If file does not exist, ignore and continue
                            pass
                        except Exception as e:
                            print(f'Error removing file {j["archivo"]}: {e}')
            else:
                for i, j in value.items():
                    for a, b in j.items():
                        self.old_data['canciones'][i][a] = b

    def ope_lista(self):
        for key, value in self.changed['listas'].items():
            if key == 'nuevo':
                for i, j in value.items():
                    self.old_data['listas'][i] = j
            else:
                for i in value:
                    self.old_data['listas'].pop(i)

    def get_data(self):
        self.ope_cancion()
        self.ope_lista()
        return self.old_data