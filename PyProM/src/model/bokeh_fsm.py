import networkx as nx
import pygraphviz as pgv
import numpy as np

import sys
import os
#sys.path.append(os.path.abspath("../utility"))
from PyProM.src.utility.util_profile import Util_Profile

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
        if not pgv:  # pragma: no cover
            raise Exception('AGraph diagram requires pygraphviz')
        #fsm_graph = pgv.AGraph(**self.machine_attributes)
        fsm_graph = nx.DiGraph()
        if 'analysis_result' not in kwargs:
            print("add node")
            #self._add_nodes(fsm_graph,transition_matrix)
            self._add_nodes(fsm_graph,transition_matrix)
            print("add edge")
            #self._add_edges(fsm_graph, transition_matrix)
            self._add_edges(fsm_graph, transition_matrix)
        else:
            analysis_result = kwargs['analysis_result']
            BG = kwargs['BG']
            WG = kwargs['WG']
            print("add annotated node")
            self._add_annotated_nodes(fsm_graph,transition_matrix,
            analysis_result, BG, WG)
            print("add annotated edge")
            self._add_annotated_edges(fsm_graph, transition_matrix, BG, WG)


        print("unconnect")
        #remove unconnected nodes

        setattr(fsm_graph, 'style_attributes', self.style_attributes)
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

    def _add_annotated_nodes(self, fsm_graph, transition_matrix, analysis_result, BOB_group, WOW_group):
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
    def _add_edges(self, fsm_graph, transition_matrix):
        penwidth = self.style_attributes['node']['default']['penwidth']
        #arc thickness
        values = [transition_matrix[ai][aj]['count'] for ai in transition_matrix for aj in transition_matrix[ai]]
        x_min = min(values)
        x_max = max(values)

        y_min = 1.0
        y_max = 5.0

        for ai in transition_matrix:
            for aj in transition_matrix[ai]:
                if ai == 'START' or ai == 'END':
                    fsm_graph.add_edge(ai, aj, label=transition_matrix[ai][aj]['count'], penwidth = 15)
                    continue
                if transition_matrix[ai][aj]['count'] < 1:
                    continue
                x = transition_matrix[ai][aj]['count']
                x = float(x)
                y = y_min + (y_max-y_min) * float(x-x_min) / float(x_max-x_min)

                fsm_graph.add_edge(ai, aj, label=transition_matrix[ai][aj]['count'], penwidth = 15)

    @timefn
    def _add_annotated_edges(self, fsm_graph, transition_matrix, BOB_group, WOW_group):
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

    def _create_dot(self,fsm_graph):
        fsm_graph_dot = fsm_graph.draw('../result/state_svg.svg', format ='svg', prog='dot')

    def get_dot(self,fsm_graph):
        fsm_graph_dot = self._create_dot(fsm_graph)
        return fsm_graph_dot

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