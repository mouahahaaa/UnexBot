async def split_date(_str):
    L = [0, 0]
    L[0] = _str.split()[0]
    L[1] = _str.split()[1]
    D = L[0].split('/')
    T = L[1].split(':')
    X = [D, T]
    return X