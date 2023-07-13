#import graphviz
import pydot
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import sys
import os
#sys.path.append(os.path.abspath("../utility"))
from PyProM.src.utility.util_profile import Util_Profile
#import networkx as nx

timefn = Util_Profile.timefn

class FSM_Miner(object):
    """docstring for FSM"""
    def __init__(self,*args, **kwargs):
        super(FSM_Miner, self).__init__(*args, **kwargs)

    machine_attributes = {
        'directed': True,
        'strict': False,
        'compound': True,
        'rankdir': 'LR',
        'ratio': '0.3',
        'ranksep': '7 equally'
    }

    style_attributes = {
        'node': {
            'default': {
                'shape': 'circle',
                'height': '4',
                'width' : '4',
                'style': 'filled',
                'fillcolor': 'white',
                'penwidth': 10,
                'fontsize': 60
                #'color': 'black',
            },
            'DUMMY': {
                'color': 'gray',
                'fillcolor': 'gray'
            },
            'HIGH': {
                'fillcolor': 'lightblue',
                #'fillcolor': 'darksalmon',
                #'shape': 'doublecircle'
            },
            'LOW': {
                'fillcolor': 'lightpink'
                #'color': 'blue',
                #'fillcolor': 'azure2',
            },
            'BOB': {
                'color': 'navy'
            },
            'WOW': {
                'color': 'red4'
            }
        },
        'edge': {
            'default': {
                'color': 'gray',
                'penwidth': '15'
            },
            'BOB': {
                'color': 'navy'
            },
            'WOW': {
                'color': 'red4'
            },
            'DUMMY': {
                'color': 'gray',
                'fillcolor': 'gray'
            }
        }
    }
    @timefn
    def _create_graph(self, transition_matrix, **kwargs):
        """
        import pygraphviz as pgv
        if not pgv:  # pragma: no cover
            raise Exception('AGraph diagram requires pygraphviz')
        #fsm_graph = pgv.AGraph(**self.machine_attributes)
        """
        fsm_graph = nx.DiGraph(**self.machine_attributes)

        if 'edge_colors' in kwargs:
            edge_colors = kwargs['edge_colors']

        if 'edge_threshold' in kwargs:
            edge_threshold = kwargs['edge_threshold']
        else:
            edge_threshold = 0

        if 'penwidth' in kwargs:
            penwidth = kwargs['penwidth']
        else:
            penwidth = 15

        if 'label' in kwargs:
            label = kwargs['label']
        else:
            label = 'count'

        if 'colormap' in kwargs:
            colormap = kwargs['colormap']
        else:
            colormap = None

        if 'dashed' in kwargs:
            dashed = kwargs['dashed']
        else:
            dashed = False


        if 'analysis_result' in kwargs:
            analysis_result = kwargs['analysis_result']
            BG = kwargs['BG']
            WG = kwargs['WG']
            print("add annotated node")
            self._add_high_low_nodes(fsm_graph,transition_matrix,
            analysis_result, BG, WG)
            print("add annotated edge")
            self._add_high_low_edges(fsm_graph, transition_matrix, BG, WG)

        elif 'chamber_info_dict' in kwargs:
            chamber_info_dict = kwargs['chamber_info_dict']
            self._add_valid_nodes(fsm_graph, transition_matrix, chamber_info_dict)
            if 'edge_threshold' in kwargs:
                edge_threshold = kwargs['edge_threshold']
            else:
                edge_threshold = False

            if edge_threshold!=False:
                self._add_valid_edges(fsm_graph, transition_matrix, chamber_info_dict, edge_threshold=edge_threshold, edge_colors=edge_colors)
            else:
                self._add_valid_edges(fsm_graph, transition_matrix, chamber_info_dict, edge_colors=edge_colors)

        else:
            print("add node")
            self._add_nodes(fsm_graph,transition_matrix)
            print("add edge")
            self._add_edges(fsm_graph, transition_matrix, label=label, edge_threshold=edge_threshold, penwidth=penwidth, colormap=colormap, dashed=dashed)





        print("unconnect")
        #remove unconnected nodes
        total_nodes = fsm_graph.nodes()
        """
        outdeg = fsm_graph.out_degree()
        indeg = fsm_graph.in_degree()
        zero_deg = [n for n in range(len(outdeg)) if (outdeg[n] == 0 or indeg[n] == 0)]
        """
        #zero_deg = ['']

        outdeg = fsm_graph.out_degree()
        indeg = fsm_graph.in_degree()
        #zero_deg = [n for n in range(len(outdeg)) if (outdeg[n] == 0 or indeg[n] == 0)]
        zero_outdeg = [node for node, deg in outdeg if deg==0]
        zero_indeg = [node for node, deg in indeg if deg==0]
        zero_deg = zero_outdeg + zero_indeg
        print("Remove nodes: {}".format(zero_deg))
        if 'start_end' not in kwargs:
            start_end = True
        else:
            start_end = kwargs['start_end']

        if len(zero_deg)!=0:
            #candidate_nodes = [total_nodes[x] for x in zero_deg]
            candidate_nodes = zero_deg
            print(candidate_nodes)
            #print("candidate nodes: {}".format(candidate_nodes))
            if start_end == False:
                fsm_graph.remove_nodes_from(candidate_nodes)
            else:
                if 'START' in candidate_nodes:
                    candidate_nodes.remove('START')
                if 'END' in candidate_nodes:
                    candidate_nodes.remove('END')
                print("candidate nodes: {}".format(candidate_nodes))
                if len(candidate_nodes) !=0:
                    fsm_graph.remove_nodes_from(candidate_nodes)


        #print("final nodes: {}".format(fsm_graph.nodes()))
        #print("final nodes: {}".format(fsm_graph.edges()))
        #setattr(fsm_graph, 'style_attributes', self.style_attributes)
        return fsm_graph

    @timefn
    def _add_nodes(self, fsm_graph, transition_matrix):
        shape = self.style_attributes['node']['default']['shape']
        style = self.style_attributes['node']['default']['style']
        fontsize = self.style_attributes['node']['default']['fontsize']
        penwidth = self.style_attributes['node']['default']['penwidth']
        for ai in transition_matrix.keys():
            if ai == 'START' or ai == 'END':
                print("ignore {}".format(ai))
                continue
            fsm_graph.add_node(ai, shape = shape, style = style, penwidth = penwidth, fontsize = fontsize)

    def _add_valid_nodes(self, fsm_graph, transition_matrix, chamber_info_dict, **kwargs):
        valids = [chamber for chamber in chamber_info_dict if chamber_info_dict[chamber]['valid']!=False]
        dummies = [chamber for chamber in chamber_info_dict if chamber_info_dict[chamber]['valid']==False]
        shape = self.style_attributes['node']['default']['shape']
        style = self.style_attributes['node']['default']['style']
        fontsize = self.style_attributes['node']['default']['fontsize']
        penwidth = self.style_attributes['node']['default']['penwidth']

        for ai in transition_matrix:
            if ai == 'START' or ai == 'END':
                print("ignore {}".format(ai))
                continue
            #simplification 하지않는 경우
            if ai in dummies:
                fillcolor = self.style_attributes['node']['DUMMY']['fillcolor']
            elif ai in valids:
                fillcolor = self.style_attributes['node']['HIGH']['fillcolor']
            else:
                pass
                #print(ai)
                #print("NO")
            #simplification 하는 경우
            if 'DM' in ai:
                fillcolor = self.style_attributes['node']['DUMMY']['fillcolor']

            #border color 설정 - BWS, BWD
            """
            if BWSs[ai] < 0.1:
                color = self.style_attributes['node']['DUMMY']['color']
            if BWDs[ai] > BOB_criterion:
                color = self.style_attributes['node']['BOB']['color']
            elif BWDs[ai] < WOW_criterion:
                color = self.style_attributes['node']['WOW']['color']
            else:
                color = self.style_attributes['node']['DUMMY']['color']
            """
            color = self.style_attributes['node']['DUMMY']['color']


            fsm_graph.add_node(ai, shape = shape, color = color, fillcolor = fillcolor, style = style, penwidth = penwidth, fontsize = fontsize)


    def _add_high_low_nodes(self, fsm_graph, transition_matrix, analysis_result, BOB_group, WOW_group):
        dummies = analysis_result.loc[analysis_result['LCresult'] == 'DUMMY', 'RESOURCE']
        highs = analysis_result.loc[analysis_result['LCresult'] == 'BOB', 'RESOURCE']
        lows = analysis_result.loc[analysis_result['LCresult'] == 'WOW', 'RESOURCE']
        shape = self.style_attributes['node']['default']['shape']
        style = self.style_attributes['node']['default']['style']
        fontsize = self.style_attributes['node']['default']['fontsize']
        penwidth = self.style_attributes['node']['default']['penwidth']

        #calculate BWDs and BWs
        BWDs = {}
        BWSs = {}
        for ai in transition_matrix:
            cases = []
            for aj in transition_matrix[ai]:
                cases+=transition_matrix[ai][aj]['case']
            best_matches = set(cases) & set(BOB_group)
            worst_matches = set(cases) & set(WOW_group)
            try:
                BWSs[ai] = (len(best_matches) + len(worst_matches))/len(cases)
                BWDs[ai] = (len(best_matches) - len(worst_matches))/len(cases)
                #BWDs.append((len(best_matches) - len(worst_matches))/len(cases))
            except ZeroDivisionError:
                continue
        BOB_criterion = np.percentile(list(BWDs.values()), 40)
        WOW_criterion = np.percentile(list(BWDs.values()), 60)


        for ai in transition_matrix:
            if ai == 'START' or ai == 'END':
                print("ignore {}".format(ai))
                continue
            #simplification 하지않는 경우
            if ai in dummies.values:
                fillcolor = self.style_attributes['node']['DUMMY']['fillcolor']
            elif ai in highs.values:
                fillcolor = self.style_attributes['node']['HIGH']['fillcolor']
            elif ai in lows.values:
                fillcolor = self.style_attributes['node']['LOW']['fillcolor']
            else:
                print(ai)
                print("NO")
            #simplification 하는 경우
            if 'dummy' in ai:
                fillcolor = self.style_attributes['node']['DUMMY']['fillcolor']

            if BWSs[ai] < 0.1:
                color = self.style_attributes['node']['DUMMY']['color']
            if BWDs[ai] > BOB_criterion:
                color = self.style_attributes['node']['BOB']['color']
            elif BWDs[ai] < WOW_criterion:
                color = self.style_attributes['node']['WOW']['color']
            else:
                color = self.style_attributes['node']['DUMMY']['color']


            fsm_graph.add_node(ai, shape = shape, color = color, fillcolor = fillcolor, style = style, penwidth = penwidth, fontsize = fontsize)


    @timefn
    def _add_edges(self, fsm_graph, transition_matrix, label='count', edge_threshold=0, penwidth=15, colormap=None, dashed=False):
        #penwidth = self.style_attributes['node']['default']['penwidth']
        #arc thickness
        values = [transition_matrix[ai][aj][label] for ai in transition_matrix for aj in transition_matrix[ai]]
        x_min = min(values)
        x_max = max(values)

        y_min = 5.0
        y_max = 20.0

        def convert_to_hex(rgba_color):
            red = int(rgba_color[0]*255)
            green = int(rgba_color[1]*255)
            blue = int(rgba_color[2]*255)
            return '#%02x%02x%02x' % (red, green, blue)

        if colormap != None:
            cmap = plt.get_cmap(colormap)

            thick_x_min = int(x_min)
            thick_x_max = int(x_max)

            thick_y_min = 160.0
            thick_y_max = 230.0

        for ai in transition_matrix:
            for aj in transition_matrix[ai]:
                if ai == aj:
                    continue
                if ai == 'START' or ai == 'END':
                    fsm_graph.add_edge(ai, aj, label=transition_matrix[ai][aj][label], penwidth = 15)
                    continue
                x = transition_matrix[ai][aj][label]
                x = float(x)
                y = y_min + (y_max-y_min) * float(x-x_min) / float(x_max-x_min)
                if colormap !=None:
                    thick_y = thick_y_min + (thick_y_max-thick_y_min) * float(x-x_min) / float(x_max-x_min)
                    rgba = cmap(int(thick_y))
                    color = convert_to_hex(rgba)

                else:
                    color = 'gray'

                if transition_matrix[ai][aj]['count'] > edge_threshold:
                    if dashed!=False:
                        style = 'dashed' if transition_matrix[ai][aj][label]==0 else 'solid'
                    else:
                        style = 'solid'
                    fsm_graph.add_edge(ai, aj, label=transition_matrix[ai][aj][label], penwidth = y, color=color, style=style)

    @timefn
    def _add_valid_edges(self, fsm_graph, transition_matrix, chamber_info_dict, edge_colors, **kwargs):
        if 'edge_threshold' in kwargs:
            edge_threshold = kwargs['edge_threshold']
        else:
            edge_threshold = False
        penwidth = self.style_attributes['node']['default']['penwidth']
        values = [transition_matrix[ai][aj]['count'] for ai in transition_matrix for aj in transition_matrix[ai]]

        x_min = min(values)
        x_max = max(values)
        y_min = 1.0
        y_max = 25.0

        print(edge_colors)
        num_colors = len(edge_colors)
        for ai in transition_matrix:
            for aj in transition_matrix[ai]:
                edge_label = transition_matrix[ai][aj]['count']
                edge_label = '                    {}                    '.format(edge_label)
                if ai == 'START' or ai == 'END':
                    #print("ignore {}".format(ai))
                    color = self.style_attributes['edge']['default']['color']
                    fsm_graph.add_edge(ai, aj, label=edge_label, color = color, penwidth = 15)
                    continue
                if transition_matrix[ai][aj]['count'] < 1:
                    continue
                x = transition_matrix[ai][aj]['count']
                x = float(x)
                y = y_min + (y_max-y_min) * float(x-x_min) / float(x_max-x_min)

                thickness = 10
                if 'DM' not in ai:
                    color_index, thickness = self.assign_edge_color(transition_matrix, chamber_info_dict, ai, aj)
                    color = edge_colors[color_index]
                elif 'DM' in ai and 'DM' not in aj and 'END' not in aj:
                    color_index, thickness = self.assign_edge_color(transition_matrix, chamber_info_dict, ai, aj, reverse=True)
                    color = edge_colors[color_index]
                else:
                    color = self.style_attributes['edge']['DUMMY']['color']

                """
                if edge_threshold!=False:
                    #더미간의 연결은 유지 (step 소실하지 않기 위해서)
                    if 'DM' in ai and 'DM' in aj:
                        fsm_graph.add_edge(ai, aj, label=transition_matrix[ai][aj]['count'], color = color, penwidth = thickness)
                    else:
                        if transition_matrix[ai][aj]['count'] > edge_threshold:
                            fsm_graph.add_edge(ai, aj, label=transition_matrix[ai][aj]['count'], color = color, penwidth = thickness)
                else:
                """
                fsm_graph.add_edge(ai, aj, label=edge_label, color = color, penwidth = thickness)


    def assign_edge_color(self, transition_matrix, chamber_info_dict, ai, aj, **kwargs):
        if 'reverse' in kwargs:
            reverse = kwargs['reverse']
        else:
            reverse = False
        if reverse == False:
            valid_list = chamber_info_dict[ai]['valid']
        else:
            valid_list = chamber_info_dict[aj]['valid']


        assigned_cluster = ''
        keys = list(transition_matrix[ai][aj]['Cluster'].keys())
        while assigned_cluster=='':
            if len(keys) == 0:
                color_index = -1
                thickness = 10
                return color_index, thickness
            cand_cluster = max(keys, key=(lambda key: transition_matrix[ai][aj]['Cluster'][key]))
            if cand_cluster in valid_list:
                assigned_cluster = cand_cluster
            else:
                keys.remove(cand_cluster)
        thickness = 35
        return int(assigned_cluster), thickness




    @timefn
    def _add_high_low_edges(self, fsm_graph, transition_matrix, BOB_group, WOW_group):
        penwidth = self.style_attributes['node']['default']['penwidth']
        #arc thickness
        values = [transition_matrix[ai][aj]['count'] for ai in transition_matrix for aj in transition_matrix[ai]]
        x_min = min(values)
        x_max = max(values)

        y_min = 1.0
        y_max = 5.0

        BWSs = dict()
        BWDs = dict()
        BWD_values = []
        for ai in transition_matrix:
            if ai == 'START' or ai == 'END':
                #print("ignore {}".format(ai))
                continue
            BWSs[ai] = dict()
            BWDs[ai] = dict()
            for aj in transition_matrix[ai]:
                cases = transition_matrix[ai][aj]['case']
                best_matches = set(cases) & set(BOB_group)
                worst_matches = set(cases) & set(WOW_group)
                try:
                    BWSs[ai][aj] = (len(best_matches) + len(worst_matches))/len(cases)
                    BWDs[ai][aj] = (len(best_matches) - len(worst_matches))/len(cases)
                    BWD_values.append((len(best_matches) - len(worst_matches))/len(cases))
                    #BWDs.append((len(best_matches) - len(worst_matches))/len(cases))
                except ZeroDivisionError:
                    print("zero division: {}".format(transition_matrix[ai][aj]))

        BOB_criterion = np.percentile(BWD_values, 60)
        print("edge BOB criterion: {}".format(BOB_criterion))
        WOW_criterion = np.percentile(BWD_values, 40)
        print("edge WOW criterion: {}".format(WOW_criterion))
        BOB_count = 0
        WOW_count = 0
        DUMMY_count = 0

        for ai in transition_matrix:
            for aj in transition_matrix[ai]:
                if ai == 'START' or ai == 'END':
                    #print("ignore {}".format(ai))
                    color = self.style_attributes['edge']['default']['color']
                    fsm_graph.add_edge(ai, aj, label=transition_matrix[ai][aj]['count'], color = color, penwidth = 15)
                    continue
                if transition_matrix[ai][aj]['count'] < 1:
                    continue
                x = transition_matrix[ai][aj]['count']
                x = float(x)
                y = y_min + (y_max-y_min) * float(x-x_min) / float(x_max-x_min)

                if BWSs[ai][aj] < 0.1:
                    color = self.style_attributes['edge']['DUMMY']['color']
                if BWDs[ai][aj] > BOB_criterion:
                    color = self.style_attributes['edge']['BOB']['color']
                    if ai.split("/")[0] == 'STEP_001':
                        BOB_count += 1
                elif BWDs[ai][aj] < WOW_criterion:
                    color = self.style_attributes['edge']['WOW']['color']
                    if ai.split("/")[0] == 'STEP_001':
                        WOW_count += 1
                else:
                    color = self.style_attributes['edge']['DUMMY']['color']
                    if ai.split("/")[0] == 'STEP_001':
                        DUMMY_count += 1

                fsm_graph.add_edge(ai, aj, label=transition_matrix[ai][aj]['count'], color = color, penwidth = 15)

    def get_fsm(self):
        return self.fsm_graph

    def _create_dot(self,fsm_graph, svg_filename):
        #fsm_graph_dot = fsm_graph.draw('../result/state_svg.svg', format ='svg', prog='dot')
        #import matplotlib.pyplot as plt
        #pos = nx.nx_pydot.graphviz_layout(fsm_graph, prog='dot')
        #nx.draw(fsm_graph, pos=pos)
        #plt.savefig('../result/state_svg.svg', format ='svg')
        #nx.drawing.nx_agraph.write_dot(fsm_graph, '../result/state.dot')
        nx.nx_pydot.write_dot(fsm_graph, '../result/state.dot')
        #os.system('dot -Tsvg state.dot -o state_svg.svg')
        #graphviz.render('dot', 'svg', '../result/state.dot')
        dot_graph = pydot.graph_from_dot_file('../result/state.dot')[0]
        dot_graph.set_rankdir('LR')
        #dot_graph.set_labelfontsize(10)
        dot_graph.write_png('../result/{}.png'.format(svg_filename))
        #dot.render('test-output/round-table.gv', view=True)

    def get_dot(self,fsm_graph, svg_filename='transition_system'):
        self._create_dot(fsm_graph, svg_filename=svg_filename)
        #fsm_graph_dot = self._create_dot(fsm_graph)
        #return fsm_graph_dot

    @timefn
    def get_graph_info(self,fsm_graph):
        total_nodes = fsm_graph.nodes()
        total_edges = fsm_graph.edges()
        print("# nodes: {}".format(len(total_nodes)))
        print("# arcs: {}".format(len(total_edges)))

        step_node_count = dict()
        step_arc_count = dict()


        for node in total_nodes:
            if node != 'START' and node != 'END':
                step = node.split("/")[0]
                if step not in step_node_count:
                    step_node_count[step] = 0
                step_node_count[step] += 1


        for arc in total_edges:
            if arc[0] != 'START' and arc[0] != 'END':
                step = arc[0].split("/")[0].strip()
                if step not in step_arc_count:
                    step_arc_count[step] = 0
                step_arc_count[step] += 1