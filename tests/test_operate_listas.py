import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from operate import OperateClient
from musica.plataforma import PlataformaMusical, ListaReproduccion


def test_deal_with_lista_added_deleted_changed():
    # Setup: old lists A, B
    a = ListaReproduccion('A')
    a.anadir_cancion(1)
    b_old = ListaReproduccion('B')
    b_old.anadir_cancion(2)

    # New lists: B modified, C added
    b_new = ListaReproduccion('B')
    b_new.anadir_cancion(2)
    b_new.changed = True
    c_new = ListaReproduccion('C')
    c_new.anadir_cancion(3)

    op = OperateClient('dummy_path')
    op.ini_lista = [a, b_old]
    op.plata = PlataformaMusical(canciones=[], listas=[b_new, c_new], cancion_ids=[])
    l_old = op.ini_lista
    l_total = [i for i in l_old if i not in op.plata.listas] + op.plata.listas

    op.deal_with_lista(l_old, l_total)

    assert 'A' in op.data['listas']['eliminar']
    assert 'B' in op.data['listas']['nuevo']
    assert 'C' in op.data['listas']['nuevo']


if __name__ == '__main__':
    test_deal_with_lista_added_deleted_changed()
    print('test passed')
