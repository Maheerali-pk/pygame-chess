
def add_tuples(tuple1, tuple2):
    res = []
    for i in range(len(tuple1)):
        res.append(tuple1[i] + tuple2[i])
    return tuple(res)


def add_tuple_list(list1, list2):
    res = []
    for i in range(len(list1)):
        res.append(add_tuples(list1[i], list2))
    return res
