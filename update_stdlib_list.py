# vim: expandtab tabstop=4 shiftwidth=4

from stdlib_list import stdlib_list

def good_lib(lib):
    if '.' in lib or '__' in lib or lib.startswith('_'):
        return False
    return True

if __name__ == "__main__":
    libs2 = [ lib.lower() for lib in stdlib_list("2.7") if good_lib(lib) ]
    libs3 = [ lib.lower() for lib in stdlib_list("3.6") if good_lib(lib) ]

    with open('ipydeps/data/libs2.txt', 'w') as f:
        for lib in libs2:
            f.write(lib + '\n')

    with open('ipydeps/data/libs3.txt', 'w') as f:
        for lib in libs3:
            f.write(lib + '\n')
