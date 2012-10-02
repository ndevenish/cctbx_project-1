
import os, sys

defaults = {
    ("H", "H") : 0.579,
    ("H", "Li") : 1.629,
    ("H", "Be") : 1.334,
    ("H", "B") : 1.115,
    ("H", "C") : 0.970,
    ("H", "N") : 0.907,
    ("H", "O") : 0.885,
    ("H", "F") : 1.037,
    ("H", "Na") : 1.907,
    ("H", "Mg") : 1.713,
    ("H", "Al") : 1.582,
    ("H", "Si") : 1.478,
    ("H", "P") : 1.301,
    ("H", "S") : 1.186,
    ("H", "Cl") : 1.202,
    ("Li", "Li") : 2.806,
    ("Li", "Be") : 2.471,
    ("Li", "B") : 2.235,
    ("Li", "C") : 2.004,
    ("Li", "N") : 1.749,
    ("Li", "O") : 1.590,
    ("Li", "F") : 1.555,
    ("Li", "Na") : 2.998,
    ("Li", "Mg") : 2.856,
    ("Li", "Al") : 2.692,
    ("Li", "Si") : 2.519,
    ("Li", "P") : 2.373,
    ("Li", "S") : 2.189,
    ("Li", "Cl") : 2.071,
    ("Be", "Be") : 2.121,
    ("Be", "Be", 2) : 4.190,
    ("Be", "B") : 1.904,
    ("Be", "B", 2) : 2.036,
    ("Be", "C") : 1.697,
    ("Be", "C", 2) : 1.541,
    ("Be", "N") : 1.501,
    ("Be", "N", 2) : 1.333,
    ("Be", "O") : 1.400,
    ("Be", "O", 2) : 1.295,
    ("Be", "F") : 1.366,
    ("Be", "Na") : 2.741,
    ("Be", "Mg") : 2.534,
    ("Be", "Mg", 2) : 4.480,
    ("Be", "Al") : 2.372,
    ("Be", "Al", 2) : 4.589,
    ("Be", "Si") : 2.220,
    ("Be", "Si", 2) : 2.341,
    ("Be", "P") : 2.074,
    ("Be", "P", 2) : 1.907,
    ("Be", "S") : 1.918,
    ("Be", "S", 2) : 1.732,
    ("Be", "Cl") : 1.811,
    ("B", "B") : 1.778,
    ("B", "B", 2) : 1.631,
    ("B", "C") : 1.663,
    ("B", "C", 2) : 1.469,
    ("B", "N") : 1.534,
    ("B", "N", 2) : 1.394,
    ("B", "O") : 1.440,
    ("B", "O", 2) : 1.374,
    ("B", "F") : 1.355,
    ("B", "Na") : 2.537,
    ("B", "Mg") : 2.319,
    ("B", "Mg", 2) : 4.210,
    ("B", "Al") : 2.154,
    ("B", "Al", 2) : 2.077,
    ("B", "Si") : 2.042,
    ("B", "Si", 2) : 1.820,
    ("B", "P") : 1.949,
    ("B", "P", 2) : 1.855,
    ("B", "S") : 1.909,
    ("B", "S", 2) : 1.909,
    ("B", "Cl") : 1.820,
    ("C", "C") : 1.491,
    ("C", "C", 2) : 1.365,
    ("C", "N") : 1.430,
    ("C", "N", 2) : 1.301,
    ("C", "O") : 1.374,
    ("C", "O", 2) : 1.222,
    ("C", "F") : 1.329,
    ("C", "Na") : 2.328,
    ("C", "Mg") : 2.105,
    ("C", "Mg", 2) : 2.198,
    ("C", "Al") : 1.973,
    ("C", "Al", 2) : 1.776,
    ("C", "Si") : 1.890,
    ("C", "Si", 2) : 1.695,
    ("C", "P") : 1.826,
    ("C", "P", 2) : 1.709,
    ("C", "S") : 1.766,
    ("C", "S", 2) : 1.663,
    ("C", "Cl") : 1.728,
    ("N", "N") : 1.350,
    ("N", "N", 2) : 1.226,
    ("N", "O") : 1.297,
    ("N", "O", 2) : 1.222,
    ("N", "F") : 1.360,
    ("N", "Na") : 2.080,
    ("N", "Mg") : 1.895,
    ("N", "Mg", 2) : 1.925,
    ("N", "Al") : 1.770,
    ("N", "Al", 2) : 1.597,
    ("N", "Si") : 1.725,
    ("N", "Si", 2) : 1.576,
    ("N", "P") : 1.653,
    ("N", "P", 2) : 1.581,
    ("N", "S") : 1.629,
    ("N", "S", 2) : 1.566,
    ("N", "Cl") : 1.306,
    ("O", "O") : 1.262,
    ("O", "O", 2) : 1.270,
    ("O", "F") : 1.128,
    ("O", "Na") : 1.920,
    ("O", "Mg") : 1.754,
    ("O", "Mg", 2) : 1.739,
    ("O", "Al") : 1.693,
    ("O", "Al", 2) : 1.572,
    ("O", "Si") : 1.650,
    ("O", "Si", 2) : 1.502,
    ("O", "P") : 1.558,
    ("O", "P", 2) : 1.497,
    ("O", "S") : 1.466,
    ("O", "S", 2) : 1.443,
    ("O", "Cl") : 1.400,
    ("F", "F") : 1.179,
    ("F", "Na") : 1.886,
    ("F", "Mg") : 1.730,
    ("F", "Al") : 1.640,
    ("F", "Si") : 1.601,
    ("F", "P") : 1.559,
    ("F", "S") : 1.548,
    ("F", "Cl") : 1.369,
    ("Na", "Na") : 3.164,
    ("Na", "Mg") : 3.094,
    ("Na", "Al") : 2.954,
    ("Na", "Si") : 2.814,
    ("Na", "P") : 2.551,
    ("Na", "S") : 2.514,
    ("Na", "Cl") : 2.397,
    ("Mg", "Mg") : 2.915,
    ("Mg", "Mg", 2) : 5.197,
    ("Mg", "Al") : 2.771,
    ("Mg", "Al", 2) : 4.774,
    ("Mg", "Si") : 2.618,
    ("Mg", "Si", 2) : 2.820,
    ("Mg", "P") : 2.478,
    ("Mg", "P", 2) : 2.359,
    ("Mg", "S") : 2.318,
    ("Mg", "S", 2) : 2.149,
    ("Mg", "Cl") : 2.213,
    ("Al", "Al") : 2.615,
    ("Al", "Al", 2) : 2.763,
    ("Al", "Si") : 2.480,
    ("Al", "Si", 2) : 2.382,
    ("Al", "P") : 2.368,
    ("Al", "P", 2) : 2.144,
    ("Al", "S") : 2.195,
    ("Al", "S", 2) : 1.993,
    ("Al", "Cl") : 2.111,
    ("Si", "Si") : 2.362,
    ("Si", "Si", 2) : 2.130,
    ("Si", "P") : 2.283,
    ("Si", "P", 2) : 2.063,
    ("Si", "S") : 2.156,
    ("Si", "S", 2) : 1.938,
    ("Si", "Cl") : 2.074,
    ("P", "P") : 2.148,
    ("P", "P", 2) : 2.086,
    ("P", "S") : 2.021,
    ("P", "S", 2) : 1.950,
    ("P", "Cl") : 2.020,
    ("S", "S") : 2.011,
    ("S", "S", 2) : 1.986,
    ("S", "Cl") : 2.110,
    ("Cl", "Cl") : 1.410,
  }

def get_default_bondlength(s1, s2, order=1):
  if len(s1)==1: s1=s1.upper()
  if len(s2)==1: s2=s2.upper()
  s1=s1.strip()
  s2=s2.strip()
  order = int(order)
  for key in [
    (s1, s2, order),
    (s2, s1, order),
    (s1, s2),
    (s2, s1),
    ]:
    if key in defaults:
      return defaults[key]
  return None

if __name__=="__main__":
  print get_default_bondlength(*tuple(sys.argv[1:]))

