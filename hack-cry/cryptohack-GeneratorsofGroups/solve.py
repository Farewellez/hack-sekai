p = 28151

def find_primitive():
    for g in range(1,1000):
        unique = []
        is_primitive = True
        for i in range(p - 1):
            if pow(g,i,p) in unique:
                is_primitive = False
                break
            unique.append(pow(g,i,p))
        
        if is_primitive:
            print(len(unique))
            return g

primitive = find_primitive()
print(primitive)