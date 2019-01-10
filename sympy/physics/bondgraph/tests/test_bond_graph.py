import sympy as sm
from sympy.physics.bond_graph.ports import (Resistor, Compliance, Inertia,
                                            EffortSource, Transformer)
from sympy.physics.bond_graph.graph import FlowJunction

m, k, b, R = sm.symbols('m, k, b, R')

x, v, theta, omega, F, T = me.dynamicsymbols('x, v, theta, omega, F, T')

damper = Resistor(effort=F, flow=v, law=b*v)
# or
damper = Resistor(effort=F, flow=v, lin_coeff=b)

spring = Compliance(effort=F, displacement=x, law=x/k)
# or
spring = Compliance(effort=F, displacement=x, lin_coeff=1/k)

mass = Inertia(effort=F, flow=v, law=m*v.diff())
# or
mass = Inertia(effort=F, flow=v, lin_coeff=m)

force = EffortSource(F)

j1 = FlowJunction(damper, spring, mass, force)

j1.states() == (x, v)
j1.inputs() == (F, )
j1.parameters() == (b, m, k)

eqs = j1.state_equations()
eqs[0] = sm.Eq(x.diff(), v)
eqs[1] = sm.Eq(v.diff(), (-b*v - k*x + F)/m)

print(j1.bonds)
"""
Bonds attached to this flow junction (1):
0 : F = b*v
1 : F = x/C
2 : F = m*dv/dt
3 : F = F
"""
del j1.bonds[3]  # remove the force source bond

torque = EffortSource(T)

wheel = Transformer(input=(T, omega), output=(F, v), lin_coeff=R)

j1.add_input(wheel)

# .in throws a syntax error
graph = EffortJunction(inthing=(torque), outthing=(wheel.inthing))

print(graph)
"""
                      I
                      ^
                      |
Se |--> 0 |--> TF --> 1 --> R
                      |
                      C

Junctions:
- 0 :
- 1 :

"""

graph.states() == (theta, omega)
graph.inputs() == (T, )
graph.parameters == (b, m, k, R)

eqs = graph.state_equations()
eqs[0] = sm.Eq(theta.diff(), omega)
eqs[1] = sm.Eq(omega.diff(), (-b*v - k*x + F)*R/m)
