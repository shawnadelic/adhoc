from oml import OML
from mecbe import MECBE
from gdp import GDP

config = {
            "node_count": 100,
            "width": 1000,
            "height": 1000,
            "transmission_range": 200,
            "min_energy": 5000000000,
            "max_energy": 5000000000,
            "packet_size": 512,
            "number_of_requests": 20,
            "seed": 0,
            "output_path": True,
}

oml = OML(**config)
mecbe = MECBE(**config)
gdp = GDP(**config)

print "**************************************************************************************"
print "Running OML"
print "**************************************************************************************"
oml.run()
oml.draw(output_file="plot-oml.svg")
print
print "**************************************************************************************"
print "Running MECBE"
print "**************************************************************************************"
mecbe.run()
mecbe.draw(output_file="plot-mecbe.svg")
print
print "**************************************************************************************"
print "Running GDP"
print "**************************************************************************************"
gdp.run()
gdp.draw(output_file="plot-gdp.svg")
