#!/usr/bin/env python3

from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_auxiliary_structures(nodes_filename, ways_filename):
    """
    Create any auxiliary structures you are interested in, by reading the data
    from the given filenames (using read_osm_data)
    """
    # want a list of relevant nodes and a dictionary for edges
    # in order to find shortest path, also need edge_length
    edges = {} # node id: set of all nodes that it is connected to
    nodes = set() # set of all unique nodes that we encounter
    node_locs = {} # node id: (lat,lon)
    edge_length = {} # (node1_id, node2_id): length
    way_speed = {} # (node1_id, node2_id): speed_limit

    for way in read_osm_data(ways_filename):
        if 'highway' in way['tags'] and way['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
            # if way passes these two tests, then it should be considered
            node_list = way['nodes']
            nodes.update(node_list) # add all nodes along the nodes that we have encountered
            if 'oneway' in way['tags'] and way['tags']['oneway'] == 'yes': #if oneway
                oneway = True
            else:
                oneway = False
            for i in range(len(node_list)-1):
                node1 = node_list[i]
                node2 = node_list[i+1]
                if node1 not in edges:
                    edges[node1] = set()
                edges[node1].add(node2)

                if (node1,node2) not in way_speed:
                    if 'maxspeed_mph' in way['tags']:
                        way_speed[(node1,node2)] = way['tags']['maxspeed_mph']
                    else:
                        way_speed[(node1,node2)] = DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]
                else:
                    if 'maxspeed_mph' in way['tags'] and way['tags']['maxspeed_mph'] < way_speed[(node1,node2)]:
                        way_speed[(node1,node2)] = way['tags']['maxspeed_mph']
                    elif way_speed[(node1,node2)] < DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]:
                        way_speed[(node1,node2)] = DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]

                if not oneway:
                    if node2 not in edges:
                        edges[node2] = set()
                    edges[node2].add(node1)
                    if (node2,node1) not in way_speed:
                        if 'maxspeed_mph' in way['tags']:
                            way_speed[(node2,node1)] = way['tags']['maxspeed_mph']
                        else:
                            way_speed[(node2,node1)] = DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]
                    else:
                        if 'maxspeed_mph' in way['tags'] and way['tags']['maxspeed_mph'] < way_speed[(node2,node1)]:
                            way_speed[(node2,node1)] = way['tags']['maxspeed_mph']
                        elif way_speed[(node2,node1)] < DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]:
                            way_speed[(node2,node1)] = DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]


    for node in read_osm_data(nodes_filename):
        if node['id'] in nodes:
            node_locs[node['id']] = (node['lat'],node['lon'])
    
    for node1 in edges.keys():
        for node2 in edges[node1]:
            dist = great_circle_distance(node_locs[node1],node_locs[node2])
            edge_length[(node1,node2)] = dist
            edge_length[(node2,node1)] = dist
            if (node2,node1) not in way_speed:
                way_speed[(node2,node1)] = way_speed[(node1,node2)]
                
    return {'edges': edges, 'nodes': nodes, 'lengths': edge_length, 'coords': node_locs, 'wayspeed' : way_speed} 


def find_short_path_nodes(aux_structures, node1, node2):
    """
    Return the shortest path between the two nodes

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    edges = aux_structures['edges']
    # nodes = aux_structures['nodes']
    # coords = aux_structures['coords']
    lengths = aux_structures['lengths']

    # goal_dist = {x:great_circle_distance(coords[x],coords[node2]) for x in nodes}

    parents = {node1: node1}
    distances = {}
    final_distances = {node1:0}

    recent_node = node1

    while node2 not in final_distances:
        if recent_node in edges:
            for adj_node in edges[recent_node]:
                # print("=====")
                # print(recent_node, adj_node)
                if adj_node not in final_distances:
                    if adj_node not in distances:
                        distances[adj_node] = final_distances[recent_node] + lengths[(recent_node, adj_node)]
                        parents[adj_node] = recent_node
                    elif distances[adj_node] > final_distances[recent_node] + lengths[(recent_node, adj_node)]:
                        parents[adj_node] = recent_node
                        distances[adj_node] = final_distances[recent_node] + lengths[(recent_node, adj_node)]
                    # print('updated')
                    # print(adj_node)
                    # print(distances[adj_node])
        
        min_dist = float('inf')
        # heur_dist = float('inf')
        closest_node = 0
        updated = False

        for node in distances.keys():
            # print('distance for loop')
            # print(node)
            # print(distances[node])
            # print(distances[node] + goal_dist[node])
            # if distances[node] + goal_dist[node] < heur_dist
            # removed heuristic to implement fast
            if distances[node] < min_dist:
                closest_node = node
                min_dist = distances[node]
                # heur_dist = distances[node] + goal_dist[node]
                updated = True

        if not updated:
            return None
        
        # print('closest node',closest_node)
        recent_node = closest_node
        final_distances[closest_node] = min_dist
        distances.pop(closest_node)
    
    rV = [node2]
    while rV[-1] != node1:
        rV.append(parents[rV[-1]])
    
    rV.reverse()

    return rV

def find_closest_node(coords, loc):
        # takes dictionary that maps IDs to coordinates
        # takes tuple (lat,lon), returns ID of the closest node
        dist_loc = float('inf')
        closest_node = None
        for k in coords.keys():
            dist_k = great_circle_distance(coords[k],loc)
            if dist_k < dist_loc:
                dist_loc = dist_k
                closest_node = k
        return closest_node

def find_short_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """

    coords = aux_structures['coords']
    node1 = find_closest_node(coords,loc1)
    node2 =find_closest_node(coords,loc2)
    
    # print(coords)

    # print(node1,node2)

    node_path = find_short_path_nodes(aux_structures, node1, node2)
    if node_path == None:
        return None
    
    rV = [coords[elem] for elem in node_path]
    return rV
        
    


def find_fast_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    wayspeed = aux_structures['wayspeed']
    lengths = aux_structures['lengths']

    new_lengths = {k: lengths[k]/wayspeed[k] for k in lengths.keys()}

    # print(new_lengths)

    new_aux_structures = {'edges': aux_structures['edges'], 'nodes': aux_structures['nodes'], 'lengths': new_lengths, 'coords': aux_structures['coords'], 'wayspeed' : aux_structures['wayspeed']}

    return find_short_path(new_aux_structures, loc1, loc2)


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.

    """
    nodes =0
    for way in read_osm_data('resources/cambridge.ways'):
        if 'oneway' in way['tags'] and way['tags']['oneway'] == 'yes':
            nodes +=1
    print(nodes)
    """
    
    """
    print(great_circle_distance((42.363745,-71.100999),(42.361283,-71.239677)))
    
    for node in read_osm_data('resources/midwest.nodes'):
        if node['id']==233941454:
            node1 = (node['lat'],node['lon'])
        if node['id']==233947199:
            node2 = (node['lat'],node['lon'])
    print(great_circle_distance(node1,node2))
    """

    """
    for way in read_osm_data('resources/midwest.ways'):
        if way['id'] == 21705939:
            node_list = way['nodes']
            break
    total_dist = 0
    for i in range(len(node_list)-1):
        for node in read_osm_data('resources/midwest.nodes'):
            if node['id']==node_list[i]:
                node1 = (node['lat'],node['lon'])
            if node['id']==node_list[i+1]:
                node2 = (node['lat'],node['lon'])
        total_dist += great_circle_distance(node1,node2)
    print(total_dist)
    """

    """
    midwest = build_auxiliary_structures('resources/midwest.nodes', 'resources/midwest.ways')
    midwest_coords = midwest['coords']
    print(find_closest_node(midwest_coords, (41.4452463, -89.3161394)))
    """


    mit = build_auxiliary_structures('resources/mit.nodes','resources/mit.ways')
    
    print(find_fast_path(mit, (42.36, -71.0907), (42.3592, -71.0932)))

    """
    print("started building")
    cambridge = build_auxiliary_structures('resources/cambridge.nodes','resources/cambridge.ways')
    print(find_short_path_nodes(cambridge, 61321294, 567774187))
    """
    pass
