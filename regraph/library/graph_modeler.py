import networkx as nx

from regraph.library.data_structures import (TypedGraph,
                                             TypedDiGraph,
                                             Homomorphism)
from regraph.library.category_op import (find_PB,
                                         find_PO,
                                         find_final_PBC)

class GraphModeler(object):

    def __init__(self, l, homL, names):
        """ l : nx.Graph list (directed or not) [G1, G2 ...]
            homL : dict list (starting with [G1->G2 ... ])
            names : str list
        """
        typing_graph = None
        homL.insert(0, None)
        self.rw_chain = []
        self.rw_names = []
        self.changes = []

        for i in range(len(l)):
            directed = type(l[î]) == nx.DiGraph
            typing_graph = self.make_tygraph(l[i][0], typing_graph, hom[i], directed)
            self.rw_chain[i] = Rewriter(typing_graph)

            if i>len(names):
                self.rw_names[i] = None
            else:
                if names[i] in self.rw_names:
                    raise ValueError(
                        "Name %s already used for another graph" % names[i]
                    )
                if type(names[i]) != str:
                    raise ValueError(
                        "Graph names have to be Strings"
                    )
                self.rw_names[i] = names[i]

    def make_tygraph(self, G, T, hom, di):
        res = TypedDiGraph(T) if di else TypedGraph(T)
        for n in G.nodes():
            res.add_node(n, hom[n], G.node[n])
        for (n1, n2) in G.edges():
            res.add_edge(n1, n2, G.edge[n1][n2])
        res.hom = Homomorphism(res, T, hom)
        return res

    def get_by_id(self, n):
        return self.rw_chain[n]

    def get_id_from_name(self, name):
        for i in range(self.rw_names):
            if self.rw_names[i] == name:
                return i
        raise ValueError(
            "Graph %s is not defined in the modeler"% name
        )

    def get_by_name(self, name):
        for i in range(self.rw_names):
            if self.rw_names[i] == name:
                return self.rw_chain[i]
        raise ValueError(
            "Graph %s is not defined in the modeler" % name
        )

    def rewrite(self, n_i, left_h, right_h):
        """ n_i : name or id
            left_h : P -> L
            right_h : P -> R
        """
        if type(n_i) == int:
            rew = self.get_by_id(n_i)
            i = n_i
        elif type(n_i) == str:
            rew = self.get_by_name(n_i)
            i = self.get_id_from_name(n_i)
        else:
            raise ValueError(
                "Undefined identifier of type %s, was expecting int or str" %
                type(n_i)
            )
        changes[i] = rew.typed_rewriting(left_h, right_h)

    def propagate_from(self, n_i):
        """ n_i : name or id
        """
        if type(n_i) == int:
            i = n_i
        elif type(n_i) == str:
            i = self.get_id_from_name(n_i)
        else:
            raise ValueError(
                "Undefined identifier of type %s, was expecting int or str" %
                type(n_i)
            )
        if i >= len(self.rw_chain)-1:
            return
        else:
            G = self.rw_chain[i+1].graph_
            T = G.metamodel_
            T-_Tprime, T-_T, junk = changes[i]
            G-, G-_G, G-_T- = pullback(G.hom, T-_T)
            Gprime, G-_Gprime, Gprime_Tprime = pullback_complement(G-_T-, T-_Tprime)
            Gprime.metamodel_ = Gprime_Tprime.target_
            Gprime.hom = Gprime_Tprime
            changes[i+1] = G-_Gprime, G-_G, Gprime_Tprime
            propagate_from(self, i+1)

    def propagate_all(self):
        for i in range(len(changes)-1, -1, -1):
            if changes[i] != None:
                self.propagate_from(i)

    def commit_changes(self):
        for i in range(len(changes)):
            rw_chain[i] = Rewriter(changes[i][0].target_)
            changes[i] = None
