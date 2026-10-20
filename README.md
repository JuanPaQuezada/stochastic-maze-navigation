# stochastic-maze-navigation
An autonomous maze-solving system featuring probabilistic occupancy grids, stochastic terrain generation, and real-time pathfinding using optimized A* and D* algorithms, adding probabilistic noise and random map
```mermaid
graph TD
    %% Estilos de Nodos
    classDef startEnd fill:#F1C40F,stroke:#D68910,stroke-width:2px,color:#000;
    classDef process fill:#3498DB,stroke:#2980B9,stroke-width:2px,color:#fff;
    classDef condition fill:#E67E22,stroke:#D35400,stroke-width:2px,color:#fff;
    classDef sub fill:#9B59B6,stroke:#8E44AD,stroke-width:2px,color:#fff;

    %% Flujo Principal
    START([Inicio de la Partida]) :::startEnd --> M1_INIT[Módulo 1: Inicializar Grilla N x M] :::process
    
    %% Generación de Entorno
    M1_INIT --> M1_NOISE[Calcular Ruido Continuo Perlin / Gaussiano] :::process
    M1_NOISE --> M1_CELL{¿Ruido > Umbral?} :::condition
    M1_CELL -- Sí --> M1_WALL[Asignar Obstáculo Infranqueable Costo = ∞] :::process
    M1_CELL -- No --> M1_COST[Asignar Terreno Continuo Costo >= 1] :::process
    
    M1_WALL --> M1_WAVE[Ejecutar Validador Wavefront desde Meta] :::sub
    M1_COST --> M1_WAVE
    
    M1_WAVE --> M1_VALID{¿Camino Abierto y Resoluble?} :::condition
    M1_VALID -- Falso --> M1_INIT
    M1_VALID -- Verdadero --> M3_MODE[Módulo 3: Seleccionar Modo de Juego] :::process

    %% Modos de Juego
    M3_MODE --> M3_CHOICE{¿Qué Modo?} :::condition
    
    M3_CHOICE -- MvM --> M2_MvM[Competencia Autónoma: A* con Manhattan vs D* / Wavefront] :::process
    M3_CHOICE -- HvM --> M2_HvM[Humano vs CPU en Tiempo Real] :::process
    M3_CHOICE -- HvH --> M2_HvH[Multijugador Local Manual] :::process

    %% Motor de Navegación (PC)
    M2_MvM --> M2_ASTAR[Módulo 2: Motor A* evalúa f n = g n + h n] :::sub
    M2_HvM --> M2_ASTAR
    
    M2_ASTAR --> M2_LOOP{¿Lista Abierta OPEN Vacía?} :::condition
    M2_LOOP -- Sí --> M4_ERR[Módulo 4: Reportar Error de Ruta] :::process
    M2_LOOP -- No --> M2_POP[Extraer Nodo con Menor f n] :::process
    
    M2_POP --> M2_META{¿Nodo Actual == Meta?} :::condition
    M2_META -- Sí --> M4_METRICS[Módulo 4: Trazar Camino y Desplegar Métricas ms, Nodos] :::process
    M2_META -- No --> M2_EXPAND[Expandir Vecinos Ortogonales y Sumar Costos c] :::process
    
    M2_EXPAND --> M2_DYN{¿Ocurre Evento Estocástico / Cambio en Mapa?} :::condition
    M2_DYN -- Sí --> M2_DSTAR[Replanificación Inversa con D*] :::sub
    M2_DYN -- No --> M2_LOOP
    
    M2_DSTAR --> M2_LOOP
    
    M4_ERR --> END([Fin de la Partida]) :::startEnd
    M2_HvH --> M4_METRICS
    M4_METRICS --> END
```
