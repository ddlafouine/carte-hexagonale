import random
import time
import heapq
import itertools
from hexa import HexGridViewer, Circle
import matplotlib.pyplot as plt


# ============================================================================
# CLASSE PRINCIPALE - GRAPHE HEXAGONAL
# ============================================================================

class HexGraph:
    """
    Représente un graphe sous forme de grille hexagonale.
    Chaque case hexagonale est un sommet, avec des arêtes vers ses 6 voisins.
    """

    def __init__(self, width: int, height: int):
        """
        Initialise une grille hexagonale vide.
        
        Args:
            width: Largeur de la grille
            height: Hauteur de la grille
        """
        self.width = width
        self.height = height
        self.n = width * height

        # Matrice d'adjacence
        self.matrice: [[int]] = [[0] * self.n for _ in range(self.n)]

        # Propriétés des cases
        self.terrain: [[int, int], str] = {}
        self.altitude: [[int, int], float] = {}
        self.riviere: set = set()
        self.villes: set = set()
        self.routes: set = set()

        # Conversion coordonnées <-> indices
        self.coord_to_node: [[int, int], int] = {}
        self.node_to_coord: [int, [int, int]] = {}

        idx = 0
        for y in range(height):
            for x in range(width):
                self.coord_to_node[(x, y)] = idx
                self.node_to_coord[idx] = (x, y)
                idx += 1

        self._build_hex_edges()

    def _build_hex_edges(self):
        """Construit les arêtes du graphe hexagonal."""
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self._get_hex_neighbours(x, y)
                node1 = self.coord_to_node[(x, y)]
                for nx, ny in neighbors:
                    node2 = self.coord_to_node[(nx, ny)]
                    self.matrice[node1][node2] = 1
                    self.matrice[node2][node1] = 1

    def _get_hex_neighbours(self, x: int, y: int) -> [[int, int]]:
        """Retourne les voisins d'une case hexagonale."""
        if y % 2 == 0:
            offs = [(1, 0), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1)]
        else:
            offs = [(1, 0), (1, 1), (0, 1), (-1, 0), (0, -1), (1, -1)]

        neighbors = []
        for dx, dy in offs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((nx, ny))
        return neighbors

    # Getters et setters
    def _terrain(self, x: int, y: int, terrain_type: str) -> None:
        self.terrain[(x, y)] = terrain_type

    def get_terrain(self, x: int, y: int) -> str:
        return self.terrain.get((x, y), "darkgreen")

    def _altitude(self, x: int, y: int, alt: float) -> None:
        self.altitude[(x, y)] = alt

    def get_altitude(self, x: int, y: int) -> float:
        return self.altitude.get((x, y), 0.0)

    def is_river(self, x: int, y: int) -> bool:
        return (x, y) in self.riviere

    def add_river_cell(self, x: int, y: int) -> None:
        self.riviere.add((x, y))

    def add_ville(self, x: int, y: int) -> None:
        self.villes.add((x, y))

    def is_ville(self, x: int, y: int) -> bool:
        return (x, y) in self.villes

    def add_route(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Ajoute une route bidirectionnelle entre deux cases adjacentes."""
        self.routes.add(((x1, y1), (x2, y2)))
        self.routes.add(((x2, y2), (x1, y1)))

    def neighbours(self, x: int, y: int) -> [[int, int]]:
        return self._get_hex_neighbours(x, y)


# ============================================================================
# Q3 - GÉNÉRATION DE TERRAIN (DIAMOND-SQUARE)
# ============================================================================

def diamond_square(size: int, roughness: float = 0.5, seed: int = None) -> [[float]]:
    """
    Génère une heightmap avec l'algorithme Diamond-Square.
    
    Args:
        size: Taille de la grille (doit être 2^n + 1, ex: 33, 65, 129)
        roughness: Contrôle la rugosité (0.0 à 1.0)
        seed: Graine aléatoire pour reproductibilité
    """
    if seed is not None:
        random.seed(seed)

    grid = [[0.0] * size for _ in range(size)]

    # Initialiser les 4 coins
    grid[0][0] = random.uniform(0, 1)
    grid[0][size-1] = random.uniform(0, 1)
    grid[size-1][0] = random.uniform(0, 1)
    grid[size-1][size-1] = random.uniform(0, 1)

    step_size = size - 1
    scale = 1.0

    while step_size > 1:
        half_step = step_size // 2

        # Étape Diamond
        for y in range(0, size - 1, step_size):
            for x in range(0, size - 1, step_size):
                avg = (grid[y][x] + grid[y][x + step_size] +
                       grid[y + step_size][x] + grid[y + step_size][x + step_size]) / 4.0
                offset = random.uniform(-scale, scale)
                grid[y + half_step][x + half_step] = avg + offset

        # Étape Square
        for y in range(0, size, half_step):
            for x in range((y + half_step) % step_size, size, step_size):
                sum_val = 0.0
                count = 0
                neighbors = [
                    (x, y - half_step), (x, y + half_step),
                    (x - half_step, y), (x + half_step, y)
                ]

                for nx, ny in neighbors:
                    if 0 <= nx < size and 0 <= ny < size:
                        sum_val += grid[ny][nx]
                        count += 1

                avg = sum_val / count if count > 0 else 0.0
                offset = random.uniform(-scale, scale)
                grid[y][x] = avg + offset

        step_size //= 2
        scale *= roughness

    # Normaliser entre 0 et 1
    min_val = min(min(row) for row in grid)
    max_val = max(max(row) for row in grid)
    if max_val - min_val > 0:
        for y in range(size):
            for x in range(size):
                grid[y][x] = (grid[y][x] - min_val) / (max_val - min_val)

    return grid


def sample_heightmap(heightmap, hex_x, hex_y, hex_width, hex_height):
    """Échantillonne la heightmap à une position hexagonale spécifique (interpolation bilinéaire)."""
    ds_size = len(heightmap)
    map_x = (hex_x / hex_width) * (ds_size - 1)
    map_y = (hex_y / hex_height) * (ds_size - 1)

    x0 = int(map_x)
    y0 = int(map_y)
    x1 = min(x0 + 1, ds_size - 1)
    y1 = min(y0 + 1, ds_size - 1)

    fx = map_x - x0
    fy = map_y - y0

    val00 = heightmap[y0][x0]
    val10 = heightmap[y0][x1]
    val01 = heightmap[y1][x0]
    val11 = heightmap[y1][x1]

    val0 = val00 * (1 - fx) + val10 * fx
    val1 = val01 * (1 - fx) + val11 * fx

    return val0 * (1 - fy) + val1 * fy


def altitude_to_terrain(altitude: float) -> str:
    """Convertit une altitude en type de terrain."""
    if altitude < 0.3:
        return "blue"      # Eau
    elif altitude < 0.45:
        return "yellow"    # Plage
    elif altitude < 0.6:
        return "darkgreen" # Plaine
    elif altitude < 0.75:
        return "green"     # Forêt
    else:
        return "grey"      # Montagne


def generate_map_with_diamond_square(hex_graph: HexGraph, roughness: float = 0.5, seed: int = None) -> None:
    """Génère une carte complète avec altitudes et terrains."""
    ds_size = 33
    heightmap = diamond_square(ds_size, roughness, seed)

    for y in range(hex_graph.height):
        for x in range(hex_graph.width):
            altitude = sample_heightmap(heightmap, x, y, hex_graph.width - 1, hex_graph.height - 1)
            terrain = altitude_to_terrain(altitude)
            hex_graph._terrain(x, y, terrain)
            hex_graph._altitude(x, y, altitude)


# ============================================================================
# Q5 - GÉNÉRATION DE RIVIÈRES
# ============================================================================

def find_highest_point(hex_graph: HexGraph) -> (int, int):
    """Trouve le sommet le plus haut de la carte."""
    max_alt = -1
    max_point = (0, 0)
    for y in range(hex_graph.height):
        for x in range(hex_graph.width):
            alt = hex_graph.get_altitude(x, y)
            if alt > max_alt:
                max_alt = alt
                max_point = (x, y)
    return max_point


def generate_river(hex_graph: HexGraph) -> None:
    """
    Génère une rivière en descendant du point le plus haut vers le plus bas.
    Utilise un algorithme glouton : à chaque étape, choisit le voisin avec l'altitude la plus basse.
    """
    current = find_highest_point(hex_graph)
    visited = set()

    while True:
        x, y = current
        hex_graph.add_river_cell(x, y)
        visited.add(current)
        current_alt = hex_graph.get_altitude(x, y)

        # Trouver le voisin non visité avec la plus basse altitude
        neighbors = hex_graph.neighbours(x, y)
        lowest_neighbor = None
        lowest_alt = current_alt

        for nx, ny in neighbors:
            if (nx, ny) not in visited:
                neighbor_alt = hex_graph.get_altitude(nx, ny)
                if neighbor_alt < lowest_alt:
                    lowest_alt = neighbor_alt
                    lowest_neighbor = (nx, ny)

        if lowest_neighbor is None:
            break

        current = lowest_neighbor


# ============================================================================
# Q7 - PLACEMENT DE VILLES ET ROUTES (SANS CONTRAINTES)
# ============================================================================

def calculate_hex_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Calcule la distance hexagonale entre deux cases."""
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    return dx + max(0, (dy - dx) // 2)


def place_villes(hex_graph: HexGraph, num_villes: int, min_distance: int = 2, quadrants: int = 4) -> None:
    """
    Place des villes réparties équitablement sur la carte.
    
    Args:
        num_villes: Nombre de villes à placer
        min_distance: Distance minimale entre deux villes
        quadrants: Nombre de zones (4 ou 9 recommandé)
    """
    divisions = int(quadrants ** 0.5)
    villes_par_quadrant = num_villes // quadrants
    villes_restantes = num_villes % quadrants

    quad_width = hex_graph.width // divisions
    quad_height = hex_graph.height // divisions

    for quad_row in range(divisions):
        for quad_col in range(divisions):
            x_min = quad_col * quad_width
            x_max = (quad_col + 1) * quad_width if quad_col < divisions - 1 else hex_graph.width
            y_min = quad_row * quad_height
            y_max = (quad_row + 1) * quad_height if quad_row < divisions - 1 else hex_graph.height

            villes_ce_quadrant = villes_par_quadrant + (1 if villes_restantes > 0 else 0)
            if villes_restantes > 0:
                villes_restantes -= 1

            villes_placed = 0
            attempts = 0
            max_attempts = villes_ce_quadrant * 100

            while villes_placed < villes_ce_quadrant and attempts < max_attempts:
                x = random.randint(x_min, x_max - 1)
                y = random.randint(y_min, y_max - 1)

                # Vérifier les contraintes
                if not hex_graph.is_river(x, y) and not hex_graph.is_ville(x, y):
                    altitude = hex_graph.get_altitude(x, y)
                    if altitude >= 0.3:  # Pas dans l'eau
                        trop_proche = any(
                            calculate_hex_distance(x, y, vx, vy) < min_distance
                            for vx, vy in hex_graph.villes
                        )

                        if not trop_proche:
                            hex_graph.add_ville(x, y)
                            villes_placed += 1

                attempts += 1


def dijkstra(hex_graph: HexGraph, start: (int, int)) -> dict:
    """
    Algorithme de Dijkstra pour trouver les plus courts chemins depuis start.
    SANS contraintes de terrain (coût uniforme = 1 par case).
    
    Complexité: O((V + E) log V) où V = nb cases, E = nb arêtes
    
    Returns:
        dict {(x,y): (distance, parent)}
    """
    distances = {start: (0, None)}
    heap = [(0, start)]
    visited = set()

    while heap:
        dist, current = heapq.heappop(heap)

        if current in visited:
            continue

        visited.add(current)

        for neighbor in hex_graph.neighbours(*current):
            if neighbor not in visited:
                new_dist = dist + 1
                if neighbor not in distances or new_dist < distances[neighbor][0]:
                    distances[neighbor] = (new_dist, current)
                    heapq.heappush(heap, (new_dist, neighbor))

    return distances


def prim_mst(villes: list, distances_dict: dict) -> list:
    """
    Algorithme de Prim pour construire un arbre couvrant minimum (MST).
    
    Complexité: O(N² log N) où N = nombre de villes
    
    Returns:
        Liste de tuples (ville1, ville2, distance)
    """
    if not villes:
        return []

    mst_edges = []
    visited = {villes[0]}
    heap = []

    # Ajouter toutes les arêtes depuis la première ville
    for ville2 in villes[1:]:
        if ville2 in distances_dict[villes[0]]:
            dist = distances_dict[villes[0]][ville2]
            heapq.heappush(heap, (dist, villes[0], ville2))

    # Construire le MST
    while heap and len(visited) < len(villes):
        dist, ville1, ville2 = heapq.heappop(heap)

        if ville2 in visited:
            continue

        visited.add(ville2)
        mst_edges.append((ville1, ville2, dist))

        # Ajouter les nouvelles arêtes
        for ville3 in villes:
            if ville3 not in visited and ville3 in distances_dict[ville2]:
                dist3 = distances_dict[ville2][ville3]
                heapq.heappush(heap, (dist3, ville2, ville3))

    return mst_edges


def reconstruct_path(distances: dict, start: (int, int), end: (int, int)) -> list:
    """Reconstruit le chemin depuis start jusqu'à end en suivant les parents."""
    if end not in distances:
        return []

    path = []
    current = end
    while current is not None:
        path.append(current)
        _, parent = distances[current]
        current = parent

    path.reverse()
    return path


def generate_routes(hex_graph: HexGraph, use_weighted: bool = False) -> float:
    """
    Génère les routes entre toutes les villes en utilisant un MST (Q.7 et Q.9).
    
    Args:
        use_weighted: Si True, utilise dijkstra_weighted (Q.8)
    
    Returns:
        Temps de calcul en secondes
    
    Complexité: O(N * V log V + N² log N)
    """
    start_time = time.time()

    villes = list(hex_graph.villes)
    if len(villes) < 2:
        return time.time() - start_time

    dijkstra_func = dijkstra_weighted if use_weighted else dijkstra

    # Calculer toutes les distances entre villes
    distances_dict = {}
    for ville in villes:
        distances = dijkstra_func(hex_graph, ville)
        distances_dict[ville] = {}
        for autre_ville in villes:
            if autre_ville != ville and autre_ville in distances:
                distances_dict[ville][autre_ville] = distances[autre_ville][0]

    # Construire le MST
    mst_edges = prim_mst(villes, distances_dict)

    # Tracer les routes
    for ville1, ville2, _ in mst_edges:
        distances = dijkstra_func(hex_graph, ville1)
        path = reconstruct_path(distances, ville1, ville2)
        for i in range(len(path) - 1):
            hex_graph.add_route(*path[i], *path[i+1])

    return time.time() - start_time


# ============================================================================
# Q8 - ROUTES AVEC CONTRAINTES (TERRAIN + ALTITUDE)
# ============================================================================

def calculate_cost(hex_graph: HexGraph, from_cell: (int, int), to_cell: (int, int)) -> float:
    """
    Calcule le coût pour aller de from_cell à to_cell.
    Prend en compte le terrain et l'altitude.
    
    Returns:
        float: coût (inf si impossible, ex: eau)
    """
    x2, y2 = to_cell
    x1, y1 = from_cell

    terrain = hex_graph.get_terrain(x2, y2)
    alt_from = hex_graph.get_altitude(x1, y1)
    alt_to = hex_graph.get_altitude(x2, y2)

    # Eau = impossible
    if terrain in ["blue", "cyan"] or hex_graph.is_river(x2, y2):
        return float('inf')

    # Coût selon le terrain
    terrain_costs = {
        "yellow": 1.5,      # Plage
        "darkgreen": 1.0,   # Plaine
        "green": 2.0,       # Forêt
        "grey": 3.0,        # Montagne
        "orange": 0.5       # Route
    }
    base_cost = terrain_costs.get(terrain, 1.0)

    # Pénalité d'altitude
    altitude_diff = abs(alt_to - alt_from)
    altitude_penalty = altitude_diff * 2.0

    return base_cost + altitude_penalty


def dijkstra_weighted(hex_graph: HexGraph, start: (int, int)) -> dict:
    """
    Dijkstra modifié pour prendre en compte terrain et altitude (Q.8).
    
    Returns:
        dict {(x,y): (distance, parent)}
    """
    distances = {start: (0, None)}
    heap = [(0, start)]
    visited = set()

    while heap:
        dist, current = heapq.heappop(heap)

        if current in visited:
            continue

        visited.add(current)

        for neighbor in hex_graph.neighbours(*current):
            cost = calculate_cost(hex_graph, current, neighbor)

            if cost == float('inf'):  # Impossible
                continue

            if neighbor not in visited:
                new_dist = dist + cost
                if neighbor not in distances or new_dist < distances[neighbor][0]:
                    distances[neighbor] = (new_dist, current)
                    heapq.heappush(heap, (new_dist, neighbor))

    return distances


# ============================================================================
# Q10 - TSP (VOYAGEUR DE COMMERCE) - VERSION EXACTE UNIQUEMENT
# ============================================================================

def tsp_exact(hex_graph, use_weighted=True):
    """
    Résout le TSP de manière exacte en testant toutes les permutations.
    
    Complexité: O(N!) - UTILISABLE SEULEMENT POUR N <= 10 villes
    
    Args:
        hex_graph: Graphe avec les villes
        use_weighted: Si True, utilise coûts pondérés (terrain + altitude)
    
    Returns:
        (meilleur_chemin, coût_total, temps_calcul)
    """
    start_time = time.time()

    villes = list(hex_graph.villes)
    if len(villes) < 2:
        return (villes, 0, time.time() - start_time)

    dijkstra_func = dijkstra_weighted if use_weighted else dijkstra

    # Précalculer toutes les distances
    distances_dict = {}
    for ville in villes:
        distances = dijkstra_func(hex_graph, ville)
        distances_dict[ville] = {}
        for autre_ville in villes:
            if autre_ville != ville and autre_ville in distances:
                distances_dict[ville][autre_ville] = distances[autre_ville][0]
            else:
                distances_dict[ville][autre_ville] = float('inf')

    # Fixer la ville de départ
    ville_depart = villes[0]
    autres_villes = villes[1:]

    meilleur_cout = float('inf')
    meilleur_chemin = None

    # Tester toutes les permutations
    for perm in itertools.permutations(autres_villes):
        chemin = [ville_depart] + list(perm)
        cout_total = 0

        # Calculer le coût du circuit (avec retour)
        for i in range(len(chemin)):
            ville_actuelle = chemin[i]
            ville_suivante = chemin[(i + 1) % len(chemin)]
            cout_total += distances_dict[ville_actuelle][ville_suivante]

        if cout_total < meilleur_cout:
            meilleur_cout = cout_total
            meilleur_chemin = chemin

    return (meilleur_chemin, meilleur_cout, time.time() - start_time)


def trace_tsp_circuit(hex_graph, chemin_tsp, use_weighted=True):
    """
    Trace le circuit du voyageur de commerce sur la carte.
    Stocke le résultat dans hex_graph.circuit_marchand.
    """
    if len(chemin_tsp) < 2:
        return

    dijkstra_func = dijkstra_weighted if use_weighted else dijkstra
    hex_graph.circuit_marchand = set()

    # Tracer chaque segment
    for i in range(len(chemin_tsp)):
        ville_depart = chemin_tsp[i]
        ville_arrivee = chemin_tsp[(i + 1) % len(chemin_tsp)]

        distances = dijkstra_func(hex_graph, ville_depart)
        path = reconstruct_path(distances, ville_depart, ville_arrivee)

        for j in range(len(path) - 1):
            hex_graph.circuit_marchand.add((path[j], path[j+1]))
            hex_graph.circuit_marchand.add((path[j+1], path[j]))


# ============================================================================
# AFFICHAGE
# ============================================================================

def display_hex_graph(hex_graph: HexGraph, show_tsp: bool = False, debug_coords: bool = False) -> None:
    """
    Affiche le graphe hexagonal.
    
    Args:
        show_tsp: Si True, affiche le circuit TSP en magenta
        debug_coords: Si True, affiche les coordonnées
    """
    viewer = HexGridViewer(hex_graph.width, hex_graph.height)

    # Terrains et altitudes
    for y in range(hex_graph.height):
        for x in range(hex_graph.width):
            altitude = hex_graph.get_altitude(x, y)
            is_river = hex_graph.is_river(x, y)

            if is_river:
                terrain = "cyan"
            elif altitude < 0.3:
                terrain = "blue"
            elif altitude < 0.45:
                terrain = "yellow"
            elif altitude < 0.6:
                terrain = "darkgreen"
            elif altitude < 0.75:
                terrain = "green"
            else:
                terrain = "grey"

            viewer.add_color(x, y, terrain)
            alpha = 0.6 + altitude * 0.4
            viewer.add_alpha(x, y, alpha)

    # Routes (orange, fines)
    routes_drawn = set()
    for (x1, y1), (x2, y2) in hex_graph.routes:
        if ((x1, y1), (x2, y2)) not in routes_drawn and ((x2, y2), (x1, y1)) not in routes_drawn:
            viewer.add_link((x1, y1), (x2, y2), color="orange", thick=2)
            routes_drawn.add(((x1, y1), (x2, y2)))

    # Circuit TSP (magenta, épais)
    if show_tsp and hasattr(hex_graph, 'circuit_marchand'):
        circuit_drawn = set()
        for (x1, y1), (x2, y2) in hex_graph.circuit_marchand:
            if ((x1, y1), (x2, y2)) not in circuit_drawn and ((x2, y2), (x1, y1)) not in circuit_drawn:
                viewer.add_link((x1, y1), (x2, y2), color="magenta", thick=5)
                circuit_drawn.add(((x1, y1), (x2, y2)))

    # Villes
    for x, y in hex_graph.villes:
        viewer.add_symbol(x, y, Circle("red", edgecolor="darkred"))

    alias = {
        "blue": "Eau",
        "cyan": "Rivière",
        "yellow": "Plage",
        "darkgreen": "Plaine",
        "green": "Forêt",
        "grey": "Montagne"
    }

    viewer.show(alias=alias, debug_coords=debug_coords)


# ============================================================================
# BENCHMARKS
# ============================================================================

def benchmark_routes(grid_sizes, num_villes_list, num_tests=3):
    """Benchmark l'algorithme de génération de routes (Q.7)."""
    results = {}

    for grid_size in grid_sizes:
        results[grid_size] = {}
        for num_villes in num_villes_list:
            if num_villes > grid_size * grid_size * 0.7:
                continue

            times = []
            for _ in range(num_tests):
                hex_graph = HexGraph(grid_size, grid_size)
                generate_map_with_diamond_square(hex_graph, roughness=0.6)
                place_villes(hex_graph, num_villes)
                calc_time = generate_routes(hex_graph, use_weighted=False)
                times.append(calc_time)

            avg_time = sum(times) / len(times)
            results[grid_size][num_villes] = avg_time
            print(f"Grille {grid_size}×{grid_size}, {num_villes} villes: {avg_time:.4f}s")

    return results


def plot_benchmark_results(results):
    """Crée des graphiques pour visualiser les résultats du benchmark."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Graphique 1: Temps vs Nombre de villes
    for grid_size in sorted(results.keys()):
        villes = sorted(results[grid_size].keys())
        times = [results[grid_size][v] for v in villes]
        ax1.plot(villes, times, marker='o', label=f'Grille {grid_size}×{grid_size}')

    ax1.set_xlabel('Nombre de villes', fontsize=12)
    ax1.set_ylabel('Temps de calcul (secondes)', fontsize=12)
    ax1.set_title('Temps en fonction du nombre de villes', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Graphique 2: Temps vs Taille de grille
    for num_villes in sorted(set(v for gs in results.values() for v in gs.keys())):
        grid_sizes = []
        times = []
        for grid_size in sorted(results.keys()):
            if num_villes in results[grid_size]:
                grid_sizes.append(grid_size)
                times.append(results[grid_size][num_villes])

        if grid_sizes:
            ax2.plot(grid_sizes, times, marker='s', label=f'{num_villes} villes')

    ax2.set_xlabel('Taille de la grille (N×N)', fontsize=12)
    ax2.set_ylabel('Temps de calcul (secondes)', fontsize=12)
    ax2.set_title('Temps en fonction de la taille de grille', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('benchmark_routes.png', dpi=150, bbox_inches='tight')
    print("\n✓ Graphique sauvegardé: benchmark_routes.png")
    plt.show()


# ============================================================================
# MAIN - MENU INTERACTIF
# ============================================================================

def main():
    """Menu principal pour lancer chaque question individuellement."""
    
    while True:
        print("\n" + "="*60)
        print("PROJET THÉORIE DES GRAPHES - GRILLE HEXAGONALE")
        print("="*60)
        print("\nQuestions disponibles:")
        print("  [3] Q3 - Génération de carte avec terrains aléatoires")
        print("  [5] Q5 - Génération de rivières")
        print("  [7] Q7 - Villes et routes (sans contraintes)")
        print("  [8] Q8 - Routes avec contraintes (terrain + altitude)")
        print("  [9] Q9 - Réseau de routes minimal (MST)")
        print("  [10] Q10 - Voyageur de commerce (TSP exact)")
        print("\nBenchmarks:")
        print("  [B7] Benchmark Q7 (temps de calcul)")
        print("\nAutres:")
        print("  [C78] Comparaison Q7 vs Q8")
        print("  [0] Quitter")
        print("="*60)
        
        choice = input("\nVotre choix: ").strip().upper()
        
        if choice == '0':
            print("Au revoir!")
            break
            
        elif choice == '3':
            print("\n=== Q3 - GÉNÉRATION DE CARTE ===")
            width = int(input("Largeur (défaut 30): ") or "30")
            height = int(input("Hauteur (défaut 30): ") or "30")
            
            hex_graph = HexGraph(width, height)
            generate_map_with_diamond_square(hex_graph, roughness=0.6)
            
            print(f"✓ Carte {width}×{height} générée")
            display_hex_graph(hex_graph)
            
        elif choice == '5':
            print("\n=== Q5 - GÉNÉRATION DE RIVIÈRE ===")
            width = int(input("Largeur (défaut 30): ") or "30")
            height = int(input("Hauteur (défaut 30): ") or "30")
            
            hex_graph = HexGraph(width, height)
            generate_map_with_diamond_square(hex_graph, roughness=0.6)
            generate_river(hex_graph)
            
            print(f"✓ Rivière générée depuis le point le plus haut")
            display_hex_graph(hex_graph)
            
        elif choice == '7':
            print("\n=== Q7 - VILLES ET ROUTES (SANS CONTRAINTES) ===")
            width = int(input("Largeur (défaut 30): ") or "30")
            height = int(input("Hauteur (défaut 30): ") or "30")
            num_villes = int(input("Nombre de villes (défaut 6): ") or "6")
            
            hex_graph = HexGraph(width, height)
            generate_map_with_diamond_square(hex_graph, roughness=0.6)
            generate_river(hex_graph)
            place_villes(hex_graph, num_villes)
            
            print(f"✓ {len(hex_graph.villes)} villes placées")
            print("Génération des routes...")
            
            calc_time = generate_routes(hex_graph, use_weighted=False)
            
            print(f"✓ Temps de calcul: {calc_time:.4f}s")
            print(f"✓ {len(hex_graph.routes) // 2} segments de route")
            display_hex_graph(hex_graph)
            
        elif choice == '8':
            print("\n=== Q8 - ROUTES AVEC CONTRAINTES ===")
            width = int(input("Largeur (défaut 30): ") or "30")
            height = int(input("Hauteur (défaut 30): ") or "30")
            num_villes = int(input("Nombre de villes (défaut 6): ") or "6")
            
            hex_graph = HexGraph(width, height)
            generate_map_with_diamond_square(hex_graph, roughness=0.6)
            generate_river(hex_graph)
            place_villes(hex_graph, num_villes)
            
            print(f"✓ {len(hex_graph.villes)} villes placées")
            print("Génération des routes (avec contraintes)...")
            
            calc_time = generate_routes(hex_graph, use_weighted=True)
            
            print(f"✓ Temps de calcul: {calc_time:.4f}s")
            print(f"✓ {len(hex_graph.routes) // 2} segments de route")
            print("✓ Les routes évitent l'eau et privilégient les terrains faciles")
            display_hex_graph(hex_graph)
            
        elif choice == '9':
            print("\n=== Q9 - RÉSEAU MINIMAL (MST) ===")
            print("Note: Q9 utilise le même algorithme que Q7/Q8")
            print("Le MST est automatiquement calculé par generate_routes()")
            width = int(input("Largeur (défaut 30): ") or "30")
            height = int(input("Hauteur (défaut 30): ") or "30")
            num_villes = int(input("Nombre de villes (défaut 8): ") or "8")
            weighted = input("Avec contraintes? (o/N): ").lower() == 'o'
            
            hex_graph = HexGraph(width, height)
            generate_map_with_diamond_square(hex_graph, roughness=0.6)
            generate_river(hex_graph)
            place_villes(hex_graph, num_villes)
            
            calc_time = generate_routes(hex_graph, use_weighted=weighted)
            
            print(f"\n✓ Réseau minimal construit avec Prim")
            print(f"✓ Temps: {calc_time:.4f}s")
            print(f"✓ {len(hex_graph.routes) // 2} segments")
            display_hex_graph(hex_graph)
            
        elif choice == '10':
            print("\n=== Q10 - VOYAGEUR DE COMMERCE (TSP) ===")
            print("⚠️  ATTENTION: Algorithme exact O(N!)")
            print("    Recommandé pour N ≤ 10 villes maximum")
            
            width = int(input("Largeur (défaut 25): ") or "25")
            height = int(input("Hauteur (défaut 25): ") or "25")
            num_villes = int(input("Nombre de villes (défaut 6): ") or "6")
            
            if num_villes > 10:
                confirm = input(f"⚠️  {num_villes} villes = très long! Continuer? (o/N): ")
                if confirm.lower() != 'o':
                    continue
            
            seed_input = input("Seed aléatoire (Entrée = aléatoire): ").strip()
            seed = int(seed_input) if seed_input else None
            
            weighted = input("Avec contraintes terrain? (o/N): ").lower() == 'o'
            
            hex_graph = HexGraph(width, height)
            generate_map_with_diamond_square(hex_graph, roughness=0.6, seed=seed)
            generate_river(hex_graph)
            place_villes(hex_graph, num_villes)
            
            if seed is not None:
                print(f"✓ Carte générée avec seed: {seed}")
            
            # Réseau de base
            generate_routes(hex_graph, use_weighted=weighted)
            
            # TSP
            print("\nCalcul du circuit optimal...")
            chemin, cout, temps = tsp_exact(hex_graph, use_weighted=weighted)
            
            print(f"\n✓ Circuit optimal trouvé!")
            print(f"✓ Temps de calcul: {temps:.4f}s")
            print(f"✓ Coût total: {cout:.2f}")
            print(f"\nOrdre de visite:")
            for i, ville in enumerate(chemin, 1):
                print(f"  {i}. {ville}")
            print(f"  → Retour à {chemin[0]}")
            
            # Tracer et afficher
            trace_tsp_circuit(hex_graph, chemin, use_weighted=weighted)
            display_hex_graph(hex_graph, show_tsp=True)
            
        elif choice == 'B7':
            print("\n=== BENCHMARK Q7 ===")
            print("Mesure le temps de calcul en fonction de la taille et du nombre de villes")
            
            grid_sizes = [10, 15, 20, 25, 30]
            num_villes_list = [3, 5, 8, 10, 15, 20]
            num_tests = 3
            
            print(f"\nGrilles: {grid_sizes}")
            print(f"Villes: {num_villes_list}")
            print(f"Tests par config: {num_tests}\n")
            
            results = benchmark_routes(grid_sizes, num_villes_list, num_tests)
            plot_benchmark_results(results)
            
        elif choice == 'C78':
            print("\n=== COMPARAISON Q7 vs Q8 ===")
            print("Génère 2 cartes identiques avec routes sans/avec contraintes")
            
            width, height = 30, 30
            num_villes = 6
            seed = 42
            
            # Q7
            print("\n1. Génération Q7 (sans contraintes)...")
            hex_graph_q7 = HexGraph(width, height)
            generate_map_with_diamond_square(hex_graph_q7, roughness=0.6, seed=seed)
            generate_river(hex_graph_q7)
            place_villes(hex_graph_q7, num_villes)
            time_q7 = generate_routes(hex_graph_q7, use_weighted=False)
            
            # Q8
            print("2. Génération Q8 (avec contraintes)...")
            hex_graph_q8 = HexGraph(width, height)
            generate_map_with_diamond_square(hex_graph_q8, roughness=0.6, seed=seed)
            generate_river(hex_graph_q8)
            hex_graph_q8.villes = hex_graph_q7.villes.copy()
            time_q8 = generate_routes(hex_graph_q8, use_weighted=True)
            
            print(f"\n=== RÉSULTATS ===")
            print(f"Q7: {time_q7:.4f}s, {len(hex_graph_q7.routes)//2} segments")
            print(f"Q8: {time_q8:.4f}s, {len(hex_graph_q8.routes)//2} segments")
            
            print("\nAffichage Q7...")
            display_hex_graph(hex_graph_q7)
            
            print("Affichage Q8...")
            display_hex_graph(hex_graph_q8)
            
        else:
            print("❌ Choix invalide")
        
        input("\nAppuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    main()