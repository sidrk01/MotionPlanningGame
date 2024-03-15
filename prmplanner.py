# prmplanner.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to the author.
# 
# Authors: Ioannis Karamouzas (ioannis@cs.ucr.edu)
#

from graph import RoadmapVertex, RoadmapEdge, Roadmap
from utils import *

disk_robot = True #(change this to False for part II) 


obstacles = None # the obstacles 
robot_radius = None # the radius of the robot
robot_width = None # the width of the OBB robot (advanced extension)
robot_height = None # the height of the OBB robot (advanced extension)


# ----------------------------------------
# modify the code below
# ----------------------------------------

# Construction phase: Build the roadmap
# You should incrementally sample configurations according to a strategy and add them to the roadmap, 
# select the neighbors of each sample according to a distance function and strategy, and
# attempt to connect the sample to its neighbors using a local planner, leading to corresponding edges
# See graph.py to get familiar with the Roadmap class  

def build_roadmap(q_range, robot_dim, scene_obstacles):

    global obstacles, robot_width, robot_height, robot_radius

    obstacles = scene_obstacles # setting the global obstacle variable

    x_limit = q_range[0] # the range of x-positions for the robot
    y_limit = q_range[1] # the range of y-positions for the robot
    theta_limit = q_range[2] # the range of orientations for the robot (advanced extension)

    robot_width, robot_height = robot_dim[0], robot_dim[1] # the dimensions of the robot, represented as an oriented bounding box
    
    robot_radius = max(robot_width, robot_height)/2.

    # the roadmap 
    graph = Roadmap()
    samples = 100
    k = 10

    for _ in range(samples):
        if disk_robot:
            q = (np.random.uniform(x_limit[0], x_limit[1]), np.random.uniform(y_limit[0], y_limit[1]))
        else:
             q = (np.random.uniform(x_limit[0], x_limit[1]), np.random.uniform(y_limit[0], y_limit[1]), np.random.uniform(theta_limit[0], theta_limit[1]))
        if not collision(q):
            new_v = graph.addVertex(q)
            neighbors = k_nearest_neighbors(graph, q, K=k)
            for neighbor in neighbors:
                if coll_free_path(q, neighbor.q):
                    graph.addEdge(new_v, neighbor, distance(q, neighbor.q))
    # uncomment this to export the roadmap to a file
    graph.saveRoadmap("prm_roadmap.txt")
    return graph

# ----------------------------------------
# modify the code below
# ----------------------------------------

# Query phase: Connect start and goal to roadmap and find a path using A*
# (see utils for Value, PriorityQueue, OrderedSet classes that you can use as in project 3)
# The returned path should be a list of configurations, including the local paths along roadmap edges
# Make sure that start and goal configurations are collision-free. Otherwise return None
    
def find_path(q_start, q_goal, graph):
    path  = []    

    if collision(q_start) or collision(q_goal):
        return None

    start_v = graph.addVertex(q_start)
    goal_v = graph.addVertex(q_goal)

    for v in [start_v, goal_v]:
        neighbors = k_nearest_neighbors(graph, v.q, K=10)
        for neighbor in neighbors:
            if coll_free_path(v.q, neighbor.q):
                graph.addEdge(v, neighbor, distance(v.q, neighbor.q))
                graph.addEdge(neighbor, v, distance(neighbor.q, v.q))

    path = astar(graph, start_v, goal_v)

    graph.removeVertex(start_v.id)
    graph.removeVertex(goal_v.id)
    return path   

# ----------------------------------------
# below are some functions that you may want to populate/modify and use above 
# ----------------------------------------

def nearest_neighbors(graph, q, max_dist=10.0):
    """
        Returns all the nearest roadmap vertices for a given configuration q that lie within max_dist units
        You may also want to return the corresponding distances 
    """
    neighbors = []
    distances = []
    for v in graph.getVertices():
        d = distance(q, v.q)
        if d < max_dist:
            neighbors.append(v)
            distances.append(d)
    return neighbors, distances


def k_nearest_neighbors(graph, q, K=10):
    """
        Returns the K-nearest roadmap vertices for a given configuration q. 
        You may also want to return the corresponding distances 
    """
    if disk_robot:
        q = q[:2]
        distances = [(v, distance(q, v.q[:2])) for v in graph.getVertices()]
    else:
        distances = [(v, distance(q, v.q)) for v in graph.getVertices()]

    distances.sort(key=lambda x: x[1])
    neighbors = [v for v, _ in distances[:K]]
    return neighbors
  
def distance (q1, q2): 
    """
        Returns the distance between two configurations. 
        You may want to look at the getRobotPlacement function in utils.py that returns the OBB for a given configuration  
    """
    if disk_robot:
        q1 = q1[:2]
        q2 = q2[:2]
        return np.linalg.norm(np.array(q1) - np.array(q2))
    else:
        trans_dist = np.linalg.norm(np.array(q1[:2]) - np.array(q2[:2]))
        rot_dist = min(abs(q1[2] - q2[2]), 2*np.pi - abs(q1[2] - q2[2]))
        weight = 0.5
        return (1 - weight)*trans_dist + weight*rot_dist

def collision(q):
    """
        Determines whether the robot placed at configuration q will collide with the list of AABB obstacles.  
    """
    for obstacle in obstacles:
        if (obstacle.x_min - robot_radius) <= q[0] <= (obstacle.x_max + robot_radius) and (obstacle.y_min - robot_radius) <= q[1] <= (obstacle.y_max + robot_radius):
            return True 
    return False
   

def interpolate (q1, q2, stepsize):
    """
        Returns an interpolated local path between two given configurations. 
        It can be used to determine whether an edge between vertices is collision-free. 
    """
    interpolated_path = []
    t = 0

    min_length = min(len(q1), len(q2))
    q1, q2 = q1[:min_length], q2[:min_length]
    while t <= 1:
        interpolated_path.append((1-t)*np.array(q1) + t*np.array(q2))
        t += stepsize
    return interpolated_path


#connecting path helper functions
def coll_free_path (q1, q2, stepsize=0.1):
    interpolated_path = interpolate(q1, q2, stepsize)
    for q in interpolated_path:
        if collision(q):
            return False
    return True

def connect (graph, v, K= 10):
    neighbors = k_nearest_neighbors(graph, v.q, K=K)
    for neighbor in neighbors:
        if neighbor != v and not graph.edgeExists(v, neighbor):
            if not any(collision(q) for q in interpolate(v.q, neighbor.q, 0.1)):
                graph.addEdge(v, neighbor, distance(v.q, neighbor.q), interpolate(v.q, neighbor.q, 0.1))
    
# search functions
def heuristic (q1, q2):
    return distance(q1, q2)

def reconstruct_path(came_from, start, goal):
    current = goal
    path = [current.q]
    while current in came_from:
        current = came_from[current]
        path.insert(0, current.q)
    return path

def astar(graph, start, goal):
    open_set = PriorityQueue(order=min, f=lambda v: v.f)
    closed_set = OrderedSet()
    came_from = {}
    g_score = {v: float("inf") for v in graph.getVertices()}
    g_score[start] = 0
    f_score = {start: heuristic(start.q, goal.q)}

    open_set.put(start, Value(f_score[start], g_score[start]))

    while not open_set.empty():
        current = open_set.pop()[0]

        if current == goal:
            return reconstruct_path(came_from, start, goal)
            
        
        closed_set.add(current)

        for neighbor in graph.getVertexNeighbors(current):
            if neighbor in closed_set:
                continue
            tentative_g_score = g_score[current] + distance(current.q, neighbor.q)

            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor.q, goal.q)

                if neighbor not in open_set or f_score[neighbor] < open_set.get(neighbor).f:
                    open_set.put(neighbor, Value(f_score[neighbor], g_score[neighbor]))
    
    return None

if __name__ == "__main__":
    from scene import Scene
    import tkinter as tk

    win = tk.Tk()
    Scene('maze.csv', disk_robot, (build_roadmap, find_path), win)
    win.mainloop()
