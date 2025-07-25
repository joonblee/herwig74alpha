#! /usr/bin/python
from __future__ import print_function
import yoda,os,math,subprocess,optparse
from string import Template
import numpy,matplotlib.pyplot as plt
from scipy.integrate import dblquad as dblquad
from scipy.integrate import quad as quad
import datetime

htmlTemplate=Template("""
<html>
<head>
<title>Tests of Onium Splittings in the Parton Shower</title>
<style>
      html { font-family: sans-serif; }
      img { border: 0; }
      a { text-decoration: none; font-weight: bold; }
    </style>
            <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
          tex2jax: {inlineMath: [["$$","$$"]]}
        });
        </script>
        <script type="text/javascript" async
          src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
        </script>
        </head>
<body>
<section id="OniumTests">
<h1>Tests of Onium splittings in the Parton Shower</h1>
${plots}
</section>

<footer style="clear:both; margin-top:3em; padding-top:3em">
${time}
</footer>

</body>
</html>""")
plotTemplate=Template("""
<div class="plot" id="plot_${id}" style="float:left; font-size:smaller; font-weight:bold;">
  <a href="#MC_Simple_Onium-${id}">&#9875;</a> ${id}:<br/>
  <a name="MC_Simple_Onium-${id}"><a href="${id}.pdf">
    <img src="${id}.png">
  </a></a>
</div>""")
# various test functions
m1=0.
m2=0.
M=0
a1=0
a2=0
aS=0.
R02=0.
mix1=0.
mix2=0.
pTmin=1.
# q -> q 1S0
def D_q_q_1S0(z) :
    return 8./81./math.pi*aS**2*R02*(1.-z)**2*z*(48. + 8.*z**2 - 8.*z**3 + 3.*z**4)/(m1**3*(2. - z)**6)

def D_g_g_1S0(z) :
    return aS**2/24./math.pi*R02/m1**3*(3.*z-2.*z**2+2.*(1.-z)*numpy.log(1.-z))

zz=0.

def upp(r) :
    return 0.5*(1+r)

def low(r) :
    return 0.5*(r+zz**2)/zz
    
def IPsi(y,r) :
    z = zz
    f0 = r**2*(1 + r)*(3 + 12*r + 13*r**2) - 16*r**2*(1 + r)*(1 + 3*r)*y \
        - 2*r*(3 - 9*r - 21*r**2 + 7*r**3)* y**2 + 8*r*(4 + 3*r + 3*r**2)*y**3 \
        - 4*r*(9 - 3*r - 4*r**2)*y**4 - 16*(1 + 3*r + 3*r**2)*y**5 + 8*(6 + 7*r)*y**6 - 32*y**7
    f1 = -2*r*(1 + 5*r + 19*r**2 + 7*r**3)*y + 96*r**2*(1 + r)*y**2 \
        + 8*(1 - 5*r - 22*r**2 - 2*r**3)*y**3 + 16*r*(7 + 3*r)*y**4 - 8*(5 + 7*r)*y**5 + 32*y**6
    f2 = r*(1 + 5*r + 19*r**2 + 7*r**3) - 48*r**2*(1 + r)*y - 4*(1 - 5*r - 22*r**2 - 2*r**3)*y**2 \
        - 8*r*(7 + 3*r)*y**3 + 4*(5 + 7*r)*y**4 - 16*y**5
    g0 = (1 - r)*r**3*(3 + 24*r + 13*r**2) - 4*r**3*(7 - 3*r - 12*r**2)*y \
        - 2*r**3*(17 + 22*r - 7*r**2)*y**2 + 4*r**2*(13 + 5*r - 6*r**2)*y**3 \
        - 8*r*(1 + 2*r + 5*r**2 + 2*r**3)*y**4 - 8*r*(3 - 11*r - 6*r**2)*y**5 + 8*(1 - 2*r - 5*r**2)*y**6
    g1 = -2*(1 - r)*r**2*(1 + r)*(1 + 7*r)*y + 8*(1 - 4*r)*r**2*(1 + 3*r)*y**2 \
        + 4*r*(1 + 10*r + 57*r**2 + 4*r**3)* y**3 - 8*r*(1 + 29*r + 6*r**2)*y**4 - 8*(1 - 8*r - 5*r**2)*y**5
    g2 = (1 - r)*r**2*(1 + r)*(1 + 7*r) - 4*(1 - 4*r)*r**2*(1 + 3*r)*y \
        - 2*r*(1 + 10*r + 57*r**2 + 4*r**3)* y**2 + 4*r*(1 + 29*r + 6*r**2)*y**3 + 4*(1 - 8*r - 5*r**2)*y**4
    c1 = f0+z*f1+z**2*f2
    c2 = g0+z*g1+z**2*g2
    return (c1 + ((1 + r - 2*y)*c2*numpy.log((-r + y + numpy.sqrt(-r + y**2))/(-r + y - numpy.sqrt(-r + y**2))))/(2.*(-r + y)*numpy.sqrt(-r + y**2))) \
        /((1 - y)**2*(-r + y)**2*(-r + y**2)**2)

def D_g_g_3S1(z) :
    global zz
    zz = z
    return 3.*R02/2.*5./5184./numpy.pi**2/m1**3*aS**3*dblquad(IPsi,0.,z,low,upp)[0]

def D_g_g_3P0(x) :
    smin = pTmin**2/x/(1-x)+4.*m1**2/x
    return -aS**2*R02/(6.*m1**3*numpy.pi)*(-9/smin + (16*m1**2*(-2 + x)*(-1 + x))/(-4*m1**2 + smin)**2
                                        + (128*m1**4*(-1 + x)**2)/(3.*(4*m1**2 - smin)**3)
                                        + (2*(11 - 10*x + x**2))/(4*m1**2 - smin) - (3*(-5 + 3*x)*numpy.log(smin))/(2.*m1**2)
                                        + (3*(-5 + 3*x)*numpy.log(-4*m1**2 + smin))/(2.*m1**2))

def D_g_g_3P1(x) :
    smin = pTmin**2/x/(1-x)+4.*m1**2/x
    return -aS**2*R02/(m1**3*numpy.pi)*((-1 + 2*(1 - x) - 2*(1 - x)**2)/(-4*m1**2 + smin) - (4*m1**2*(1 - x))/(-4*m1**2 + smin)**2 + (32*m1**4*(1 - x)**2)/(3.*(-4*m1**2 + smin)**3))

def D_g_g_3P2(x) :
    smin = pTmin**2/x/(1-x)+4.*m1**2/x
    return -aS**2*R02/(3.*m1**3*numpy.pi)*(-6/smin + (-7 - 10*(1 - x) - 2*(1 - x)**2)/(-4*m1**2 + smin) + (4*m1**2*(1 + 4*(1 - x))*(1 - x))/(-4*m1**2 + smin)**2 - 
                                         (32*m1**4*(1 - x)**2)/(3.*(-4*m1**2 + smin)**3) + (3*(2 - x)*numpy.log(smin))/m1**2 - (3*(2 - x)*numpy.log(-4*m1**2 + smin))/m1**2)

# q -> q 3S1
def D_q_q_3S1(z) :
    return 8./math.pi*aS**2*R02*(1.-z)**2*z*(16.-32.*z+72.*z**2-32.*z**3+5.*z**4)/(27.*m1**3*(2.-z)**6)
# q -> q 3P0
def D_q_q_3P0(z):
     return 9./2./math.pi*R02*16.*aS**2*(1-z)**2*z*(192+384*z+528*z**2-1376*z**3 +1060*z**4-376*z**5+59*z**6)/(729.*m1**5*(2 - z)**8)
# q -> q 3P1
def D_q_q_3P1(z) :
    return 9./2./math.pi*R02*64.*aS**2*(1 - z)**2*z*(96 - 288*z +   496*z**2 -   408*z**3 +   202*z**4 -   54*z**5 + 7*z**6)/(243.*m1**5*(2 - z)**8)
# q -> q 3P2
def D_q_q_3P2(z):
    return 9./2./math.pi*R02*128*aS**2*(1 - z)**2*z*(48 - 192*z +   480*z**2 -   668*z**3 +   541*z**4 -   184*z**5 + 23*z**6)/(729.*m1**5*(2 - z)**8)
# q -> q 1P1
def D_q_q_1P1(z) :
    return 9./2./math.pi*R02*16*aS**2*(1 - z)**2*z*(64 - 128*z +   176*z**2 -   160*z**3 +   140*z**4 - 56*z**5+9*z**6)/(81.*m1**5*(2-z)**8)
# q -> q 1D2
def D_q_q_1D2(x) :
    return 8.*aS**2*R02/math.pi*(1 - x)**2*x*(3840-15360*x+30720*x**2-37120*x**3+35328*x**4-29344*x**5+18344*x**6-5848*x**7+775*x**8)/(81.*m1**7*(2 - x)**10)
# q -> q 3D1
def D_q_q_3D1(x) :
     return 8*aS**2*R02/math.pi*(1 - x)**2*x*(17280 - 103680*x + 321120*x**2 - 551840*x**3 + 546744*x**4 - 314752*x**5 + 112402*x**6 - 24594*x**7 + 2915*x**8)/(405.*m1**7*(2 - x)**10)
# q -> q 3D2
def D_q_q_3D2(x) :
     return 16*aS**2*R02/math.pi*(1 - x)**2*x*(2880 - 14400*x + 37360*x**2 - 58240*x**3 + 58604*x**4 - 38372*x**5 + 16517*x**6 - 4014*x**7 + 445*x**8)/(81.*m1**7*(2 - x)**10)
# q -> q 3D3
def D_q_q_3D3(x) :
     return 8*aS**2*R02/math.pi*(1 - x)**2*x*(11520 - 69120*x + 231680*x**2 - 488960*x**3 + 675136*x**4 - 592288*x**5 + 309688*x**6 - 80736*x**7 + 8285*x**8)/(405.*m1**7*(2 - x)**10)
# q -> q' 1S0
def D_q_qp_1S0(z) :
    W0 =  2.*(1.+z*a1)**2*(1.-z)
    W1 = -2.*(2.*z**2*a2**2-z**2*a2 -4.*z*a2**2+4.*z*a2 -3.*z+4.*a2-2.)*(1.-z*a2)
    W2 = -8.*(1.-z*a2)**2*a1*a2
    deltaX = z*(1.-z)/(1.-a2*z)**2
    return 2.*aS**2/27./M**3*R02/math.pi/a1**2/(1.-a2*z)**2* \
        (W0*deltaX+W1*deltaX**2/2.+W2*deltaX**3/3.)
# q -> q' 3S1
def D_q_qp_3S1(z) :
    W0 =  2.*((1.+z*a1)**2+2.*z**2)*(1.-z)
    W1 = -2.*(2.*z**2*a2**2 -3.*z**2*a2 +4.*z*a2**2 + 4.*z*a2 -9.*z - 4.*a2+6.)*(1.-z*a2)
    W2 = -24.*(1.-z*a2)**2*a1*a2
    deltaX = z*(1.-z)/(1.-a2*z)**2
    return 2.*aS**2/27./math.pi/M**3*R02/a1**2/(1.-a2*z)**2* \
         (W0*deltaX+W1*deltaX**2/2.+W2*deltaX**3/3.)
# q ->q' 3P0
def D_q_qp_3P0(z) :
    W0 =  ( 4.*a2 - 3. - 8*z*a2**2 + 10*z*a2 - 3*z + 4*z**2*a2**3 - 5*z**2*a2**2 + z**2*a2 )**2*(1.-z)/96./a2**2
    W1 =  ((-1 + z*a2)**2*(18 + 27*z - 12*a2 +   18*z*a2 + 30*z**2*a2 -   40*a2**2 -   152*z*a2**2 -   206*z**2*a2**2 -   9*z**3*a2**2 +   32*a2**3 +   176*z*a2**3 +   324*z**2*a2**3 +   58*z**3*a2**3 -   64*z*a2**4 -   184*z**2*a2**4 -   80*z**3*a2**4 +   32*z**2*a2**5 +   32*z**3*a2**5))/(96.*a2**2)
    W2 = (2*a2*(7.*a2-6.*z) -10.*a2-3. -2.*z*a2**2*(7.*a2-12.) -z**2*a2**2*(2.*a2-3.))*a1*(1.-z*a2)**3/(12.*a2)
    W3 = 2.*a1**2*a2*(1.-z*a2)**4/3.
    deltaX = z*(1.-z)/(1.-a2*z)**2
    return 32.*aS**2/9./math.pi*R02/a1**4/(1.-a2*z)**4/M**5* \
        (W0*deltaX+W1*deltaX**2/2.+W2*deltaX**3/3.+W3*deltaX**4/4.)
# q ->q' 3P2
def D_q_qp_3P2(z) :
    W0 =  (2 + 4*z + 9*z**2 +  10*z**3 + 5*z**4 -  8*z*a2 - 16*z**2*a2 -  28*z**3*a2 -  20*z**4*a2 +  12*z**2*a2**2 +  20*z**3*a2**2 +  24*z**4*a2**2 -  8*z**3*a2**3 -  8*z**4*a2**3 +  2*z**4*a2**4)*(1.-z)/24.   
    W1 = (-20 - 13*z + 8*z**2 +  30*z**3 + 16*a2 +  52*z*a2 - 30*z**2*a2 -  28*z**3*a2 -  32*z*a2**2 +  4*z**2*a2**2 -  7*z**3*a2**2 +  16*z**2*a2**3 +  4*z**3*a2**3)*(1.-z*a2)**2/24.
    W2 = ( -26*a2 + 34 + 26.*z*a2**2 + 18*z*a2 - 45*z + 8*z**2*a2**2 - 15*z**2*a2 )*a1*(1.-z*a2)**3/12.
    W3 = 10./3.*a1**2*a2*(1.-z*a2)**4
    deltaX = z*(1.-z)/(1.-a2*z)**2
    return 32.*aS**2/9./math.pi*R02/a1**4/(1.-a2*z)**4/M**5* \
        (W0*deltaX+W1*deltaX**2/2.+W2*deltaX**3/3.+W3*deltaX**4/4.)
# q to q' 1P1
def D_q_qp_1P1(z) :
    W0 =  (1.-z)*(1 + z*(2 - 4*a2) +   z**4*(2 + a1**2)*   a2**2 +   z**2*(3 - 2*a1*a2) +   2*z**3*a2*   (-1 - 3*a2 + 2*a2**2))/32./a2**2
    W1 = ((-1 + z*a2)**2*   (-6 + 12*a2 - 8*a2**2 +  z**3*a2**2*  (13 - 38*a2 + 24*a2**2)   + 2*z**2*a2*  (5 + 17*a2 - 26*a2**2 + 4*a2**3) + z*  (9 - 38*a2 + 16*a2**2 + 16*a2**3)))/(32.*a2**2)
    W2 = (-1.+(6.-10.*z)*a2-(2.-4.*z+z**2)*a2**2+2.*z*(1.+z)*a2**3)*a1*(1.-z*a2)**3/4./a2
    W3 = 2.*a1**2*a2*(1.-z*a2)**4
    deltaX = z*(1.-z)/(1.-a2*z)**2
    return 32.*aS**2/9.*R02/math.pi/a1**4/(1.-a2*z)**4/M**5* \
        (W0*deltaX+W1*deltaX**2/2.+W2*deltaX**3/3.+W3*deltaX**4/4.)
# q to q' 3P1
def D_q_qp_3P1(z) :
    W0 = -((-1 + z)*(1 + 2*z + 3*z**2 -   4*z*a2 - 10*z**2*a2 -   2*z**3*a2 +   8*z**2*a2**2 +   6*z**3*a2**2 +   z**4*a2**2 -   4*z**3*a2**3 -   2*z**4*a2**3 +   z**4*a2**4))/a2**2/16.
    W1 = ((-1 + z*a2)**2*   (-6 + 9*z + 4*a2 -  10*z*a2 + 10*z**2*a2 +  6*z*a2**2 -  22*z**2*a2**2 +  z**3*a2**2 +  8*z**2*a2**3 -  2*z**3*a2**3 +  2*z**3*a2**4))/ (16.*a2**2)
    W2 = -(a1*(-1 + z*a2)**3*(-2 + 6*a2 - 11*z*a2 -   2*a2**2 + 6*z*a2**2 +   z**2*a2**2 + 2*z*a2**3))/a2/4.
    W3 = 2.*a1**2*a2*(-1 + z*a2)**4
    deltaX = z*(1.-z)/(1.-a2*z)**2
    return 32.*aS**2/9.*R02/math.pi/a1**4/(1.-a2*z)**4/M**5* \
        (W0*deltaX+W1*deltaX**2/2.+W2*deltaX**3/3.+W3*deltaX**4/4.)
# q to q' P1
def D_q_qp_P1(z) :
    W0 = -0.25*((-1 + z)*   (1 + z* (2 + 3*z +   a2*  (-3 +   z*  (-4 + a2 +   (-1 + a2)**2*  z)))))/ (a2**2*   (-1 + a2*z)**3)
    W1 = (6 - 9*z +   a2*   (-8 + 4*a2 + 24*z - 4*a2* (3 + 2*a2)*z + 2* (-5 + a2 +   2*a2**2*  (2 + a2))* z**2 + a2* (11 +   4*(-4 + a2)*  a2)*z**3))/(4.*a2**2*  (-1 + a2*z)**2)
    W2 = 2.*(-1 + a2)*  (-1 + 3*a2 +(-2 + a2)*a2*z)/a2
    deltaX = z*(1.-z)/(1.-a2*z)**2
    mixed=16.*aS**2/9.*R02/math.pi/a1**4/M**5/math.sqrt(2.)* \
        (W0*deltaX+W1*deltaX**2/2.+W2*deltaX**3/3.)
    return mix1**2*D_q_qp_1P1(z)+mix2**2*D_q_qp_3P1(z)+mix1*mix2*mixed

# q ->q' 3D1
def D_q_qp_3D1(x) :
    return (aS**2*R02/math.pi*(1 - x)**2*x*(60*(1 + 4*a1)**2 - 60*(1 + 4*a1)*(7 + 36*a1 - 28*a1**2)*x + 5*(261 + 2652*a1 + 6128*a1**2 - 12576*a1**3 + 7360*a1**4)*x**2 + 10*(-237 - 2589*a1 - 8754*a1**2 + 27528*a1**3 - 28808*a1**4 + 11360*a1**5)*x**3 + (2775 + 31350*a1 + 156435*a1**2 - 648372*a1**3 + 909816*a1**4 - 613056*a1**5 + 183552*a1**6)*x**4 - 4*(540 + 6585*a1 + 49910*a1**2 - 166879*a1**3 + 201928*a1**4 - 115084*a1**5 + 28400*a1**6)*a2*x**5 + (1095 + 13830*a1 + 142935*a1**2 - 389916*a1**3 + 377696*a1**4 - 164320*a1**5 + 36800*a1**6)*a2**2*x**6 - 2*(165 + 2100*a1 + 27645*a1**2 - 58086*a1**3 + 42360*a1**4 - 15720*a1**5 + 3360*a1**6)*a2**3*x**7 + 5*(9 + 114*a1 + 1817*a1**2 - 2524*a1**3 + 1676*a1**4 - 672*a1**5 + 192*a1**6)*a2**4*x**8))/(3240.*(1 - a2)**6*a2**2*M**7*(1 - a2*x)**10)
# q ->q' 3D3
def D_q_qp_3D3(x) :
    return  2.*aS**2*R02/math.pi*(1 - x)**2*x*(90 + 90*(-7 + 2*a1)*x + 5*(399 - 174*a1 + 200*a1**2)*x**2 + 10*(-378 + 193*a1 - 437*a1**2 + 70*a1**3)*x**3 +  (4725 - 2900*a1 + 8390*a1**2 - 1918*a1**3 + 2268*a1**4)*x**4 + 2*(-1995 + 1700*a1 - 4930*a1**2 + 1617*a1**3 - 2387*a1**4 + 350*a1**5)*x**5 +  (2205 - 2830*a1 + 7940*a1**2 - 5194*a1**3 + 4914*a1**4 - 930*a1**5 + 1000*a1**6)*x**6 -  2*(360 - 325*a1 + 1680*a1**2 - 749*a1**3 + 1540*a1**4 + 295*a1**5 + 90*a1**6)*a2*x**7 +  5*(21 - 14*a1 + 133*a1**2 - 56*a1**3 + 189*a1**4 - 18*a1**5 + 18*a1**6)*a2**2*x**8)/(405.*a1**6*M**7*(1 - a2*x)**10)

def D_q_qp_3D2(x) :
     return aS**2*R02/math.pi*(-1 + x)**2*x*(180 + 180*(-7 + 4*a1)* x + 5* (777 - 852*a1 +464*a1**2 -64*a1**3 +128*a1**4)*x**2 - 10* (693 - 1087*a1 +1126*a1**2 -624*a1**3 +112*a1**4 +128*a1**5)*x**3 + (7875 -15650*a1 +23295*a1**2 -22564*a1**3 +9112*a1**4 +128*a1**5 +2304*a1**6)*x**4+ 4* (-1470 +2005*a1 -4740*a1**2 +4613*a1**3 -2296*a1**4 +488*a1**5 +320*a1**6)*a2* x**5 + (2835 - 2050*a1 +12035*a1**2 -8332*a1**3 +5952*a1**4 -960*a1**5 +640*a1**6)* a2**2*x**6 + 2* (-405 + 40*a1 -2565*a1**2 +602*a1**3 -1000*a1**4 +320*a1**5)* a2**3*x**7 + 5* (21 + 10*a1 +205*a1**2 +52*a1**3 +84*a1**4)*a2**4* x**8)/(648.*a1**6*a2**2*M**7*(-1 + a2*x)**10)

def D_q_qp_1D2(x) :
    return (aS**2*R02/math.pi*(-1 + x)**2*x*(60 - 60* (7 - 8*a1 +4*a1**2)*x + 5* (267 - 600*a1 +580*a1**2 -160*a1**3 +64*a1**4)*x**2 - 10* (255 - 825*a1 +1130*a1**2 -596*a1**3 +88*a1**4 +64*a1**5)*x**3 + (3225 -13050*a1 +22585*a1**2 -16872*a1**3 +5036*a1**4 -576*a1**5 +1152*a1**6)*x**4+ 4* (-690 + 2535*a1 -4200*a1**2 +2279*a1**3 -968*a1**4 +524*a1**5 +160*a1**6)*a2* x**5 + (1545 - 4890*a1 +8525*a1**2 -2176*a1**3 +3076*a1**4 -320*a1**5 +320*a1**6)* a2**2*x**6 - 2* (255 - 660*a1 +1475*a1**2 +174*a1**3 +740*a1**4 +120*a1**5)* a2**3*x**7 + 5* (15 - 30*a1 +107*a1**2 +56*a1**3 +80*a1**4)*a2**4* x**8))/(324.*a1**6*a2**2*M**7*(-1 + a2*x)**10)

def D_q_qp_D2(x) :
    return mix1**2*D_q_qp_1D2(x)+mix2**2*D_q_qp_3D2(x)+mix1*mix2*(aS**2*5.*R02/math.pi*(-1 + x)**2*x*(-12 + 12* (5 - 4*a1 +2*a1**2)*x - (129 - 198*a1 +156*a1**2 +64*a1**3)*x**2 + 4* (39 - 85*a1 +76*a1**2 -8*a1**3 +36*a1**4)*x**3 - 2* (57 - 156*a1 +133*a1**2 -130*a1**3 +198*a1**4 +48*a1**5)*x**4 - 4* (-12 + 27*a1 -4*a1**2 +51*a1**3 +2*a1**4 +14*a1**5)*a2* x**5 + (-9 + 16*a1 +11*a1**2 +62*a1**3 +4*a1**4)*a2**2* x**6))/(54.*math.sqrt(6.)*a1**6*a2**2*M**7*(-1 + a2*x)**8)

def D_cc1(z) :
    return 4.*aS**2*R02*(1.-z)**2*z*(16.-32.*z+72.*z**2-32.*z**3+5.*z**4)/(9.*m1**3*math.pi*(2.-z)**6)

def D_bc0(z) :
    return aS**2*a1*R02*(1 - z)**2*z*(6 - 18*(1 - 2*a1)*z + (21 - 74*a1 + 68*a1**2)*z**2 - 2*(1 - a1)*(6 - 19*a1 + 18*a1**2)*z**3 + 3*(1 - a1)**2*(1 - 2*a1 + 2*a1**2)*z**4)/(54.*m1**3*math.pi*(1 - (1 - a1)*z)**6)

def D_bc1(z) :
    return aS**2*a1*R02*(1 - z)**2*z*(2 - 2*(3 - 2*a1)*z + 3*(3 - 2*a1 + 4*a1**2)*z**2 - 2*(1 - a1)*(4 - a1 + 2*a1**2)*z**3 + (1 - a1)**2*(3 - 2*a1 + 2*a1**2)*z**4)/(18.*m1**3*math.pi*(1 - (1 - a1)*z)**6)

# analytic line
def fragmentation(funct,scale,step) :
    x = []
    y = []
    xe=step
    while xe<1. :
        x.append(xe)
        y.append(funct(x[-1])*scale)
        xe+=step
    return (x,y)

# latex for plots
latexName = {441  : "\\eta_c", 443    : "J/\\psi", 100441 : "\\eta_c(2S)", 100443 : "\psi(2S)",
             
             10443 : "h_c", 10441: "\\chi_{c0}", 20443: "\\chi_{c1}",  445: "\\chi_{c2}",

             30443 : "\\psi(3770)" , 20445 : "\\psi_2(1D)", 447 : "\\psi_3(1D)",
             
             551  : "\\eta_b", 553 : "\\Upsilon" , 100551 : "\\eta_b(2S)", 100553 : "\\Upsilon(2S)", 200551 : "\\eta_b(3S)", 200553 : "\\Upsilon(3S)", 300553 : "\\Upsilon(4S)",
             
             10553 : "h_b", 10551: "\\chi_{b0}", 20553: "\\chi_{b1}",  555: "\\chi_{b2}",
             
             110553 : "h_b(2P)", 110551: "\\chi_{b0}(2P)", 120553: "\\chi_{b1}(2P)",  100555: "\\chi_{b2}(2P)",
             210553 : "h_b(3P)", 210551: "\\chi_{b0}(3P)", 220553: "\\chi_{b1}(3P)",  200555: "\\chi_{b2}(3P)",

             10555 : "\\eta_{b2}", 30553 : "\\Upsilon_1(1D)", 20555 : "\\Upsilon_2(1D)", 557 : "\\Upsilon_3(1D)",
             
             541 : "B_c^+", 543 : "B_c^{*+}", 10541 : "B_{c0}^{*+}", 545 : "B_{c2}^{*+}",
             100541 : "B_c(2S)^+", 100543 : "B_c(2S)^{*+}", 10543 : "B_{c1}^+", 20543 : "B_{c1}^{\\prime+}",
             30543 : "B_c(1D)^{*+}", 547 : "B_{c3}(1D)^{*+}", 20545 : "B_{c2}(H)^{+}", 10545 : "B_{c2}(L)^+",
              4403 : "(cc)_1", 5503 : "(bb)_1", 5401 : "(bc)_0", 5403 : "(bc)_1"  }


herwigName = {441 : "eta_c"  , 443 : "Jpsi"    , 100441 : "eta_c(2S)"    , 100443 : "psi(2S)", 
              10443 : "h_c", 10441: "chi_c0", 20443: "chi_c1",  445: "chi_c2",
              30443 : "psi(3770)" , 20445 : "psi_2(1D)", 447 : "psi_3(1D)",
              
              551 : "eta_b"  , 553 : "Upsilon" , 100551 : "eta_b(2S)"    , 100553 : "Upsilon(2S)", 200551 : "eta_b(3S)", 200553 : "Upsilon(3S)", 300553 : "Upsilon(4S)",
              10553 : "h_b", 10551: "chi_b0", 20553: "chi_b1",  555: "chi_b2",
              110553 : "h_b(2P)", 110551: "chi_b0(2P)", 120553: "chi_b1(2P)",  100555: "chi_b2(2P)",
              210553 : "h_b(3P)", 210551: "chi_b0(3P)", 220553: "chi_b1(3P)",  200555: "chi_b2(3P)",
              10555 : "eta_b2", 30553 : "Upsilon_1(1D)", 20555 : "Upsilon_2(1D)", 557 : "Upsilon_3(1D)",
              
              541 : "B_c+", 543 : "B_c*+", 10541 : "B*_c0+", 545 : "B_c2+", 10543 : "B_c1+", 20543 : "B'_c1+",
              100541 : "B_c(2S)+", 100543 : "B_c(2S)*+",
              30543 : "B_c(1D)*+", 547 : "B_c3(1D)*+", 20545 : "B_c2(H)+", 10545 : "B_c2(L)+",

              4403 : "cc_1", 5503 : "bb_1", 5401 : "bc_0", 5403 : "bc_1" }


# splitting tests
testParameters={ "ctocEta_c"     : [441    ,"ctoc11S0SplittingSudakov",4,"ccbar","1S",0.26,1.5,4.9,0.8**3,5e2    ,D_q_q_1S0,10**4],
                 "ctocJPsi"      : [443    ,"ctoc13S1SplittingSudakov",4,"ccbar","1S",0.26,1.5,4.9,0.8**3,5e2    ,D_q_q_3S1,10**4],
                 "ctocEta_c2S"   : [100441 ,"ctoc21S0SplittingSudakov",4,"ccbar","2S",0.26,1.5,4.9,0.6966,5e2    ,D_q_q_1S0,10**4],
                 "ctocPsi2S"     : [100443 ,"ctoc23S1SplittingSudakov",4,"ccbar","2S",0.26,1.5,4.9,0.6966,5e2    ,D_q_q_3S1,10**4],

                 "gtogEta_c"     : [441    ,"gtogcc11S0SplittingSudakov",21,"ccbar","1S",0.26,1.5,4.9,0.8**3,5e2    ,D_g_g_1S0,10**4],
                 "gtogJPsi"      : [443    ,"gtogcc13S1SplittingSudakov",21,"ccbar","1S",0.26,1.5,4.9,0.8**3,5e4    ,D_g_g_3S1,10**6],
                 "gtogEta_c2S"   : [100441 ,"gtogcc21S0SplittingSudakov",21,"ccbar","2S",0.26,1.5,4.9,0.6966,5e2    ,D_g_g_1S0,10**4],
                 "gtogPsi2S"     : [100443 ,"gtogcc23S1SplittingSudakov",21,"ccbar","2S",0.26,1.5,4.9,0.6966,5e4    ,D_g_g_3S1,10**6],

                 "gtogChi_c0"    : [10441  ,"gtogcc13P0SplittingSudakov",21,"ccbar","1P",0.26,1.5,4.9,0.1296,5e2    ,D_g_g_3P0,10**7],
                 "gtogChi_c1"    : [20443  ,"gtogcc13P1SplittingSudakov",21,"ccbar","1P",0.26,1.5,4.9,0.1296,5e2    ,D_g_g_3P1,10**6],
                 "gtogChi_c2"    : [  445  ,"gtogcc13P2SplittingSudakov",21,"ccbar","1P",0.26,1.5,4.9,0.1296,5e2    ,D_g_g_3P2,10**6],

                 "ctocH_c"       : [10443  ,"ctoc11P1SplittingSudakov",4,"ccbar","1P",0.26,1.5,4.9,0.1296,5e2    ,D_q_q_1P1,10**4],
                 "ctocChi_c0"    : [10441  ,"ctoc13P0SplittingSudakov",4,"ccbar","1P",0.26,1.5,4.9,0.1296,5e2    ,D_q_q_3P0,10**4],
                 "ctocChi_c1"    : [20443  ,"ctoc13P1SplittingSudakov",4,"ccbar","1P",0.26,1.5,4.9,0.1296,5e2    ,D_q_q_3P1,10**4],
                 "ctocChi_c2"    : [  445  ,"ctoc13P2SplittingSudakov",4,"ccbar","1P",0.26,1.5,4.9,0.1296,5e2    ,D_q_q_3P2,10**4],
                 "ctocPsi3770"   : [30443  ,"ctoc13D1SplittingSudakov",4,"ccbar","1D",0.26,1.5,4.9,0.0329,5e3    ,D_q_q_3D1,10**5],
                 "ctocPsi_2"     : [20445  ,"ctoc13D2SplittingSudakov",4,"ccbar","1D",0.26,1.5,4.9,0.0329,5e3    ,D_q_q_3D2,10**5],
                 "ctocPsi_3"     : [  447  ,"ctoc13D3SplittingSudakov",4,"ccbar","1D",0.26,1.5,4.9,0.0329,5e3    ,D_q_q_3D3,10**5],

                 "btobEta_b"     : [551     ,"btob11S0SplittingSudakov",5,"bbbar","1S",0.19,1.5,4.9,1.8**3,5e3   ,D_q_q_1S0,10**5],
                 "btobUpsilon"   : [553     ,"btob13S1SplittingSudakov",5,"bbbar","1S",0.19,1.5,4.9,1.8**3,5e3   ,D_q_q_3S1,10**5],
                 "btobEta_b2S"   : [100551  ,"btob21S0SplittingSudakov",5,"bbbar","2S",0.19,1.5,4.9,2.8974,5e3   ,D_q_q_1S0,10**5],
                 "btobUpsilon2S" : [100553  ,"btob23S1SplittingSudakov",5,"bbbar","2S",0.19,1.5,4.9,2.8974,5e3   ,D_q_q_3S1,10**5],
                 "btobEta_b3S"   : [200551  ,"btob31S0SplittingSudakov",5,"bbbar","3S",0.19,1.5,4.9,2.2496,5e3   ,D_q_q_1S0,10**5],
                 "btobUpsilon3S" : [200553  ,"btob33S1SplittingSudakov",5,"bbbar","3S",0.19,1.5,4.9,2.2496,5e3   ,D_q_q_3S1,10**5],
                 "btobUpsilon4S" : [300553  ,"btob43S1SplittingSudakov",5,"bbbar","4S",0.19,1.5,4.9,1.9645,5e3   ,D_q_q_3S1,10**5],
    
                 "gtogEta_b"     : [551     ,"gtogbb11S0SplittingSudakov",21,"bbbar","1S",0.19,1.5,4.9,1.8**3,5e3   ,D_g_g_1S0,10**5],
                 "gtogUpsilon"   : [553     ,"gtogbb13S1SplittingSudakov",21,"bbbar","1S",0.19,1.5,4.9,1.8**3,5e5   ,D_g_g_3S1,10**7],
                 "gtogEta_b2S"   : [100551  ,"gtogbb21S0SplittingSudakov",21,"bbbar","2S",0.19,1.5,4.9,2.8974,5e3   ,D_g_g_1S0,10**5],
                 "gtogUpsilon2S" : [100553  ,"gtogbb23S1SplittingSudakov",21,"bbbar","2S",0.19,1.5,4.9,2.8974,5e5   ,D_g_g_3S1,10**7],
                 "gtogEta_b3S"   : [200551  ,"gtogbb31S0SplittingSudakov",21,"bbbar","3S",0.19,1.5,4.9,2.2496,5e3   ,D_g_g_1S0,10**5],
                 "gtogUpsilon3S" : [200553  ,"gtogbb33S1SplittingSudakov",21,"bbbar","3S",0.19,1.5,4.9,2.2496,5e5   ,D_g_g_3S1,10**7],
                 "gtogUpsilon4S" : [300553  ,"gtogbb43S1SplittingSudakov",21,"bbbar","4S",0.19,1.5,4.9,1.9645,5e5   ,D_g_g_3S1,10**7],
                 
                 "btobH_b"       : [10553   ,"btob11P1SplittingSudakov",5,"bbbar","1P",0.19,1.5,4.9,1.6057,10000.,D_q_q_1P1,10**6],
                 "btobChi_b0"    : [10551   ,"btob13P0SplittingSudakov",5,"bbbar","1P",0.19,1.5,4.9,1.6057,10000.,D_q_q_3P0,10**6],
                 "btobChi_b1"    : [20553   ,"btob13P1SplittingSudakov",5,"bbbar","1P",0.19,1.5,4.9,1.6057,10000.,D_q_q_3P1,10**6],
                 "btobChi_b2"    : [  555   ,"btob13P2SplittingSudakov",5,"bbbar","1P",0.19,1.5,4.9,1.6057,10000.,D_q_q_3P2,10**6],

                 "btobH_b2P"     : [110553  ,"btob21P1SplittingSudakov",5,"bbbar","2P",0.19,1.5,4.9,1.8240,5e4   ,D_q_q_1P1,10**6],
                 "btobChi_b02P"  : [110551  ,"btob23P0SplittingSudakov",5,"bbbar","2P",0.19,1.5,4.9,1.8240,5e4   ,D_q_q_3P0,10**6],
                 "btobChi_b12P"  : [120553  ,"btob23P1SplittingSudakov",5,"bbbar","2P",0.19,1.5,4.9,1.8240,5e4   ,D_q_q_3P1,10**6],
                 "btobChi_b22P"  : [100555  ,"btob23P2SplittingSudakov",5,"bbbar","2P",0.19,1.5,4.9,1.8240,5e4   ,D_q_q_3P2,10**6],
                 
                 "btobChi_b03P"  : [210551  ,"btob33P0SplittingSudakov",5,"bbbar","3P",0.19,1.5,4.9,1.9804,5e4   ,D_q_q_3P0,10**6],
                 "btobChi_b13P"  : [220553  ,"btob33P1SplittingSudakov",5,"bbbar","3P",0.19,1.5,4.9,1.9804,5e4   ,D_q_q_3P1,10**6],
                 "btobChi_b23P"  : [200555  ,"btob33P2SplittingSudakov",5,"bbbar","3P",0.19,1.5,4.9,1.9804,5e4   ,D_q_q_3P2,10**6],
                 
                 "btobEta_b2"    : [10555  ,"btob11D2SplittingSudakov",5,"bbbar","1D",0.26,1.5,4.9,0.8394,5.e5   ,D_q_q_1D2,10**7],
                 "btobUpsilon_1" : [30553  ,"btob13D1SplittingSudakov",5,"bbbar","1D",0.26,1.5,4.9,0.8394,1.e6   ,D_q_q_3D1,10**7],
                 "btobUpsilon_2" : [20555  ,"btob13D2SplittingSudakov",5,"bbbar","1D",0.26,1.5,4.9,0.8394,1.e6   ,D_q_q_3D2,10**7],
                 "btobUpsilon_3" : [  557  ,"btob13D3SplittingSudakov",5,"bbbar","1D",0.26,1.5,4.9,0.8394,1.e6   ,D_q_q_3D3,10**7],
                 
                 "btocB_c"       : [541     ,"btoc11S0SplittingSudakov",5,"bcbar","1S",0.26,1.5,4.9,1.9943,100.,D_q_qp_1S0,10**3],
                 "btocB_cStar"   : [543     ,"btoc13S1SplittingSudakov",5,"bcbar","1S",0.26,1.5,4.9,1.9943,100.,D_q_qp_3S1,10**3],
                 "btocB_c2S"     : [100541  ,"btoc21S0SplittingSudakov",5,"bcbar","2S",0.26,1.5,4.9,2.8974,100.,D_q_qp_1S0,10**3],
                 "btocB_cStar2S" : [100543  ,"btoc23S1SplittingSudakov",5,"bcbar","2S",0.26,1.5,4.9,2.8974,100.,D_q_qp_3S1,10**3],
                 
                 "btocB_c0"      : [10541   ,"btoc13P0SplittingSudakov",5,"bcbar","1P",0.26,1.5,4.9,0.3083,500.,D_q_qp_3P0,10**4],
                 "btocB_c2"      : [545     ,"btoc13P2SplittingSudakov",5,"bcbar","1P",0.26,1.5,4.9,0.3083,500.,D_q_qp_3P2,10**4],
                 "btocB_c1P1"    : [10543   ,"btoc1P1SplittingSudakov" ,5,"bcbar","1P",0.26,1.5,4.9,0.3083,500.,D_q_qp_1P1,10**4,90.],
                 "btocB_c3P1"    : [20543   ,"btoc1P1SplittingSudakov" ,5,"bcbar","1P",0.26,1.5,4.9,0.3083,500.,D_q_qp_3P1,10**4,90.],
                 "btocB_c1P1mix" : [10543   ,"btoc1P1SplittingSudakov" ,5,"bcbar","1P",0.26,1.5,4.9,0.3083,500.,D_q_qp_P1 ,10**4,25.],
                 "btocB_c3P1mix" : [20543   ,"btoc1P1SplittingSudakov" ,5,"bcbar","1P",0.26,1.5,4.9,0.3083,500.,D_q_qp_P1 ,10**4,25.],

                 "btocB_cStar1D" : [30543   ,"btoc13D1SplittingSudakov",5,"bcbar","1D",0.26,1.5,4.9,0.0986,5000.,D_q_qp_3D1,10**5],
                 "btocB_c3"      : [547     ,"btoc13D3SplittingSudakov",5,"bcbar","1D",0.26,1.5,4.9,0.0986,1000.,D_q_qp_3D3,10**5],
                 "btocB_c1D2"    : [10545   ,"btoc1D2SplittingSudakov" ,5,"bcbar","1D",0.26,1.5,4.9,0.0986,5000.,D_q_qp_1D2,10**5,90.],
                 "btocB_c3D2"    : [20545   ,"btoc1D2SplittingSudakov" ,5,"bcbar","1D",0.26,1.5,4.9,0.0986,5000.,D_q_qp_3D2,10**5,90.],
                 "btocB_c1D2mix" : [10545   ,"btoc1D2SplittingSudakov" ,5,"bcbar","1D",0.26,1.5,4.9,0.0986,5000.,D_q_qp_D2 ,10**5,34.4],
                 "btocB_c3D2mix" : [20545   ,"btoc1D2SplittingSudakov" ,5,"bcbar","1D",0.26,1.5,4.9,0.0986,5000.,D_q_qp_D2 ,10**5,34.4],

                 "ctocbarcc1"    : [4403    ,"QtoQcc1SplittingSudakov" ,4,"cc"   ,"1S",0.26,1.5,4.9,0.07 ,1e3,D_cc1,1e5],
                 "btobbarbb1"    : [5503    ,"QtoQbb1SplittingSudakov" ,5,"bb"   ,"1S",0.26,1.5,4.9,0.633,1e3,D_cc1,1e5],
                 "btocbarbc0"    : [5401    ,"QtoQbc0SplittingSudakov" ,5,"bc"   ,"1S",0.26,1.5,4.9,0.25 ,5e2,D_bc0,1e5],
                 "btocbarbc1"    : [5403    ,"QtoQbc1SplittingSudakov" ,5,"bc"   ,"1S",0.26,1.5,4.9,0.25 ,5e2,D_bc1,1e5],
}
# options
op = optparse.OptionParser(usage=__doc__)
op.add_option("--generate-input-files", dest="infiles", default=False, action="store_true")
op.add_option("--analyse", dest="analyse", default=False, action="store_true")
op.add_option("--fast", dest="fast", default=False, action="store_true")
opts, args = op.parse_args()
# get template and write the file
with open(os.path.join("Rivet/Templates/EE.in"), 'r') as f:
    templateText = f.read()
template = Template( templateText )
# if we are generating the inputfiles
if opts.infiles :
    targets=""
    # first find all the splittings
    opts, args = op.parse_args()
    splittings=[]
    for fname in ["../src/defaults/Shower.in",
                  "../src/snippets/OniumShower.in"] :
        infile=open(fname)
        line=infile.readline()
        while line :
            if "SplittingGenerator:AddFinalSplitting" in line:
                splittings.append(line.replace("Add","Delete"))
            line=infile.readline()
        infile.close()
    # now loop over the examples
    for (key,val) in testParameters.items() :
        # mass of the state
        if val[3]=="ccbar" or val[3]=="cc" :
            mO=2.*val[6]
        elif val[3]=="bbbar" or val[3]=="bb" :
            mO=2.*val[7]
        else :
            mO=val[6]+val[7]
        # process
        if val[2] < 6 :
            proc = """
insert /Herwig/MatrixElements/SubProcess:MatrixElements 0 /Herwig/MatrixElements/MEee2gZ2qq
set /Herwig/MatrixElements/MEee2gZ2qq:MinimumFlavour %s
set /Herwig/MatrixElements/MEee2gZ2qq:MaximumFlavour %s
""" % ( val[2],val[2])
        elif val[2]==21 : 
            proc ="""
create Herwig::MEee2Higgs2SM /Herwig/MatrixElements/MEee2Higgs2SM
insert /Herwig/MatrixElements/SubProcess:MatrixElements 0 /Herwig/MatrixElements/MEee2Higgs2SM
set /Herwig/MatrixElements/MEee2Higgs2SM:Allowed Gluon
"""
        # substs for the input file
        parameters={"parameterFile" : """
set /Herwig/Generators/EventGenerator:EventHandler:LuminosityFunction:Energy 10000.
set /Herwig/Generators/EventGenerator:EventHandler:HadronizationHandler NULL
set /Herwig/Generators/EventGenerator:EventHandler:DecayHandler NULL
set /Herwig/Analysis/Basics:CheckQuark No
set /Herwig/Particles/d:ConstituentMass 1e-10
set /Herwig/Particles/u:ConstituentMass 1e-10
set /Herwig/Particles/g:ConstituentMass 1e-9
insert /Herwig/Analysis/RivetAnalysis:Analyses 0 MC_Simple_Onium""",
                "process" : """
%s
set /Herwig/Particles/b:ConstituentMass %s
set /Herwig/Particles/c:ConstituentMass %s
set /Herwig/Particles/b:NominalMass %s
set /Herwig/Particles/c:NominalMass %s
set /Herwig/Particles/%s:NominalMass %s\n""" %(proc,val[7],val[6],val[7],val[6],herwigName[val[0]],mO),
                "shower" : """
read snippets/OniumShower.in
set /Herwig/Shower/ShowerHandler:HardEmission 0
do /Herwig/OniumParameters:SetWaveFunction %s %s %s
set /Herwig/Shower/%s:FixedAlphaS %s
set /Herwig/Shower/%s:EnhancementFactor %s
cd /Herwig/Shower
"""%(val[3],val[4],val[8],val[1],val[5],val[1],val[9])}
        # mixing if needed
        if len(val) == 13 :
            parameters["shower"] += "do /Herwig/OniumParameters:SetSingletTripletMixing %s %s\n" % (val[4],val[12])
        hName=herwigName[val[0]]
        if val[3] == "bcbar" and val[2]==5 : hName=hName.replace("+","-")
        # delete other splittings
        for sp in splittings :
            if not (val[1] in sp and hName in sp):
                parameters["shower"] += sp
        # write the input file
        parameters["runname"]="Onium-%s"%key
        with open(os.path.join("Rivet","Onium-%s.in"%key), 'w') as f:
            f.write( template.substitute(parameters) )
        targets += "Onium-%s.yoda " % key
    print(targets)
# if we are doing the analysis
if opts.analyse :
    if not os.path.isdir("Onium-Splitting"):
        os.mkdir("Onium-Splitting")
    plots=""
    # loop over the tests
    for (key,val) in testParameters.items() :
        # mass of the quarks
        if val[3]=="ccbar" or val[3]=="cc":
            m1=val[6]
            m2=val[6]
        elif val[3]=="bbbar"  or val[3]=="bb":
            m1=val[7]
            m2=val[7]
        elif val[3]=="bcbar"  or val[3]=="bc":
            m1=val[6]
            m2=val[7]
        M  = m1+m2
        a1 = m1/M
        a2 = 1-a1
        # other parameters
        aS  = val[5]
        R02 = val[8]
        # mixing if needed
        if len(val) == 13 :
            mix1 = math.sin(val[12]/180.*math.pi)
            mix2 = math.cos(val[12]/180.*math.pi)
            itest = int((val[0]%100000)/10000);
            if itest==2 :
                (mix1,mix2) = (mix2,-mix1)
        else :
            mix1=0
            mix2=0
        if(val[2]==21) :
            q1="g"
            q2="g"
        else :
            if val[2] ==4   : q1 = "c"
            elif val[2] ==5 : q1 = "b"
            if val[3] != "bcbar" and val[3] !="bc" : q2 = q1
            elif q1=="c"                           : q2 = "b"
            else                                   : q2 = "c"
        lName=latexName[val[0]]
        if q1=="b" and q2=="c" : lName=lName.replace("+","-")
        if len(val[3])==2 :
           title="Comparsion of fragmentation function for $%s\\to \\bar{%s} %s$" % (q1,q2,lName)
        else :
           title="Comparsion of fragmentation function for $%s\\to %s %s$" % (q1,q2,lName)
        if len(val) == 13 :
            title+=" ($\\theta=%.1f^0$)" % val[12]
        plt.title(title)
        aos   = yoda.read("Onium-%s.yoda" % key)
        histo = aos["/MC_Simple_Onium/h_%s" % val[0]]
        x  = []
        dx = []
        y1 = []
        yan = []
        dy1= []
        chisq = 0.
        ndof  = 0
        for bin in histo.bins() :
            x  .append(bin.xMid()      )
            dx .append(0.5*bin.xWidth())
            y1 .append(bin.height()   *val[11])
            dy1.append(bin.heightErr()*val[11])
            if(opts.fast) :
                fval = val[11]*val[10](bin.xMid())
            else :
                fval = val[11]*quad(val[10],bin.xMin(),bin.xMax())[0]/bin.xWidth()
            yan.append(fval)
            if(dy1[-1]>0. and x[-1]>0.01 and x[-1]<0.99) :
                chisq += ((fval-y1[-1])/dy1[-1])**2
                ndof+=1.
        if(ndof!=0) : chisq/=ndof
        if(not opts.fast) :
            (xan,yan) = fragmentation(val[10],val[11],step)
            step=0.001
        else :
            xan=x
        plt.plot(xan,yan,label="analytic ",color="black")
        plt.errorbar(x,y1,yerr=dy1,xerr=dx,linestyle="none",fmt="none",
                     label="Hw Fixed $\\alpha_S$",color="red")
        plt.xlabel("$z_{%s}$" % lName)
        plt.ylabel("$D(z_{%s})\\times10^{%s}$" % (lName,int(math.log10(val[11]))))
        if val[10]==D_g_g_3S1 :
            loc = 1
        else :
            loc = 2        
        plt.legend(loc=loc,title="$\\chi^2/N=%.2f$"%chisq)
        plt.xlim([0.,1.])
        plt.savefig("Onium-Splitting/%s.pdf" %key)
        plt.savefig("Onium-Splitting/%s.png" %key)
        plt.clf()
        plots+=plotTemplate.substitute({"id" : key})
    with open(os.path.join("Onium-Splitting","index.html"), 'w') as f:
            f.write( htmlTemplate.substitute( {"plots" : plots,
                                               "time"  :'<p>Generated at %s</p>' % datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")  }) )

# setup chi_c2(2P) 100445 chi_c2(2P) 3.929 0.029 0.24 0 0 0 5 0 
