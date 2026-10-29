"""Exact local D-path boundary and symmetric state attribution; not field causality."""
import itertools
import numpy as np

def phi(f,v):return 2*((1-v)/(1+f)+v*f/(1+f*f))
def phi_prime(f,v):return 2*(-(1-v)/(1+f)**2+v*(1-f*f)/(1+f*f)**2)
def hazard(f,d,s,v,c):
 b=1+(1-v)*f+v*f*f
 return d*phi(f,v)*b/(b+c*s)
def elasticities(f,s,v,c):
 b=1+(1-v)*f+v*f*f;bp=1-v+2*v*f
 ef=f*phi_prime(f,v)/phi(f,v)+f*bp/b*c*s/(b+c*s)
 return ef,-c*s/(b+c*s)
def shapley_state(lo,hi,v,c):
 lo=np.asarray(lo);hi=np.asarray(hi);out=np.zeros_like(lo,dtype=float)
 for order in itertools.permutations(range(3)):
  state=lo.copy();prev=hazard(*state.T,v,c)
  for j in order:
   state[:,j]=hi[:,j];now=hazard(*state.T,v,c);out[:,j]+=(now-prev)/6;prev=now
 return out


def hill_hazard(f,d,s,q,c):
 return d*f**(q-1)/(1+f**q+c*s)
def hill_elasticity(f,s,q,c):
 return ((q-1)*(1+c*s)-f**q)/(1+f**q+c*s)
