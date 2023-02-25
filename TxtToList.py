with open('words.txt', 'r', encoding='UTF-8') as TXTFile:
    with open('words.py', 'w', encoding='UTF-8') as PYFile:
        wordsPY = 'mat = ['
        for word in TXTFile.readlines():
            wordsPY += f"'{word[0:-1]}', "
        wordsPY = wordsPY[0:-2] + ']'
        PYFile.write(wordsPY)
