from networkx.exception import NetworkXNoPath
from ad_hoc import RandomAdHocNetwork

class MECBE(object):
    def __init__(self, output_path = False, **kwargs):
        self.net = RandomAdHocNetwork(**kwargs)
        self.output_path = output_path
    def run(self):
        self.all_requests = list(self.net.requests)
        self.remaining_requests = list(self.net.requests)
        self.satisfied_requests = []
        self.request_solutions = []
        total_energy = 0
        net_prime = self.net.copy()
        while self.remaining_requests:
            net_prime.prune_edges()
            request = self.remaining_requests.pop()
            src, dest = request 

            try:
                minimum_path = self.minimum_metric_path(net_prime, src, dest)
            except NetworkXNoPath:
                print "Stopping, cannot satisfy request: {} -> {}".format(src, dest)
                break

            request_energy = net_prime.update_along_path(minimum_path)

            self.satisfied_requests.append((src, dest))
            self.request_solutions.append(((src, dest), minimum_path, request_energy))

            total_energy += request_energy

        if self.request_solutions:
            print "Satisfied requests:"
        for request, path, energy in self.request_solutions:
            print
            if self.output_path is True:
                print "Path: {}".format(" -> ".join(path))
            print "Request {} -> {}".format(request[0], request[1])
            print "Energy Consumed: {}".format(energy)
 
        #self.net.draw(requests=self.satisfied_requests)
        print
        print "**************************************************************************************"
        print "Total Requests Satisfied: {}".format(len(self.satisfied_requests))
        print "Total Energy Consumed: {}".format(total_energy)

    def minimum_metric_path(self, net, src, dest):
        temp = net.copy()
        for edge in temp.edges():
            temp_src, temp_dest = edge
            if temp[temp_src][temp_dest]["type"] == "external":
                temp[temp_src][temp_dest]["metric"] = 1/temp.node[temp_src]["energy"]
            else:
                temp[temp_src][temp_dest]["metric"] = 0

        shortest_path = net.shortest_path(src, dest, weight="metric")

        return shortest_path

    def draw(self, output_file=None, requests=None):
        if requests is None:
            requests = self.satisfied_requests
        self.net.draw(output_file=output_file, requests=requests)

if __name__ == "__main__":
    mecbe = MECBE()
    mecbe.run()
