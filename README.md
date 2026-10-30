# stochastic-maze-navigation
An autonomous maze-solving system featuring probabilistic occupancy grids, stochastic terrain generation, and real-time pathfinding using optimized A* and D* algorithms with probabilistic noise.

## Spatial Generation and Computational Cost Reduction

The `Map` class implements the representation and generation of the navigation environment through a stochastic occupancy grid. Instead of determining the state of each cell using a sequential random process, the system uses spatial hashing to calculate each cell's value independently based on its position and a seed.

This procedure generates values that appear random while remaining reproducible and consistent for the same position and seed. The primary advantage is that a cell's state can be obtained on demand without storing the entire map or iterating through all previous cells, reducing memory usage and computational overhead.

The `get_cell_cost` function adds an important exception to the probabilistic model: positions belonging to `carved_corridors` always receive a cost of `1.0`, even if the hash would otherwise classify them as obstacles or high-cost terrain. This guarantees that the generated maze contains traversable routes for the navigation algorithms.

From a scientific perspective, the design separates two processes with different purposes: *spatial hashing* deterministically controls the distribution of obstacles, while the path-carving process guarantees connectivity and solvability. This combination provides both stochastic variability and reproducible experiments.
<p align="center">
    <img width="1030" height="959" alt="image" src="https://github.com/user-attachments/assets/fc97a803-733a-498f-b10b-a83800ac1200" />
</p>

```mermaid
flowchart TD
    %% Node styles
    classDef startEnd fill:#F1C40F,stroke:#D68910,stroke-width:2px,color:#000;
    classDef process fill:#3498DB,stroke:#2980B9,stroke-width:2px,color:#fff;
    classDef condition fill:#E67E22,stroke:#D35400,stroke-width:2px,color:#fff;
    classDef sub fill:#9B59B6,stroke:#8E44AD,stroke-width:2px,color:#fff;

    %% Main flow
    START([Game start]):::startEnd
    M1_INIT["Module 1: Initialize an N × M grid"]:::process

    START --> M1_INIT
    M1_INIT --> M1_NOISE["Calculate continuous Perlin / Gaussian noise"]:::process
    M1_NOISE --> M1_CELL{"Is noise > threshold?"}:::condition

    M1_CELL -->|Yes| M1_WALL["Assign impassable obstacle<br/>Cost = ∞"]:::process
    M1_CELL -->|No| M1_COST["Assign continuous terrain<br/>Cost ≥ 1"]:::process

    M1_WALL --> M1_WAVE["Run the Wavefront validator from the goal"]:::sub
    M1_COST --> M1_WAVE

    M1_WAVE --> M1_VALID{"Is there an open and solvable path?"}:::condition
    M1_VALID -->|False| M1_INIT
    M1_VALID -->|True| M3_MODE["Module 3: Select game mode"]:::process

    %% Game modes
    M3_MODE --> M3_CHOICE{"Which mode?"}:::condition

    M3_CHOICE -->|MvM| M2_MVM["Autonomous competition:<br/>A* with Manhattan vs. D* / Wavefront"]:::process
    M3_CHOICE -->|HvM| M2_HVM["Human vs. CPU in real time"]:::process
    M3_CHOICE -->|HvH| M2_HVH["Local manual multiplayer"]:::process

    %% Navigation engine
    M2_MVM --> M2_ASTAR
    M2_HVM --> M2_ASTAR
    M2_ASTAR["Module 2: A* engine<br/>Evaluates f(n) = g(n) + h(n)"]:::sub

    M2_ASTAR --> M2_LOOP{"Is the OPEN list empty?"}:::condition
    M2_LOOP -->|Yes| M4_ERR["Module 4: Report route error"]:::process
    M2_LOOP -->|No| M2_POP["Extract the node with the lowest f(n)"]:::process

    M2_POP --> M2_META{"Is the current node the goal?"}:::condition
    M2_META -->|Yes| M4_METRICS["Module 4: Trace the path and display metrics<br/>(ms, nodes)"]:::process
    M2_META -->|No| M2_EXPAND["Expand orthogonal neighbors<br/>and add traversal costs c"]:::process

    M2_EXPAND --> M2_DYN{"Does a stochastic event occur<br/>or does the map change?"}:::condition
    M2_DYN -->|Yes| M2_DSTAR["Reverse replanning with D*"]:::sub
    M2_DYN -->|No| M2_LOOP

    M2_DSTAR --> M2_LOOP

    %% Completion
    M4_ERR --> END([End of game]):::startEnd
    M2_HVH --> M4_METRICS
    M4_METRICS --> END
```

To generate the pseudorandom maze dynamically, the `generate_map` method uses Python's `time` library to create a seed from `time.thread_time_ns()`. This value is assigned to `self.seed`, allowing each maze generation to use a different time-based seed while preserving deterministic spatial hashing and corridor generation for that specific maze.
