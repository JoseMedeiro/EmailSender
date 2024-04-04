def find_in_array_dict(l:list,k_v:dict,start = 0):
    if len(l) == 0:
        return -1
    for i, e in enumerate(l[start:]):
        eq = True
        for k in k_v:
            if e[k] != k_v[k]:
                eq = False
                break
        if eq:
            return i+start

    return -1

def unique_array_dict(l1:list,query_keys:list=['_id'])->list:
    l2 = list()
    for e in l1:
        query = {}
        for k in query_keys:
            query[k] = e['fields'][k]
        if find_in_array_dict(l2,query) == -1:
            l2.append(e)
    return l2

def force_list(v)->list:
    if not isinstance(v,list):
        return [v]
    return v