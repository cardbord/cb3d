def calc_rel_distance(arr,runtime_dis):
    return sum([runtime_dis.observer.calc_dist_topoint(arr.rpoints[i]) for i in arr.raw_rotates]) / len(arr.raw_rotates) #avg distance


def quicksort(array):
    if len(array) <= 1:
        return array
    else:
        pivot = array[0]
        
        left = [x for x in array[1:] if x >= pivot]
        right = [x for x in array[1:] if x < pivot]
        return quicksort(left) + [pivot] + quicksort(right)