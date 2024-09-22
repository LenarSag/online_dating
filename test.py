def findWords(words: list[str]) -> list[str]:
    upper = set('qwertyuiop')
    middle = set('asdfghjkl')
    bottom = set('zxcvbnm')

    lst = []

    for word in words:
        s = set(word.lower())
        if s.issubset(upper):
            lst.append(word)
            break
        elif s.issubset(middle):
            lst.append(word)
            break
        elif s.issubset(bottom):
            lst.append(word)
            break

    return lst


words = ['Hello', 'Alaska', 'Dad', 'Peace']
print(findWords(words))
