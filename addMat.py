from mat import mat

new = []
while True:
    to_add = input('Введите матное слово: ')
    if to_add not in mat and to_add not in new and to_add != 'add':
        add = input(f'Добавить? {to_add} (y/n): ')
        if add == 'y':
            new.append(to_add)
            new.sort()
    elif to_add == 'add':
        add = input(f'Добавить? {new} (y/n): ')
        if add == 'y':
            mat += new
            mat.sort()
            with open('mat.py', 'w', encoding='UTF-8') as words:
                mat = f'mat = {str(mat)}'
                words.write(str(mat))
                break
