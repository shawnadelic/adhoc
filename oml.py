from networkx.exception import NetworkXNoPath
from ad_hoc import RandomAdHocNetwork

class OML(object):
    def __init__(self, output_path = False, **kwargs):
        self.net = RandomAdHocNetwork(**kwargs)
        self.output_path = output_path
    def run(self):
        if self.net.connected:
            self.all_requests = list(self.net.requests)
            self.remaining_requests = list(self.net.requests)
            self.satisfied_requests = []
            self.request_solutions = []
            self.c = 1000
            self.lmbda = 10000
            net_prime = None
            net_double_prime = None
            total_energy = 0
            while self.remaining_requests:
                request = self.remaining_requests.pop()
                src, dest = request 

                # Step 1

                if net_prime is None:
                    net_prime = self.net.copy()
                net_prime.prune_edges()
                try:
                    p_prime = net_prime.shortest_path(src, dest, weight="cost")
                except NetworkXNoPath:
                    print "Cannot satisfy request: {} -> {}".format(src, dest)
                    break

                min_edge, min_re = net_prime.min_residual_energy(p_prime)
                min_src, min_dest = min_edge
        
                net_double_prime = net_prime.copy()
                net_double_prime.prune_edges(min_re)

                # Step 2

                for edge_src, edge_dest in net_double_prime.edges():
                    w_double_prime = self._w_double_prime(net_double_prime, edge_src, edge_dest, min_re)
                    net_double_prime.set_weight(edge_src, edge_dest, w_double_prime)
                try:
                    p_double_prime = net_double_prime.shortest_path(src, dest, weight="weight")
                except NetworkXNoPath:
                    print "Cannot satisfy request on net_double_prime: {} -> {}".format(src, dest)
                    break

                net_double_prime.update_along_path(p_double_prime)
                path_total_energy = net_prime.update_along_path(p_double_prime)
                total_energy += path_total_energy

                self.satisfied_requests.append((src, dest))
                self.request_solutions.append(((src, dest), p_double_prime, path_total_energy))

            if self.request_solutions:
                print "Satisfied requests:"
            for request, path, energy in self.request_solutions:
                print
                print "Request: {} -> {}".format(request[0], request[1])
                if self.output_path is True:
                    print "Path: {}".format(" -> ".join(path))
                print "Energy Consumed: {}".format(energy)
            
            #self.net.draw(requests=self.satisfied_requests)
            print
            print "**************************************************************************************"
            print "Total Requests Satisfied: {}".format(len(self.satisfied_requests))
            print "Total Energy Consumed: {}".format(total_energy)

    def _e_min(self, net, node):
        min_node = min(net[node], key=lambda dest: net.weight(node, dest))
        return net.weight(node, min_node)

    def _alpha(self, net, node, min_re):
        return float(min_re) / net.get_energy(node)

    def _rho(self, net, src, dest):
        if net.get_energy(src) - net.weight(src, dest) > self._e_min(net, src):
            return 0
        else:
            return self.c

    def _w_double_prime(self, net, src, dest, min_re):
        if net[src][dest]["type"] == "external":
            value = net.weight(src, dest) + self._rho(net, src, dest)
            alpha = self._alpha(net, src, min_re)
            weight = (self.lmbda**alpha - 1)
            return value * weight
        else:
            return net.weight(src, dest)

    def draw(self, output_file=None, requests=None):
        if self.net.connected:
            if requests is None:
                requests = self.satisfied_requests
            self.net.draw(output_file=output_file, requests=requests)

if __name__ == "__main__":
    oml = OML()
    oml.run()
