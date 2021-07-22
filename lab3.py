#!/usr/bin/env python3

import pickle
# NO ADDITIONAL IMPORTS ALLOWED!

# Note that part of your checkoff grade for this lab will be based on the
# style/clarity of your code.  As you are working through the lab, be on the
# lookout for things that would be made clearer by comments/docstrings, and for
# opportunities to rearrange aspects of your code to avoid repetition (for
# example, by introducing helper functions).


def transform_data(raw_data):
    edges = {} # actor: {set of actors that they have acted with}
    movies = {} # (actor1,actor2): movie they acted together in  
    actors_in_movies = {} # movie: {set of actors in that movie}
    for tup in raw_data:
        a1,a2,movie = tup
        if a1 not in edges:
            edges[a1] = {a2,}
        else:
            edges[a1].add(a2)
        if a2 not in edges:
            edges[a2] = {a1,}
        else:
            edges[a2].add(a1)
        
        movies[(a1,a2)] = movie
        movies[(a2,a1)] = movie
        
        if movie not in actors_in_movies:
            actors_in_movies[movie] = {a1,a2}
        else:
            actors_in_movies[movie].add(a1)
            actors_in_movies[movie].add(a2)
        
    return (edges,movies,actors_in_movies)



def acted_together(data_tup, actor_id_1, actor_id_2):
    data = data_tup[0] # need to check whether there is an edge connecting the two actors
    if actor_id_1 == actor_id_2: # actor has obviously acted with self
        return True    
    if actor_id_2 in data[actor_id_1]: # if actor_id_2 is in the set of actors that actor_id_1 has acted with, return True, else False
        return True
    else:
        return False


def actors_with_bacon_number(data_tup, n):
    assert n >= 0 #negative bacon numbers don't exist
    data = data_tup[0] # access edges
    seen = {actor: False for actor in data.keys()} # have not seen any actors
    seen[4724] = True # starting with Kevin Bacon, so we have seen him
    distance_list = [{4724,},] # list of sets, the index of the set indicates the distance from Kevin Bacon. Only Bacon is in the set at index 0

    while len(distance_list[-1]) != 0: # while the most recently generated set is nonempty, check for actors that we have not seen
        distance_list.append(set()) # append empty set for next group of actors with 1 higher bacon number
        for i in distance_list[-2]: 
            for j in data[i]:
                if not seen[j]:
                    distance_list[-1].add(j)
                    seen[j] = True # after processing, we have seen them
    if n >= len(distance_list):
        return set() # return empty set if out of range
    return distance_list[n]



def bacon_path(data_tup, actor_id):
    data = data_tup[0]
    seen = {actor: False for actor in data.keys()}
    seen[4724] = True
    parent = {4724:4724}
    distance_list = [{4724,},]

    # rerun BFS from actors_with_bacon_number but maintain a parent dictionary
    while len(distance_list[-1]) != 0:
        distance_list.append(set())
        for i in distance_list[-2]:
            for j in data[i]:
                if not seen[j]:
                    distance_list[-1].add(j)
                    parent[j] = i
                    seen[j] = True
    
    if actor_id not in parent: # if we did not encounter actor_id, then it has no parent and we cannot reach this actor from Kevin Bacon
        return None

    rV = [actor_id]
    while rV[-1] != 4724: # last element of the path (currently in reverse order) should be the starting point, which is Kevin Bacon
        rV.append(parent[rV[-1]])
    
    rV.reverse()

    return rV

def actor_to_actor_path(data_tup, actor_id_1, actor_id_2):
    # this function is the exact same as bacon_path except that the starting point is now arbitrary. Replace 4724 (Kevin Bacon) with actor_id_1
    # bacon_path could be simplified to actor_to_actor_path(data_tup, 4724, actor_id)
    data = data_tup[0]
    seen = {actor: False for actor in data.keys()}
    seen[actor_id_1] = True
    parent = {actor_id_1:actor_id_1}
    distance_list = [{actor_id_1,},]

    while len(distance_list[-1]) != 0:
        distance_list.append(set())
        for i in distance_list[-2]:
            for j in data[i]:
                if not seen[j]:
                    distance_list[-1].add(j)
                    parent[j] = i
                    seen[j] = True
    
    if actor_id_2 not in parent:
        return None

    rV = [actor_id_2]
    while rV[-1] != actor_id_1:
        rV.append(parent[rV[-1]])
    
    rV.reverse()

    return rV

def movie_path(data_tup, actor_id_1, actor_id_2):
    # create actor path, then convert actor path into a path of movies using the actor pairs
    path = actor_to_actor_path(data_tup, actor_id_1, actor_id_2)
    movies_dict = data_tup[1]

    rV = []
    for i in range(len(path)-1):
        rV.append(movies_dict[(path[i],path[i+1])])
    
    return rV



def actor_path(data_tup, actor_id_1, goal_test_function):
    data = data_tup[0]
    seen = {actor: False for actor in data.keys()}
    seen[actor_id_1] = True
    parent = {actor_id_1:actor_id_1}
    distance_list = [{actor_id_1,},]

    if goal_test_function(actor_id_1): # if the starting actor satisfies the goal, then just return the actor and that path
        return [actor_id_1,]

    while len(distance_list[-1]) != 0: # rerun BFS while maintaining parent pointers, the BFS returns a path to the first actor that it finds that satisfies the goal
        distance_list.append(set())
        for i in distance_list[-2]:
            for j in data[i]:
                if not seen[j]:
                    distance_list[-1].add(j)
                    parent[j] = i
                    seen[j] = True
                    if goal_test_function(j):
                        rV = [j,]
                        while rV[-1] != actor_id_1:
                            rV.append(parent[rV[-1]])
                        rV.reverse()
                        return rV
    
    return None # BFS has finished, did not already return a value which indicates that no reachable actors from actor_id_1 satisfy the goal

def actors_connecting_films(data_tup, film1, film2):
    actors_in_movies = data_tup[2]
    def goal(actor_id): # goal function to be passed into actor_path
        if actor_id in actors_in_movies[film2]:
            return True
        else:
            return False
    
    lists = []
    for actor in actors_in_movies[film1]: # generate a list of lists that contain the path from each actor in film1 to the closest actor in film2
        lists.append(actor_path(data_tup,actor,goal))
    
    max_length = float('inf')
    index = 0
    for i in range(len(lists)): # for loop iterates over the list of lists to find the shortest path
        if lists[i] != None:
            if len(lists[i]) < max_length:
                max_length = len(lists[i])
                index = i
    
    return lists[index]


if __name__ == '__main__':
    with open('resources/large.pickle', 'rb') as f:
        largedb = pickle.load(f)
    
    largedb_transformed = transform_data(largedb)

    with open('resources/small.pickle', 'rb') as f:
        smalldb = pickle.load(f)
    
    smalldb_transformed = transform_data(smalldb)
    
    with open('resources/tiny.pickle', 'rb') as f:
        tinydb = pickle.load(f)

    tinydb_transformed = transform_data(tinydb)

    with open('resources/movies.pickle','rb') as f:
        moviesdb = pickle.load(f)
    
    reverse_moviesdb = {v:k for k,v in moviesdb.items()}

    with open('resources/names.pickle','rb') as f:
        namesdb = pickle.load(f)
    
    reverse_namesdb = {v: k for k,v in namesdb.items()}

    print(tinydb_transformed[0])

    print(actor_to_actor_path(tinydb_transformed,1532,1640))
    
    # print(acted_together(smalldb_transformed,namesdb['Noureddine El Ati'],namesdb['Theresa Russell']))

    # print(acted_together(smalldb_transformed,namesdb['Barbara Flynn'],namesdb['Philip Bosco']))
    
    # print(namesdb['Laurence Luckinbill'])

    #large_bacon_6 = actors_with_bacon_number(largedb_transformed,6)

    #print(large_bacon_6)

    #names_large_bacon_6 = set(reverse_namesdb[x] for x in large_bacon_6)
    
    #print(names_large_bacon_6)

    #print(bacon_path(tinydb_transformed,1640))

    #zjd_path = bacon_path(largedb_transformed, namesdb['Zhi-Jian Deng'])

    #print([reverse_namesdb[x] for x in zjd_path])

    #brigitte_to_mike = actor_to_actor_path(largedb_transformed, namesdb['Brigitte Eves'], namesdb['Mike Miller'])

    # print([reverse_namesdb[x] for x in brigitte_to_mike])
    # print(actor_to_actor_path(largedb_transformed,10526,19534))
    # print(reverse_namesdb[59204])

    #movie_titles = movie_path(largedb_transformed, namesdb['Terry Kinney'], namesdb['Vjeran Tin Turk'])

    #print([reverse_moviesdb[x] for x in movie_titles])

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    pass
