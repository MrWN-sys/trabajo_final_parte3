import pygame
import os

class Cancion:
    id = 0
    usado = []

    def get_id(self):
        while True:
            Cancion.id += 1
            if Cancion.id not in Cancion.usado:
                Cancion.usado.append(Cancion.id)
                break

    def __init__(self, titulo=None,  artista=None, duracion=None, genero=None, archivo_mp3=None):
        self.get_id()
        self.id = Cancion.id
        self.titulo = titulo
        self.artista = artista
        self.duracion = duracion
        self.genero = genero
        self.archivo = archivo_mp3
        self.changed = None

    def cambia_id(self, new_id: int) -> None:
        Cancion.usado.remove(self.id)
        Cancion.usado.append(int(new_id))
        self.id = int(new_id)

    def reproducir(self) -> None:
         # 初始化pygame并播放音乐
         pygame.init()
         pygame.mixer.init()
         # 使用 pygame.mixer.music API
         pygame.mixer.music.load(self.archivo)
         pygame.mixer.music.play()
    
    def stop(self) -> None:
        pygame.mixer.music.pause()
       

    def edit_cancion(self, titulo: str, artista: str, duracion: int, genero: str, archivo:str):
       self.changed = {}
       l2 = [titulo, artista, duracion, genero, archivo]
       l3 = ['titulo', 'artista', 'duracion', 'genero', 'archivo']
       for i, j in zip(l3, l2):
           if j:
                setattr(self, i, j)
                if i != 'archivo':
                    self.changed[i] = j
                else:
                    self.changed[i] = os.path.basename(j)
            
     
    def mostrar_infos(self, sequence=None, normal=True) -> str:
        texto1 = f'{self.titulo} - {self.artista} ({round(float(self.duracion), 1)}s) '
        texto2 = f'[{self.genero}] -> {self.archivo}'
        if not normal:
            return f'{sequence}) ' + texto1
        else:
            return f'{self.id}) ' + texto1 + texto2
        
    def mostrar_data_parte2(self):
        data = {}
        keys = ['titulo', 'artista', 'duracion', 'genero', 'archivo']
        values = [self.titulo, self.artista, self.duracion, self.genero, self.archivo]
        for key, value in zip(keys, values):
            if key != 'archivo':
                data[key] = value
            else:
                data[key] = os.path.basename(value)
        # include id explicitly
        data['id'] = self.id
        return data


class ListaReproduccion:
   def __init__(self, nombre:str):
       self.nombre = nombre
       self.canciones = []
       self.changed = False

   def anadir_cancion(self, id_cancion: int) -> bool:
       if id_cancion not in self.canciones:
           self.canciones.append(id_cancion)
           self.changed = True
           return True
       return False

   def quitar_cancion(self, id_cancion: int) -> bool:
       if id_cancion in self.canciones:
           self.canciones.remove(id_cancion)
           self.changed = True
           return True
       return False
   
   def mostrar_informacion(self) -> str:
       return f'{self.nombre} ({len(self.canciones)} canciones)'
   
   def mostrar_cancion(self, canciones: list[Cancion]) -> list[str]:
       return [cancion for cancion in canciones if cancion.id in self.canciones]
   
   def anadir_lista_de_cancion(self, lista_ids: list[int]):
       for id in lista_ids:
           self.anadir_cancion(id)


class PlataformaMusical:
   def __init__(self, canciones=None, listas=None, cancion_ids=None):
       self.canciones = canciones if canciones is not None else []
       self.listas = listas if listas is not None else []
       self.cancion_ids = cancion_ids if cancion_ids is not None else []

   def registrar_cancion(self, titulo: str, artista: str, duracion: int, genero: str, archivo:str) -> bool:
        for cancion in self.canciones:
           if cancion.titulo == titulo and cancion.artista == artista:
               return False
        cancion = Cancion(titulo, artista, duracion, genero, archivo)
        self.canciones.append(cancion)
        self.cancion_ids.append(cancion.id)
        return True
  
   def editar_cancion(self, id: int, titulo: str, artista: str, duracion: int, genero: str, archivo:str) -> bool:
       if id not in self.cancion_ids:
           return False
       for cancion in self.canciones:
           if cancion.id == id:
               song = cancion
       song.edit_cancion(titulo, artista, duracion, genero, archivo)
       return True
  
   def eliminar_cancion(self, id: int) -> bool:
       if id not in self.cancion_ids:
           return False
       self.canciones.remove([i for i in self.canciones if i.id == id][0])
       self.cancion_ids.remove(id)
       for lista in self.listas:
           if id in lista.canciones:
               lista.canciones.remove(id)
       return True
  
   def listar_canciones(self) -> list[Cancion]:
       return self.canciones
  
   def crear_lista(self, nombre: str) -> bool:
       if nombre not in [lista.nombre for lista in self.listas]:
           self.listas.append(ListaReproduccion(nombre))
           return True
       return False
  
   def borrar_lista(self, nombre: str) -> bool:
       for lista in self.listas:
           if lista.nombre == nombre:
               self.listas.remove(lista)
               return True
       return False
   
   def obtener_lista(self, nombre:str) -> ListaReproduccion:
       for lista in self.listas:
           if lista.nombre == nombre:
               return lista
