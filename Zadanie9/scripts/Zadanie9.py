#poetry run bokeh serve --show .\scripts\Zadanie9.py

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from matplotlib.animation import FuncAnimation
from IPython.display import HTML

from bokeh.io import output_notebook, curdoc
from bokeh.plotting import figure, show
from bokeh.layouts import row, column, gridplot, layout
from bokeh.models import Slider, Div, ColumnDataSource
from bokeh.palettes import all_palettes




def SIR_func(y, t, beta, gamma):
    dS = -beta * y[0] * y[1]
    dR = gamma * y[1]
    dI = -dS - dR
    return (dS, dI, dR)





t0 = 0
tmax = 1000
tbins = 200
t = np.linspace(t0, tmax, tbins)
beta = 0.0002
gamma = 0.04
N0 = 1000
S0 = 997
I0 = N0 - S0
R0 = 0

y = odeint(SIR_func, (S0, I0, R0), t, args=(beta, gamma))

S = []
I = []
R = []

for sir in y:
    S.append(sir[0])
    I.append(sir[1])
    R.append(sir[2])




t_range = 300
N_max = 10000


fig = figure(
    width=1600,
    aspect_ratio=3,
    x_axis_label='$$t$$',
    y_axis_label='$$N$$',
)


data1 = ColumnDataSource(data={'x':t, 'y':S})
data2 = ColumnDataSource(data={'x':t, 'y':I})
data3 = ColumnDataSource(data={'x':t, 'y':R})

plot1 = fig.line(x='x', y='y', source=data1, color='blue', legend_label='Susceptable', line_width=3)
plot2 = fig.line(x='x', y='y', source=data2, color='red', legend_label='Infectious', line_width=3)
plot3 = fig.line(x='x', y='y', source=data3, color='green', legend_label='Recovered', line_width=3)

s1 = Slider(start=0, end=0.001, value=beta, step=0.00001, title='beta', width=200, format='0[.]00000')
s2 = Slider(start=0, end=0.1, value=gamma, step=0.0001, title='gamma', width=200, format='0[.]0000')
s4 = Slider(start=0, end=N0, value=S0, step=1, title='S0', width=200)
s5 = Slider(start=0, end=N0, value=I0, step=1, title='I0', width=200)
s6 = Slider(start=0, end=tmax, value=tmax, step=1, title='t', width=200)

def update(attr, old, new):
    beta = s1.value
    gamma = s2.value
    S0 = s4.value
    I0 = s5.value
    tmax = s6.value

    t = np.linspace(t0, tmax, tbins)
    y = odeint(SIR_func, (S0, I0, R0), t, args=(beta, gamma))

    S.clear()
    I.clear()
    R.clear()

    for sir in y:
        S.append(sir[0])
        I.append(sir[1])
        R.append(sir[2])
    
    plot1.data_source.data = {'x':t, 'y':S}
    plot2.data_source.data = {'x':t, 'y':I}
    plot3.data_source.data = {'x':t, 'y':R}

def update_s4(attr, old, new):
    S0 = s4.value
    I0 = N0 - S0
    s5.update(value=I0)

    update(attr, old, new)

def update_s5(attr, old, new):
    I0 = s5.value
    S0 = N0 - I0
    s4.update(value=S0)

    update(attr, old, new)
    

s1.on_change('value_throttled', update)
s2.on_change('value_throttled', update)
s4.on_change('value_throttled', update_s4)
s5.on_change('value_throttled', update_s5)
s6.on_change('value', update)


curdoc().add_root(column(Div(text='<h1>Modle SIR</h1>'), row(column(s1, s2, s4, s5, s6, width=200), fig)))