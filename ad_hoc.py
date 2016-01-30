import logging
import matplotlib.pyplot as plt
import math
import networkx as nx
import random

logging.basicConfig(level=logging.ERROR, format="%(message)s")

class RandomAdHocNetwork(nx.DiGraph):
    figure_counter = 0
    
    def __init__(self, node_count=100, width=1000, height=1000,
            transmission_range=200, min_energy=5000000000, max_energy=5000000000,
            packet_size=512, seed=None, number_of_requests = 10):
        super(RandomAdHocNetwork, self).__init__()
        random.seed(seed)
        self.node_count = node_count
        self.width = width
        self.height = height
        self.transmission_range = transmission_range
        self.min_energy = min_energy
        self.max_energy = max_energy
        self.packet_size = packet_size
        self.number_of_requests = number_of_requests
        self.x_offset = self.width / 40
        self.y_offset = self.height / 40
        self.requests = []
        self._generate_random_nodes()
        self._calculate_neighbors()
        self._generate_requests()
        
        if not self.is_connected():
            print("Error: graph is not connected")

    @staticmethod
    def _formatted_name(node):
        node_info = node.split()
        node_name, node_type = node_info
        if node_type == "in":
            return "{name} {info} ".format(name=node_name, info=node_type)
        else:
            return "{name} {info}".format(name=node_name, info=node_type)

    def residual_energy(self, src, dest):
        return self.node[src]["energy"] - self.cost(src, dest)

    def set_weight(self, src, dest, value):
        self[src][dest]["weight"] = value

    def get_weight(self, src, dest):
        return self[src][dest]["weight"]

    def get_energy(self, node):
        return self.node[node]["energy"]

    def set_energy(self, node, energy):
        self.node[node]["energy"] = energy

    def min_residual_energy(self, path):
        min_src = None
        min_dest = None
        min_value = None
        for index, value in enumerate(path[:-1]):
            src = path[index]
            dest = path[index + 1]
            if self[src][dest]["type"] == "external":
                value = self.residual_energy(src, dest)
                if not min_src or value < min_value:
                    min_src = src
                    min_dest = dest
                    min_value = value
        if min_value < 0:
            print path
            print min_src, min_dest, min_value
            print "Energy", self.node[min_src]["energy"]
            print "Cost", self.cost(min_src, min_dest)
            raise Exception
        return ((min_src, min_dest), min_value)

    def external_edges(self):
        return filter(lambda s: self[s[0]][s[1]]["type"] == "external", self.edges())

    def _generate_request(self):
        src, dest = random.sample(range(self.node_count), 2)
        return ("{} in".format(src), "{} in".format(dest))

    def _generate_requests(self):
        n = self.number_of_requests
        for i in range(n):
            self.requests.append(self._generate_request())

    def _calculate_energy_cost(self, distance): 
        # Energy consumption measured by 
        # E(T) = E(elec)*k + e(amp)*k*l^2
        # E(elec) = 50 nJ/bit
        # e(amp) = 100pJ/bit/m^2 = 0.1nJ/bit/m^2
        # 100 pJ = 0.1 nJ
        # Total cost of energy consumption in nanojoules
        k = self.packet_size
        l = distance
        transmission_energy = (50 * k) + (0.1 * k * l**2)
        return transmission_energy

    def _generate_random_nodes(self):
        xcoord = None
        ycoord = None
        self.coords = dict()
        xcoord, ycoord = self._get_random_node()
        for n in xrange(self.node_count):
            while (xcoord, ycoord) in self.coords:
                xcoord, ycoord = self._get_random_node()
            self.coords[(xcoord, ycoord)] = n
            in_node = "{} in".format(n)
            out_node = "{} out".format(n)
            initial_energy = random.uniform(self.min_energy,
                self.max_energy)
            self.add_node(in_node, id=n, type="in", x=xcoord, y=ycoord)
            self.add_node(out_node, id=n, type="out", x=xcoord,
                y=ycoord, energy=initial_energy)

    def shortest_path(self, src, dest, weight="cost"):
        return nx.shortest_path(self, src, dest, weight=weight)

    def shortest_path_length(self, src, dest, weight="cost"):
        return nx.shortest_path_length(self, src, dest, weight=weight)

    def _get_random_node(self):
        return (random.randint(0, self.width), random.randint(0,
            self.height))

    def update_along_path(self, path):
        total_energy = 0
        for index, value in enumerate(path[:-1]):
            src = path[index]
            dest = path[index + 1]
            if self[src][dest]["type"] == "external":
                total_energy += self.cost(src, dest)
                self.set_energy(src, self.get_energy(src) - self.cost(src, dest))
        return total_energy

    def prune_edges(self, threshold = None):
        for src, dest in self.external_edges():
            edge = self[src][dest]
            if threshold is None:
                edge_threshold = self.cost(src, dest)
            else:
                edge_threshold = max(threshold, self.cost(src, dest))
            if self.node[src]["energy"] < edge_threshold:
                logging.debug("Node -> {} :: Energy -> {} :: Threshold -> {} ".format(src, self.node[src]["energy"], edge_threshold))
                logging.debug("Removing edge {} -> {} : {}".format(src, dest, edge))
                self.remove_edge(src, dest)

    def cost(self, src, dest):
        try:
            edge = self[src][dest]
        except KeyError:
            raise KeyError("No edge from {} to {}".format(src, dest))
        try:
            return edge["cost"]
        except KeyError:
            raise KeyError("No cost set for edge from {} to {}".format(src, dest))


    def weight(self, src, dest):
        try:
            edge = self[src][dest]
        except KeyError:
            raise KeyError("No edge from {} to {}".format(src, dest))
        try:
            return edge["weight"]
        except KeyError:
            raise KeyError("No weight set for edge from {} to {}".format(src, dest))

    def _calculate_neighbors(self):
        for out_node in self.out_nodes():
            for in_node in self.in_nodes():
                distance = self.distance_between(out_node, in_node)
                cost = self._calculate_energy_cost(distance)
                if (distance <= self.transmission_range and
                        (in_node.split()[0] != out_node.split()[0])):
                    self.add_edge(out_node, in_node, distance=distance,
                    weight=cost, cost=cost, type="external")
        for in_node in self.in_nodes():
            out_node = in_node.split()[0] + " out"
            self.add_edge(in_node, out_node, distance=0, weight=0,
            cost=0, type="internal")

    def distance_between(self, src, dest):
        x1 = self.node[src]["x"]
        y1 = self.node[src]["y"]
        x2 = self.node[dest]["x"]
        y2 = self.node[dest]["y"]
        distance = math.sqrt(((x1 - x2) * (x1 - x2)) + ((y1 - y2) * (y1 - y2)))
        return distance

    def in_nodes(self):
        return sorted(filter(lambda n: " in" in n, self.nodes()))

    def out_nodes(self):
        return sorted(filter(lambda n: " out" in n, self.nodes()))

    def get_by_coords(self, x, y, node_type=None):
        node_id = self.coords[(x, y)]
        if node_type:
            return self.node["{} {}".format(str(node_id), node_type)]
        else:
            nodes.append(self.node["{} in".format(str(node_id))])
            nodes.append(self.node["{} out".format(str(node_id))])
        return nodes

    def print_info(self, nodes=True, edges=True):
        if nodes:
            for node in sorted(self.nodes()):
                print("Node {node}:  {info}".
                    format(node=self._formatted_name(node), info=self.node[node]))
        if edges:
            for edge in sorted(self.edges()):
                src, dest = edge
                print("Edge {src} -> {dest}: {info}"
                    .format(src=src, dest=dest, info=self[src][dest]))

    def is_connected(self):
        """
        Build temporary graph structure to check for connectivity
        since NetworkX can only check for connectivity on undirected graphs
        """
        temp = nx.Graph()
        for e in self.edges():
            src = e[0].split()[0]
            dest = e[1].split()[0]
            temp.add_edge(src, dest)
        return nx.is_connected(temp)

    def draw(self, output_file=None, requests=None):
        plt.figure(random.randint(0,1000000))
        colors = {
            "out": "c",
            "in": "m",
        }
        for n in self.nodes():
            node = self.node[n]
            plt.scatter(node["x"], node["y"])
            plt.scatter(node["x"] + self.x_offset, node["y"] + self.y_offset)
        for e in self.edges():
            src, dest = e
            edge_type = self.node[src]["type"]
            color = colors[edge_type]
            plt.plot([self.node[src]["x"], self.node[dest]["x"] +
                self.x_offset], [self.node[src]["y"], self.node[dest]["y"]
                + self.y_offset], color=color)
        if requests:
            for r in requests:
                src, dest = r
                color = "g"
                plt.plot([self.node[src]["x"], self.node[dest]["x"] +
                    self.x_offset], [self.node[src]["y"], self.node[dest]["y"]
                    + self.y_offset], color=color)

        if output_file:
            plt.savefig(output_file)
        else:
            plt.show()
