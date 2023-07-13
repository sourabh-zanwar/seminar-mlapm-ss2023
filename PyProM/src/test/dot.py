import networkx as nx
from networkx.drawing.nx_agraph import write_dot, graphviz_layout, pygraphviz_layout
G = nx.DiGraph()

G.add_node("ROOT")

for i in range(5):
    G.add_node("Child_%i" % i)
    G.add_node("Grandchild_%i" % i)
    G.add_node("Greatgrandchild_%i" % i)

    G.add_edge("ROOT", "Child_%i" % i)
    G.add_edge("Child_%i" % i, "Grandchild_%i" % i)
    G.add_edge("Grandchild_%i" % i, "Greatgrandchild_%i" % i)

# same layout using matplotlib with no labels
layout =pygraphviz_layout(G, prog='dot')

from bokeh.models import ColumnDataSource

nodes, nodes_coordinates = zip(*sorted(layout.items()))
nodes_ys, nodes_xs = list(zip(*nodes_coordinates))
nodes_source = ColumnDataSource(dict(x=nodes_xs, y=nodes_ys, name=nodes))

from bokeh.plotting import show, figure
from bokeh.models import HoverTool

hover = HoverTool(tooltips=[('name', '@name'), ('id', '$index')])
plot = figure(sizing_mode='stretch_both',
              tools=['tap', hover, 'box_zoom', 'reset'])
r_circles = plot.circle('x', 'y', source=nodes_source, size=40, color='blue', level = 'overlay')
def get_edges_specs(_network, _layout):
    d = dict(xs=[], ys=[])
    #weights = [d['weight'] for u, v, d in _network.edges(data=True)]
    #max_weight = max(weights)
    #calc_alpha = lambda h: 0.1 + 0.6 * (h / max_weight)

    # example: { ..., ('user47', 'da_bjoerni', {'weight': 3}), ... }
    for u, v, data in _network.edges(data=True):
        d['ys'].append([_layout[u][0], _layout[v][0]])
        d['xs'].append([_layout[u][1], _layout[v][1]])
        #d['alphas'].append(calc_alpha(data['weight']))
    return d

edges = get_edges_specs(G, layout)
lines_source = ColumnDataSource(edges)

r_lines = plot.multi_line('xs', 'ys', line_width=1.5, color='navy', source=lines_source)

show(plot)
