from src.mazeMapping import Map

map = Map(width=50, height=50, density_rate=0.6, hardness_rate=0.7, start=(0, 0), goal=(49, 49), seed=42)
map.generate_map()
map.print_map()


