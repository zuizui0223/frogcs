"""Alternative synthetic D response families, each normalized at F=1."""
import numpy as np
FAMILIES=['constant','II','III','mixed','steep']
def factor(f,v,family,k=1.):
 f=np.asarray(f,float);k=np.asarray(k,float)
 ii=(1+k)/(k+f);iii=(1+k*k)*f/(k*k+f*f);iv=(1+k**3)*f*f/(k**3+f**3)
 family=np.asarray(family)
 codes=family if np.issubdtype(family.dtype,np.integer) else np.select([family==name for name in FAMILIES],range(5),default=-1)
 return np.select([codes==i for i in range(5)],[np.ones_like(f),ii,iii,(1-v)*ii+v*iii,(1-v)*ii+v*iv],default=np.nan)
