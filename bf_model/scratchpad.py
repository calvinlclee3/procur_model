def someFunc(input):
    input['b'] = 4
    input['a'] = "modified"

if __name__ == "__main__":
    dictA = {'a' : 3}
    someFunc(dictA)
    print(f'{dictA}')