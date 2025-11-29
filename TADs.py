from datetime import datetime
import os

class Nodo:
    def __init__(self, data, next=None, last=None):
        self.data = data
        self.next = next
        self.last = last

class Pila:
    def __init__(self):
        self.current = None
        self.size = 0

    def is_empty(self):
        return self.current is None
    
    def enpilar(self, data):
        nodo = Nodo(data, self.current)
        self.current = nodo
        self.size += 1

    def despilar(self):
        if self.is_empty():
            return None
        data = self.current.data
        self.current = self.current.next
        self.size -= 1
        return data
    
    def pilar_lista(self, lista: list, path: str):
        for i in lista:
            self.enpilar(os.path.join(path, i))

class ListaEnlazada:
    def __init__(self):
        self.current = None
        self.ultimo = None
        self.primero = None

    def enlazar(self, data):
        nodo = Nodo(data, None, self.current)
        temp = self.current.next if self.current else None
        if temp:
            siguiente = temp.next
            temp.last = temp.next = None
            temp = siguiente
        if self.current:
            self.current.next = nodo
        else:
            self.primero = nodo
        self.current = self.ultimo = nodo
    
    def deshacer(self):
        if self.current:
            if self.current.last:
                self.current = self.current.last
                return True
        return False
    
    def rehacer(self):
        if self.current:
            if self.current.next:
                self.current = self.current.next
                return True
        return False