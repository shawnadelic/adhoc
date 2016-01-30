from networkx.exception import NetworkXNoPath
from ad_hoc import RandomAdHocNetwork

class GDP(object):
    def __init__(self, output_path = False, **kwargs):
        self.net = RandomAdHocNetwork(**kwargs)
        self.output_path = output_path
    def run(self):
        self.all_requests = list(self.net.requests)
        self.remaining_requests = list(self.net.requests)
        self.satisfied_requests = []
        self.request_solutions = []
        total_energy = 0
        net = self.net
        self.beta = self.calculate_beta(net)
        while self.remaining_requests:
            #request = self.remaining_requests.pop()
            #src, dest = request

            try:
                min_request, min_path, min_path_value = self.minimum_weighted_path(net, self.remaining_requests)
            except NetworkXNoPath:
                print "Stopping, cannot satisfy any more requests"
                break

            min_energy = net.update_along_path(min_path)
            net.prune_edges()

            self.remaining_requests.remove(min_request)
            self.satisfied_requests.append(min_request)
            self.request_solutions.append((min_request, min_path, min_energy))

            #self.satisfied_requests.append((src, dest))
            self.multiply_weight_along_path(net, min_path)

            total_energy += min_energy

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

    def minimum_weighted_path(self, net, requests):
        min_path = None
        min_request = None
        min_path_value = None
        for src, dest in requests:
            try:
                path = net.shortest_path(src, dest, weight="weight")
                path_value = net.shortest_path_length(src, dest, weight="weight")
            except NetworkXNoPath:
                pass
            if min_path is None or path_value < min_path_value:
                min_path = path
                min_path_value = path_value
                min_request = (src, dest)

        return (min_request, min_path, min_path_value)

    def multiply_weight_along_path(self, net, path):
        for index, value in enumerate(path[:-1]):
            net[path[index]][path[index+1]]["weight"] *= self.beta

    def calculate_beta(self, net):
        epsilon = (net.min_energy + net.max_energy) / float(2)
        m = len(net.edges())
        beta = m ** (float(1) / (epsilon + 1) )
        return beta

    def draw(self, output_file=None, requests=None):
        if requests is None:
            requests = self.satisfied_requests
        self.net.draw(output_file=output_file, requests=requests)

if __name__ == "__main__":
    gdp = GDP()
    gdp.run()
