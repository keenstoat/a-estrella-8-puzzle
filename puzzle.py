#!/usr/bin/env python3

from copy import deepcopy
import os

class Node:
    name = ""
    g = None
    h = None
    tablero = None
    tablero_solucion = None
    parent = None
    childrenList = None
    iteration = "n/a"

    def get_h(self):
        if self.h:
            return self.h
        distance = 0
        for row_index, row in enumerate(self.tablero):
            for col_index, col in enumerate(row):
                distance += 1 if col != self.tablero_solucion[row_index][col_index] else 0
        self.h = distance
        return self.h

    def get_f(self):
        return self.g + self.get_h()

    def get_space_row_col(self):
        for row_index, row in enumerate(self.tablero):
            if 0 in row:
                return row_index, row.index(0)

    def move_space(self, direction):
        row, col = self.get_space_row_col()
        if direction == "u":
            if row == 0: return
            else: 
                new_row = row - 1
                new_col = col
        elif direction == "r":
            if col == 2: return
            else: 
                new_row = row
                new_col = col + 1
        elif direction == "d":
            if row == 2: return
            else: 
                new_row = row + 1
                new_col = col
        elif direction == "l":
            if col == 0: return
            else: 
                new_row = row
                new_col = col - 1
        else:
            return
        new_tablero = deepcopy(self.tablero)
        new_tablero[row][col] = new_tablero[new_row][new_col]
        new_tablero[new_row][new_col] = 0
        
        child = Node()
        child.g = self.g + 1
        child.name = f"{self.name}.{direction}"
        child.tablero = new_tablero
        child.tablero_solucion = self.tablero_solucion
        child.parent = self
        self.add_child(child)

    def expand(self):
        for dir in ["u", "r", "d", "l"]:
            self.move_space(dir)

    def get_children(self):
        return self.childrenList or []
        c = []
        if self.up: c.append(self.up)
        if self.right: c.append(self.right)
        if self.down: c.append(self.down)
        if self.left: c.append(self.left)
        return c
    
    def add_child(self, child):
        if not self.childrenList: 
            self.childrenList = []
        self.childrenList.append(child)

    def print_tablero(self):
        for row in self.tablero:
            for col in row:
                print(f"[{col}]", end="")
            print()
        print()

    def is_solucion(self):
        return self.get_h() == 0
        return self.tablero_solucion == self.tablero

    def get_graphviz_label(self):
        
        header = f"{{h={str(self.get_h())}| i={self.iteration} }}"
        labelList = [header]
        for row in self.tablero:
            labelList.append("{" + "|".join([str(row[0]),str(row[1]),str(row[2])]) + "}")

        mark_solucion = ", color=green" if self.is_solucion() else ""
        label = f'"{self.name}" [label="{{ {"|".join(labelList)} }}" {mark_solucion}];\n'
        return label




def create_arbol_dot(raiz, img_ext="png"):
    print("Creando tablero.dot ...")
    cola = [raiz]
    with open("tablero.dot", "w") as dot_file:
        dot_file.write("digraph {\nnode [shape=record];\n")
    
    while cola:
        nodo = cola.pop(0)
        graph_text = nodo.get_graphviz_label()
        for child in nodo.get_children():
            graph_text += child.get_graphviz_label()
            graph_text += f'"{nodo.name}" -> "{child.name}";\n'
            cola.append(child)
        with open("tablero.dot", "a") as dot_file:
            dot_file.write(graph_text)
    
    with open("tablero.dot", "a") as dot_file:
        dot_file.write("\n}")
    
    print("Creando tablero.png ...")
    os.system(f"dot -T{img_ext} tablero.dot -o tablero.{img_ext}")

def create_solucion_dot(nodo):

    print("Creando solucion.dot ...")
    with open("solucion.dot", "w") as dot_file:
        dot_file.write('digraph {\nnode [shape=record];\n')

    while nodo.parent:
        graph_text = nodo.parent.get_graphviz_label()
        graph_text += nodo.get_graphviz_label()
        graph_text += f'"{nodo.parent.name}" -> "{nodo.name}";\n'
        nodo = nodo.parent
        with open("solucion.dot", "a") as dot_file:
            dot_file.write(graph_text)
    
    with open("solucion.dot", "a") as dot_file:
        dot_file.write("\n}")
    
    print("Creando solucion.png ...")
    os.system("dot -Tpng solucion.dot -o solucion.png")

def a_estrella(tablero_inicial, tablero_final, max_iterations=-1):

    raiz = Node()
    raiz.name = "0"
    raiz.g = 0
    raiz.tablero = tablero_inicial
    raiz.tablero_solucion = tablero_final

    visitados = []
    cola = [raiz]
    i = 0
    while cola:
        
        i += 1
        nodo = cola.pop(0)
        nodo.iteration = i

        if max_iterations > -1 and i >= max_iterations:
            print(f"Iteraciones: {i}")
            return nodo, raiz

        if nodo.is_solucion():
            nodo.print_tablero()
            print(f"Iteraciones: {i}")
            return nodo, raiz

        visitados.append(nodo.tablero)

        def insert_in_order(nodo):
            inserted = False
            for pos in range(len(cola)):
                if cola[pos].get_f() > nodo.get_f():
                    cola.insert(pos, nodo)
                    inserted = True
                    break
            if not inserted: cola.append(nodo)

        nodo.expand()
        # print(f"children: {[x.name for x in nodo.children()]}")
        for child in nodo.get_children():
            if child.tablero not in visitados:
                insert_in_order(child)

    return None
    

tablero_inicial = [
    [8, 3, 5],
    [6, 7, 0],
    [2, 1, 4]
]
tablero_final = [
    [1, 2, 3],
    [8, 0, 4],
    [7, 6, 5]
]

nodo_solucion, raiz = a_estrella(tablero_inicial, tablero_final)

create_arbol_dot(raiz, img_ext="svg")
create_solucion_dot(nodo_solucion)
