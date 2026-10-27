# stochastic-maze-navigation
An autonomous maze-solving system featuring probabilistic occupancy grids, stochastic terrain generation, and real-time pathfinding using optimized A* and D* algorithms, adding probabilistic noise

## Generación espacial y reducción del costo computacional

La clase `Map` implementa la representación y generación del entorno de navegación mediante una grilla de ocupación estocástica. En lugar de decidir el estado de cada celda utilizando una secuencia de números aleatorios que deba conservarse explícitamente, se utiliza una función de *space hashing* basada en las coordenadas espaciales y en una semilla fija. Cada posición `(x, y)` se asocia primero con un bloque espacial de tamaño `4 × 4` mediante `x // 4` y `y // 4`; posteriormente, las coordenadas del bloque se combinan con constantes enteras y la semilla para construir una clave determinista. Sobre esa clave se calcula un valor hash mediante `zlib.crc32`, y el resultado se normaliza al intervalo `[0, 100)`. Si el valor obtenido es menor que `density_rate × 100`, la celda se clasifica como obstáculo con costo `∞`; en caso contrario, se le asigna un costo transitable igual a `1.0`.

Este procedimiento permite generar valores aparentemente aleatorios, pero reproducibles y consistentes para una misma posición y semilla. La ventaja principal es que el estado de una celda puede obtenerse directamente a partir de sus coordenadas, sin recorrer una estructura adicional de números aleatorios ni almacenar una distribución completa para consultar posteriormente cada ubicación. La operación de consulta tiene costo constante, `O(1)`, y la memoria auxiliar utilizada por el mecanismo de hashing es constante, `O(1)`. Por tanto, aunque la materialización completa de la matriz sigue requiriendo `O(NM)` operaciones cuando se llena toda la grilla, el cálculo de cada celda es independiente, directo y fácilmente paralelizable. Además, el mismo modelo puede utilizarse de forma perezosa durante la exploración: una celda se evalúa únicamente cuando el algoritmo de navegación la necesita. Esto evita trabajo innecesario en regiones que no son visitadas por A* o D* y resulta especialmente útil en mapas grandes o dinámicos.

La función `get_cell_cost` añade una excepción importante al modelo probabilístico: las posiciones pertenecientes a `carved_corridors` siempre reciben costo `1.0`, incluso si el hash las habría clasificado como obstáculos. De esta manera, los corredores construidos durante la generación del mapa tienen prioridad sobre la distribución estocástica y pueden utilizarse para garantizar conectividad. La clase `Map` inicializa la grilla, genera el terreno mediante `space_hashing`, selecciona puntos aleatorios de forma reproducible a partir de `seed` y utiliza una estructura tipo conjunto disjunto dentro del procedimiento de Kruskal para conectar dichos puntos con corredores ortogonales. Las aristas entre puntos se ponderan mediante distancia Manhattan, se procesan en orden creciente y se aceptan únicamente cuando conectan componentes diferentes. Este proceso genera una red de corredores con menor riesgo de componentes aislados; finalmente, las posiciones de inicio y meta se fuerzan como transitables.

Desde el punto de vista científico, el diseño separa dos procesos que cumplen funciones distintas: el *space hashing* controla la distribución espacial de obstáculos de manera determinista, mientras que Kruskal introduce una restricción topológica para asegurar rutas practicables. La semilla actúa como parámetro de control experimental: al mantenerla constante, se puede reproducir exactamente el mismo mapa y comparar tiempos de ejecución, número de nodos expandidos, longitud de ruta y costo acumulado entre diferentes estrategias de búsqueda. Al modificar la semilla o `density_rate`, se obtienen nuevas realizaciones del entorno sin cambiar la lógica del generador. Esta combinación de aleatoriedad reproducible, consulta espacial de costo constante y corrección estructural mediante corredores proporciona una base eficiente para evaluar navegación probabilística y replanificación en mapas estocásticos.

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
