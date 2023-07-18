import unittest
import uuid

from internalgraph import Edge, InternalGraph, Node


class GraphTestCase(unittest.TestCase):
    def setUp(self):
        # three levels deep for testing neighbors limited to two
        # A -ac-> C, B -bc-> C, C -cd-> D, D -df-> F, E -ef-> F
        self.node_A = Node(properties={"name": "A",
                                       "key1": "value1",
                                       "key2": "value2"})
        self.node_B = Node(properties={"name": "B",
                                       "key1": "value3",
                                       "key3": "value4"})
        self.node_C = Node(properties={"name": "C"})
        self.node_D = Node(properties={"name": "D"})
        self.node_E = Node(properties={"name": "E"})
        self.node_F = Node(properties={"name": "F"})
        self.edge_ac = Edge(properties={"name": "ac",
                                        "key1": "value5",
                                        "key10": "value6"},
                            from_id=self.node_A.id,
                            to_id=self.node_C.id)
        self.edge_cb = Edge(properties={"name": "cb",
                                        "key10": "value7",
                                        "key11": "value8"},
                            from_id=self.node_C.id,
                            to_id=self.node_B.id)
        self.edge_cd = Edge(properties={"name": "cd"},
                            from_id=self.node_C.id,
                            to_id=self.node_D.id)
        self.edge_df = Edge(properties={"name": "df"},
                            from_id=self.node_D.id,
                            to_id=self.node_F.id)
        self.edge_ef = Edge(properties={"name": "ef"},
                            from_id=self.node_E.id,
                            to_id=self.node_F.id)
        self.graph_ABC = InternalGraph(
                            nodes=[self.node_A, self.node_B, self.node_C],
                            edges=[self.edge_ac, self.edge_cb])

    def test_graph_noedges(self):
        g = InternalGraph(nodes=[self.node_A, self.node_B, self.node_C])
        self.assertEqual(len(g.nodes), 3)
        self.assertEqual(len(g.edges), 0)

    def test_basic_ABC(self):
        self.assertEqual(len(self.graph_ABC.nodes), 3)
        self.assertEqual(len(self.graph_ABC.edges), 2)

    def test_edges_ABC(self):
        all_edges = list(self.graph_ABC.get_all_edges([
            self.node_A.id,
            self.node_B.id,
            self.node_C.id
        ]))
        self.assertIn(self.edge_ac, all_edges)
        self.assertIn(self.edge_cb, all_edges)

    def test_neighbors_ABC(self):
        neighbors = list(self.graph_ABC.get_node_neighbors(self.node_C.id))
        self.assertIn(self.node_A.id, neighbors)
        self.assertIn(self.node_B.id, neighbors)

    def test_node_property_keys(self):
        node_prop_labels = self.graph_ABC.get_all_node_property_names()
        expected_set = {"id", "name", "key1", "key2", "key3"}
        self.assertTrue(isinstance(node_prop_labels, set))
        self.assertEqual(node_prop_labels, expected_set)

    def test_edge_property_keys(self):
        edge_prop_labels = self.graph_ABC.get_all_edge_property_names()
        expected_set = {"id", "name", "key1", "key10", "key11", "start", "end"}
        self.assertIsInstance(edge_prop_labels, set)
        self.assertEqual(edge_prop_labels, expected_set)

    def test_node_exists(self):
        self.assertTrue(self.graph_ABC.node_exists(self.node_A.id))
        invalid = uuid.uuid4()
        self.assertFalse(self.graph_ABC.node_exists(invalid))

    def test_add_edge(self):
        self.assertNotIn(self.node_D, self.graph_ABC.nodes)
        self.graph_ABC.add_node(self.node_D)
        self.graph_ABC.add_edge(self.edge_cd)
        self.assertIn(self.edge_cd, self.graph_ABC.edges)
