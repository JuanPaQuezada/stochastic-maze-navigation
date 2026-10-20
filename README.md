# stochastic-maze-navigation
An autonomous maze-solving system featuring probabilistic occupancy grids, stochastic terrain generation, and real-time pathfinding using optimized A* and D* algorithms, adding probabilistic noise [...]
```mermaid
flowchart TD
    %% Estilos de nodos
    classDef startEnd fill:#F1C40F,stroke:#D68910,stroke-width:2px,color:#000;
    classDef process fill:#3498DB,stroke:#2980B9,stroke-width:2px,color:#fff;
    classDef condition fill:#E67E22,stroke:#D35400,stroke-width:2px,color:#fff;
    classDef sub fill:#9B59B6,stroke:#8E44AD,stroke-width:2px,color:#fff;

    %% Flujo principal
    START([Inicio de la partida]):::startEnd
    M1_INIT["Módulo 1: Inicializar grilla N × M"]:::process

    START --> M1_INIT
    M1_INIT --> M1_NOISE["Calcular ruido continuo Perlin / Gaussiano"]:::process
    M1_NOISE --> M1_CELL{"¿Ruido > umbral?"}:::condition

    M1_CELL -->|Sí| M1_WALL["Asignar obstáculo infranqueable<br/>Costo = ∞"]:::process
    M1_CELL -->|No| M1_COST["Asignar terreno continuo<br/>Costo ≥ 1"]:::process

    M1_WALL --> M1_WAVE["Ejecutar validador Wavefront desde la meta"]:::sub
    M1_COST --> M1_WAVE

    M1_WAVE --> M1_VALID{"¿Camino abierto y resoluble?"}:::condition
    M1_VALID -->|Falso| M1_INIT
    M1_VALID -->|Verdadero| M3_MODE["Módulo 3: Seleccionar modo de juego"]:::process

    %% Modos de juego
    M3_MODE --> M3_CHOICE{"¿Qué modo?"}:::condition

    M3_CHOICE -->|MvM| M2_MVM["Competencia autónoma:<br/>A* con Manhattan vs. D* / Wavefront"]:::process
    M3_CHOICE -->|HvM| M2_HVM["Humano vs. CPU en tiempo real"]:::process
    M3_CHOICE -->|HvH| M2_HVH["Multijugador local manual"]:::process

    %% Motor de navegación
    M2_MVM --> M2_ASTAR
    M2_HVM --> M2_ASTAR
    M2_ASTAR["Módulo 2: Motor A*<br/>Evalúa f(n) = g(n) + h(n)"]:::sub

    M2_ASTAR --> M2_LOOP{"¿Lista abierta OPEN vacía?"}:::condition
    M2_LOOP -->|Sí| M4_ERR["Módulo 4: Reportar error de ruta"]:::process
    M2_LOOP -->|No| M2_POP["Extraer nodo con menor f(n)"]:::process

    M2_POP --> M2_META{"¿Nodo actual = meta?"}:::condition
    M2_META -->|Sí| M4_METRICS["Módulo 4: Trazar camino y desplegar métricas<br/>(ms, nodos)"]:::process
    M2_META -->|No| M2_EXPAND["Expandir vecinos ortogonales<br/>y sumar costos c"]:::process

    M2_EXPAND --> M2_DYN{"¿Ocurre un evento estocástico<br/>o cambia el mapa?"}:::condition
    M2_DYN -->|Sí| M2_DSTAR["Replanificación inversa con D*"]:::sub
    M2_DYN -->|No| M2_LOOP

    M2_DSTAR --> M2_LOOP

    %% Finalización
    M4_ERR --> END([Fin de la partida]):::startEnd
    M2_HVH --> M4_METRICS
    M4_METRICS --> END
```
