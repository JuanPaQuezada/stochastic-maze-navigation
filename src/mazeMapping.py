import random
import zlib
import time
def space_hashing(x,y, density, seed):
    random.seed(seed)
    #cordinates of the cell 
    b_x=x//4
    b_y=y//4
    #generate deterministic hash value
    key=f"{b_x*73856093}_{b_y*19349663}_{seed}"
    #evaluate the cell state
    hash_value=zlib.crc32(key.encode('utf-8'))%100
    if hash_value<density*100:
        return float('inf')
    return 1.0



def get_cell_cost(x,y, carved_corridor,density, seed):
    if (x,y) in carved_corridor:
        return 1.0
    return space_hashing(x,y,density, seed)

class Map:
    def __init__(self, width, height, density_rate, hardness_rate, start, goal,seed=42):
        self.width = width
        self.height = height
        self.density_rate = density_rate
        self.hardness_rate=hardness_rate
        self.start=start
        self.goal=goal
        self.seed=seed
        self.ocupancy_grid=[[1.0 for _ in range((self.width))] for _ in range((self.height))]
        self.carved_corridors=set()
    def carve_corridor(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        min_x,max_x=min(x1,x2),max(x1,x2)
        for x in range(min_x,max_x+1):
            self.ocupancy_grid[y1][x]=1.0
            self.carved_corridors.add((x,y1))

        min_y, max_y=min(y1,y2),max(y1,y2)
        for y in range(min_y,max_y+1):
            self.ocupancy_grid[y][x2]=1.0
            self.carved_corridors.add((x2,y))
    def kruskal(self, k):
        random.seed(self.seed)
        points=set()
        #adding the start and goal points to the set tuple
        points.add(self.start)
        points.add(self.goal)
        while len(points)<k:
            x=random.randint(0,self.width-1)
            y=random.randint(0,self.height-1)
            points.add((x,y))
        p_coord=list(points)
        edges=[]
        #create edges with manhattan distance
        for i in range(len(p_coord)):
            for j in range(i+1,len(p_coord)):
                p1=p_coord[i]
                p2=p_coord[j]
                dist=abs(p1[0]-p2[0])+abs(p1[1]-p2[1])
                edges.append((dist,p1,p2))

        #sort edges by cost distance
        edges.sort(key=lambda x:x[0])

        #disjoint-set structure
        parent={p:p for p in p_coord}
        def find(p):
            if parent[p]!=p:
                parent[p]=find(parent[p])
            return parent[p]

        for dist,p1,p2 in edges:
            root1=find(p1)
            root2=find(p2)
            if root1!=root2:
                parent[root2]=root1
                self.carve_corridor(p1,p2)


    def generate_map(self):
        '''
           Generate the occupancy grid based on the density
           applying the space hashing function and making sure
           the path 
        '''
        #generate pseudorandom seed with time 
        dinamic_seed=int(time.thread_time_ns()//100)
        self.seed=dinamic_seed
        for y in range(self.height):
            for x in range(self.width):
                self.ocupancy_grid[y][x]=space_hashing(x,y,self.density_rate,self.seed)
        self.kruskal(k=10)
        self.ocupancy_grid[self.start[1]][self.start[0]]=1.0
        self.ocupancy_grid[self.goal[1]][self.goal[0]]=1.0
        return self.ocupancy_grid

    def print_map(self):
        for row in self.ocupancy_grid:
            print(' '.join(['#' if cell==float('inf') else '.' for cell in row]))
            # use '#' for walls and '.' for free space    

map = Map(width=50, height=50, density_rate=0.3, hardness_rate=0.5, start=(0, 0), goal=(49, 49), seed=42)
map.generate_map()
map.print_map()


