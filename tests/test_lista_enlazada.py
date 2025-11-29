import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from TADs import ListaEnlazada


def test_enlazar_and_redo_cleared():
    l = ListaEnlazada()
    l.enlazar(1)
    l.enlazar(2)
    l.enlazar(3)
    # undo once -> current should be 2
    assert l.deshacer() is True
    assert l.current.data == 2
    # redo once -> current should be 3
    assert l.rehacer() is True
    assert l.current.data == 3
    # undo twice -> back to 1
    assert l.deshacer() is True
    assert l.deshacer() is True
    assert l.current.data == 1
    # enalizar new data should clear redo chain
    l.enlazar(4)
    # after adding new node, redo should not be possible
    assert l.rehacer() is False
    assert l.current.data == 4


if __name__ == '__main__':
    test_enlazar_and_redo_cleared()
    print('test passed')
