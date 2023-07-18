import unittest
import uuid

import internalgraph
from internalgraph import Edge, InternalGraph, Node


class BuildNodesTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_new_empty_node(self):
        self.node = Node()
        self.assertIsInstance(self.node.id, uuid.UUID)

    def test_new_node_with_id(self):
        obj_id = uuid.uuid4()
        self.node = Node(id=obj_id)
        self.assertEqual(obj_id, self.node.id)
        self.assertEqual(repr(self.node),
                         f'<Node ID {self.node.id} (no "label" property)>')

    def test_new_node_with_props(self):
        props = {
            'label': 'pumpernickle',
            'label with spaces': 'Pumper Nickle',
            'unicode label': 'Pōmper Nickle'
        }
        self.node = Node(properties=props)
        self.assertEqual(self.node.get_property('label'), 'pumpernickle')
        self.assertEqual(self.node.get_property('label with spaces'), 'Pumper Nickle')
        self.assertEqual(self.node.get_property('unicode label'), 'Pōmper Nickle')
        self.assertEqual(repr(self.node),
                         f'<Node "pumpernickle" ID {self.node.id}>')

    def test_split_dict(self):
        source = {"a": 1,
                  "b": 2,
                  "c": {"d": 3},
                  "e": [4, 5, 6]
                  }
        left, right = internalgraph.BaseGraphElement.split_dict(
            in_dict=source, strip_list=["a", "e"]
        )
        self.assertEqual(left,
                         {"a": 1, "e": [4, 5, 6]})
        self.assertEqual(right,
                         {"b": 2, "c": {"d": 3}})
