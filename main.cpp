#include "single_include/bmssp.hpp"
#include <iostream>
#include <vector>

using T = long long;

int main() {
    // 1. Definir el grafo
    int n = 5;
    std::vector<std::tuple<int, int, T>> edges = {
        {0, 1, 10}, {0, 2, 3}, {1, 3, 2}, {2, 1, 4},
        {2, 3, 8}, {2, 4, 2}, {3, 4, 5}
    };
    int source_node = 0;

    // 2. Inicializar el solver
    spp::bmssp<T> solver(n);

    // 3. Añadir todas las aristas
    for (const auto& [u, v, weight] : edges) {
        solver.addEdge(u, v, weight);
    }

    // 4. Preparar el grafo (obligatorio llamar una vez)
    solver.prepare_graph(false);
    // usas true si el grafo no tiene grado de salida constante

    // 5. Ejecutar el algoritmo
    auto [distances, predecessors] = solver.execute(source_node);

    // 6. Imprimir resultados
    std::cout << "Distancias desde la fuente " << source_node << ":" << std::endl;
    for (int i = 0; i < n; ++i) {
        std::cout << "  Hasta " << i << ": ";
        if (distances[i] == solver.oo) {
            std::cout << "inalcanzable" << std::endl;
        } else {
            std::cout << distances[i] << std::endl;
        }
    }
    return 0;
}
