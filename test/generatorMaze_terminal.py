from src.mazeMapping import Map

if __name__ == "__main__":
    #Create a map with specified parameters
    map=Map(width=50,height=50,density_rate=0.3,hardness_rate=0.5,start=(0,0),goal=(49,49),seed=42)
    map.generate_map()
    map.print_map()



