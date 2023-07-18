import unittest
import uuid

from internalgraph import Edge, InternalGraph, Node


class BuildEdgesTestCase(unittest.TestCase):
    def setUp(self):
        self.from_id = uuid.uuid4()
        self.to_id = uuid.uuid4()
        self.edge_id = uuid.uuid4()
        self.good_properties = {'one': 'a',
                                'two': 'b',
                                'label': 'MyEdge'}
        self.bad_properties = ['one', 'a', 'two', 'b']

    def test_new_empty_edge(self):
        edge = Edge(from_id=self.from_id,
                    to_id=self.to_id)
        self.assertIsInstance(edge.id, uuid.UUID)
        self.assertIsInstance(edge._properties, dict)
        self.assertEqual(edge.from_id, self.from_id)
        self.assertEqual(edge.to_id, self.to_id)

    def test_new_edge_with_id(self):
        edge = Edge(from_id=self.from_id,
                    to_id=self.to_id,
                    id=self.edge_id)
        self.assertEqual(edge.id, self.edge_id)
        self.assertIsInstance(edge._properties, dict)
        self.assertEqual(edge.from_id, self.from_id)
        self.assertEqual(edge.to_id, self.to_id)
        self.assertEqual(repr(edge),
                         f'<Edge ID {edge.id} (no "label" property)>')

    def test_new_edge_with_props(self):
        edge = Edge(from_id=self.from_id,
                    to_id=self.to_id,
                    properties=self.good_properties)
        self.assertIsInstance(edge.id, uuid.UUID)
        self.assertIsInstance(edge._properties, dict)
        self.assertEqual(edge.from_id, self.from_id)
        self.assertEqual(edge.to_id, self.to_id)
        for k, v in self.good_properties.items():
            self.assertEqual(edge.get_property(k), v)
        self.assertEqual(repr(edge),
                         f'<Edge "{self.good_properties["label"]}" ID {edge.id}>')

    def test_edge_serialize(self):
        edge = Edge(from_id=self.from_id,
                    to_id=self.to_id)
        serialized = edge.serialize()
        self.assertDictEqual(serialized,
                             {
                                 'id': edge.id,
                                 'start': self.from_id,
                                 'end': self.to_id,
                                 'short_details': {},
                             })

    def test_edge_serialize_with_details(self):
        from_id = uuid.uuid4()
        to_id = uuid.uuid4()
        edge = Edge(from_id=from_id,
                    to_id=to_id,
                    properties=self.good_properties)
        serialized = edge.serialize()
        self.good_properties.pop('label')  # rebuilt on next test case
        self.assertDictEqual(serialized,
                             {
                                 'id': edge.id,
                                 'start': from_id,
                                 'end': to_id,
                                 'label': 'MyEdge',
                                 'short_details': self.good_properties
                             })
