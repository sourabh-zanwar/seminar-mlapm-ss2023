import pygraphviz as pgv
import numpy as np
import itertools
import collections
import copy

import sys
import os
#sys.path.append(os.path.abspath("../utility"))
from PyProM.src.utility.util_profile import Util_Profile
from PyProM.src.utility.util_transform import UtilTransform

#sys.path.append(os.path.abspath("../mining"))
from PyProM.src.mining.dependency_graph import DependencyGraph

#sys.path.append(os.path.abspath(("../model")))
from PyProM.src.model.fsm import FSM_Miner

timefn = Util_Profile.timefn

class HeuristicMiner(object):
    """docstring for FSM"""
    def __init__(self, eventlog, *args, **kwargs):
        super().__init__(*args, **kwargs)
        DG = DependencyGraph()
        dependency_graph = DG.get_dependency_graph(eventlog)
        self.dependency_relation = self.apply_threshold(dependency_graph, threshold = 0.9)
        casual_matrix = self.produce_causal_matrix(self.dependency_relation, 0.1)
        self.count_frequency(eventlog, casual_matrix)




    def apply_threshold(self, dg, threshold = 0.9):
        dependency_graph = dict(dg)
        for ai in list(dependency_graph.keys()):
            for aj in list(dependency_graph[ai].keys()):
                if dependency_graph[ai][aj]['measure'] < threshold:
                    dependency_graph[ai].pop(aj)
            if len(dependency_graph[ai].keys()) == 0:
                dependency_graph.pop(ai)
        return dependency_graph

    def _produce_causal_set(self,dependency_relation, casual_matrix, and_threshold, _type='output'):

        for ai in dependency_relation:
            output = list(dependency_relation[ai].keys())
            if ai not in casual_matrix:
                casual_matrix[ai] = collections.defaultdict(list)
            casual_matrix[ai][_type] = output
            for pair in itertools.combinations(output, r=2):
                bc = 0
                cb = 0
                if pair[0] in dependency_relation:
                    if pair[1] in dependency_relation[pair[0]]:
                        bc = dependency_relation[pair[0]][pair[1]]['count']
                if pair[1] in dependency_relation:
                    if pair[0] in dependency_relation[pair[1]]:
                        cb = dependency_relation[pair[1]][pair[0]]['count']
                if _type == 'output':
                    ab = dependency_relation[ai][pair[0]]['count']
                    ac = dependency_relation[ai][pair[1]]['count']
                    measure = (bc+cb)/(ab+ac+1)
                if _type == 'input':
                    ba = 0
                    ca = 0
                    if pair[0] in dependency_relation:
                        if ai in dependency_relation[pair[0]]:
                            ba = dependency_relation[pair[0]][ai]['count']
                    if pair[1] in dependency_relation:
                        if ai in dependency_relation[pair[1]]:
                            ca = dependency_relation[pair[1]][ai]['count']
                    measure = (bc+cb)/(ca+ba+1)


                if measure > and_threshold:
                    casual_matrix[ai][_type].append(pair)
            casual_matrix[ai][_type] = self.sort_by_length(casual_matrix[ai][_type])
        return casual_matrix

    def produce_causal_matrix(self,dependency_relation, and_threshold):
        casual_matrix = dict()
        casual_matrix = self._produce_causal_set(dependency_relation, casual_matrix, and_threshold, _type = 'output')
        dependency_relation = UtilTransform().transpose_dict(dependency_relation)
        casual_matrix = self._produce_causal_set(dependency_relation, casual_matrix, and_threshold, _type = 'input')

        return casual_matrix

    def sort_by_length(self, _list):
        _list.sort(key = len)
        return _list


    def count_frequency(self, eventlog, casual_matrix):
        event_trace = eventlog.get_event_trace(1)
        trace_count = eventlog._get_trace_count(event_trace)
        for act in casual_matrix:
            #__input = self.sort_by_length(casual_matrix[act]['input'])
            if 'input_count' not in casual_matrix[act]:
                casual_matrix[act]['input_count'] = [0] * len(casual_matrix[act]['input'])
            if 'output_count' not in casual_matrix[act]:
                casual_matrix[act]['output_count'] = [0] * len(casual_matrix[act]['output'])
            seqs = []
            for _input in casual_matrix[act]['input']:
                if isinstance(_input, str):
                    seq = (_input, act)
                else:
                    seq = _input + (act, )
                seqs.append(seq)
            casual_matrix = self.calculate_binding_frequency(casual_matrix,trace_count,act, seqs, _type = 'input')
            seqs = []
            for _output in casual_matrix[act]['output']:
                if isinstance(_output, str):
                    seq = (act, _output)
                else:
                    seq = (act, ) + _output
                seqs.append(seq)
            casual_matrix = self.calculate_binding_frequency(casual_matrix,trace_count,act, seqs, _type = 'output')
                #self.calculate_binding_frequency(casual_matrix, trace_count, _input, _type)
            print("{}: {}".format(act, casual_matrix[act]))

    def tuple_to_string(self, _tuple):
        return '_'.join(_tuple)

    def calculate_binding_frequency(self, casual_matrix, trace_count, act, seqs, _type='input'):
        for trace in trace_count:
            trace_str = self.tuple_to_string(trace)
            #print(trace_str)
            for index, seq in enumerate(seqs):
                seq_str = self.tuple_to_string(seq)
                #print(seq_str)
                if seq_str in trace_str:
                    #print("{}: {}".format(seq_str,trace_str))
                    count_type = _type + "_count"
                    casual_matrix[act][count_type][index] += trace_count[trace]
                    break
        return casual_matrix