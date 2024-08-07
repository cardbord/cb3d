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
    

def transform(points:list, draw_plane:str,extrusion:str='0',zerodisplacement:str='0'):
    plane_array = []
    extrusion=float(extrusion)
    zerodisplacement=float(zerodisplacement)
    match draw_plane:
        case 'xz':
            original_plane=[]
            extruded_plane=[]
            for point in points:
                original_plane.append([point[0],point[1],zerodisplacement])
                extruded_plane.append([point[0],point[1],extrusion+zerodisplacement])
            plane_array.append(original_plane)
            plane_array.append(extruded_plane)


            for i in range(1,len(points)):
                side_plane = []
                side_plane.extend([[points[i][0],points[i][1],zerodisplacement], [points[i][0],points[i][1],extrusion+zerodisplacement], [points[i-1][0],points[i-1][1],extrusion+zerodisplacement], [points[i-1][0],points[i-1][1],zerodisplacement]])
                plane_array.append(side_plane)
            side_plane = []
            side_plane.extend([[points[-1][0],points[-1][1],zerodisplacement], [points[-1][0],points[-1][1],extrusion+zerodisplacement], [points[0][0],points[0][1],extrusion+zerodisplacement], [points[0][0],points[0][1],zerodisplacement]])
            plane_array.append(side_plane)

        case 'xy':
            original_plane=[]
            extruded_plane = []
            for point in points:
                original_plane.append([point[0],zerodisplacement,point[1]])
                extruded_plane.append([point[0],extrusion+zerodisplacement,point[1]])
            plane_array.append(original_plane)
            plane_array.append(extruded_plane)


            for i in range(1,len(points)):
                side_plane = []
                side_plane.extend([[points[i][0],zerodisplacement,points[i][1]], [points[i][0],extrusion+zerodisplacement,points[i][1]], [points[i-1][0],extrusion+zerodisplacement,points[i-1][1]], [points[i-1][0],zerodisplacement,points[i-1][1]]])
                plane_array.append(side_plane)
            side_plane = []
            side_plane.extend([[points[-1][0],zerodisplacement,points[-1][1]], [points[-1][0],extrusion+zerodisplacement,points[-1][1]], [points[0][0],extrusion+zerodisplacement,points[0][1]], [points[0][0],zerodisplacement,points[0][1]]])
            plane_array.append(side_plane)
        
        case 'yz':
            original_plane=[]
            extruded_plane = []
            for point in points:
                original_plane.append([zerodisplacement,point[0],point[1]])
                extruded_plane.append([extrusion+zerodisplacement,point[0],point[1]])
            plane_array.append(original_plane)
            plane_array.append(extruded_plane)


            for i in range(1,len(points)):
                side_plane = []
                side_plane.extend([[zerodisplacement,points[i][0],points[i][1]], [extrusion+zerodisplacement,points[i][0],points[i][1]], [extrusion+zerodisplacement,points[i-1][0],points[i-1][1]], [zerodisplacement,points[i-1][0],points[i-1][1]]])
                plane_array.append(side_plane)
            side_plane = []
            side_plane.extend([[zerodisplacement,points[-1][0],points[-1][1]], [extrusion+zerodisplacement,points[-1][0],points[-1][1]], [extrusion+zerodisplacement,points[0][0],points[0][1]], [zerodisplacement,points[0][0],points[0][1]]])
            plane_array.append(side_plane)

    
    return plane_array