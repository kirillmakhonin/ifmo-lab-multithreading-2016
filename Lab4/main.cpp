#include <iostream>
#include <fstream>
#include <vector>
#include <list>
#include <omp.h>
#include <iomanip>

template <class T>
struct vertex_t {
	bool visited;
	std::vector<long> edges_list;
	T distance;
	bool distance_is_inf;
};

template <class T>
struct edge_t {
	long a;
	long b;
	T distance;
};

typedef std::vector<vertex_t<long>> vertex_list_t;
typedef std::vector<edge_t<long>> edge_list_t;

struct graph_t {
	long vertex_count;
	vertex_list_t vertex_list;
	long edge_count;
	edge_list_t edge_list;
};


void load_graph(std::string file, graph_t & graph){
	std::ifstream is(file);
	is >> graph.vertex_count >> graph.edge_count;

	graph.vertex_list.resize(graph.vertex_count);
	graph.edge_list.resize(graph.edge_count);

	long i, a, b, distance;

	#pragma omp parallel for schedule(static)
	for (i = 0; i < graph.vertex_count; i++){
		graph.vertex_list[i].distance = -1;
		graph.vertex_list[i].visited = false;
		graph.vertex_list[i].distance_is_inf = true;
	}

	for (i = 0; i < graph.edge_count; i++){
		is >> a >> b >> distance;
		graph.edge_list[i].a = a;
		graph.edge_list[i].b = b;
		graph.edge_list[i].distance = distance;
		graph.vertex_list[a].edges_list.push_back(i);
		graph.vertex_list[b].edges_list.push_back(i);
	}

}

void dijkstra(graph_t & graph, long src_vertex_id){
	long i, j, k;

	graph.vertex_list[src_vertex_id].visited = false;
	graph.vertex_list[src_vertex_id].distance = 0L;
	graph.vertex_list[src_vertex_id].distance_is_inf = false;

	for (i = 0; i < graph.vertex_count; i++){
		long target = -1;
		for (j = 0; j < graph.vertex_count; j++){
			if (!graph.vertex_list[j].visited
				&& (
				target < 0 ||
				(graph.vertex_list[target].distance_is_inf && !graph.vertex_list[j].distance_is_inf) ||
				(!graph.vertex_list[target].distance_is_inf && !graph.vertex_list[j].distance_is_inf && graph.vertex_list[j].distance < graph.vertex_list[target].distance)
				)){
				target = j;
			}
		}

		if (target < 0)
			break;

		std::vector<long> & edges_list = graph.vertex_list[target].edges_list;
		long len = edges_list.size();

		#pragma omp parallel for schedule(static)
		for (k = 0; k < len; k++){
			edge_t<long> & edge = graph.edge_list[edges_list[k]];
			long to = edge.a == target ? edge.b : edge.a;
			long new_distance = graph.vertex_list[target].distance + edge.distance;
				
			if (graph.vertex_list[to].distance_is_inf){
				graph.vertex_list[to].distance_is_inf = false;
				graph.vertex_list[to].distance = new_distance;
			}
			else if (graph.vertex_list[to].distance > new_distance){
				graph.vertex_list[to].distance = new_distance;
			}

		}

		graph.vertex_list[target].visited = true;
			
		
	}
}

void save_result(std::string file, graph_t & graph){
	std::ofstream os(file);
	for (long i = 0; i < graph.vertex_count; i++){
		if (i != 0)
			os << " ";

		if (graph.vertex_list[i].distance_is_inf)
			os << "INF";
		else
			os << graph.vertex_list[i].distance;		
	}
}

int main(int argc, char** argv){
	if (argc != 4){
		std::cerr << "Wrong count of arguments. Use prog.exe <in> <src_vertex_id> <out>" << std::endl;
		return 1;
	}

	graph_t graph;
	load_graph(argv[1], graph);
	long src_vertex = atol(argv[2]);

	double start, end, time;
	start = omp_get_wtime();
	// ----
	dijkstra(graph, src_vertex);
	// ----
	end = omp_get_wtime();
	time = end - start;

	save_result(argv[3], graph);

	std::cout << std::setprecision(9) << std::fixed << time << std::endl;
}