"""
Very simple graph storage class with primitive query and serialization.
"""

import datetime
import uuid
import json
from abc import ABC
from typing import Any, Iterator, List, Optional, Set, Tuple, Union


class BaseGraphElement(ABC):
    """
    Abstract base class for Elements within a graph.  Contains common methods and
    attributes, but should not be instantiated directly.
    """

    def __init__(self, id: Optional[Union[uuid.UUID, str]] = None,
                 properties: Optional[dict] = None):
        """
        Constructor.
        :param id: Optional.  UUID to assign the element.
                   Auto-generated otherwise
        :param properties: Optional.  Dictionary of attributes.
        """
        self._properties = properties if properties else dict()
        self.id = id if id else uuid.uuid4()

    def set_property(self, name: str, value: Any):
        """
        Set a property for the object.
        :param name: String.  Common values are _name_ and _type_.
        Set a property for the object.
        :param name: String.  Common values are _name_ and _type_.
                     Spaces and Unicode are allowed.
        :param value: Any type, but string is popular.  Note that any non-string
                     types will need their own serializers.
        :return: None
        """
        self._properties[name] = value

    def get_property(self, name: str, no_error=False) -> Any:
        """
        Return the value of a property.  If _no_error_ is True, None will be
        returned if the property is not set, but otherwise an error is raised.
        Use _items()_ or an iterator to get the list of keys/values.
        :param name: Name of the attribute to get,
        :param no_error: Boolean that suppresses KeyError if _name_ does not
                         exist.
        :return: The value of the parameter.  _None_ is returned if the _name_
                 does not exist and _no_error_ is True.
        """
        if name == 'id':
            return self.id
        if no_error:
            return self._properties.get(name)
        return self._properties[name]  # with built-in exceptions

    @staticmethod
    def split_dict(in_dict: dict, strip_list: List[str]) -> Tuple[dict, dict]:
        """
        Return two lists.  Any item in in_dict whose key is in strip_list
        gets filtered into the first list in the return value.  All other
        key/value pairs are returned in the second.
        @param in_dict: input dictionary who keys will be compared to strip_list
        @param strip_list: list of key names to put in the first output
        @return: A list of two dictionaries.  The first has items stripped out
                 of the in_dict and the second has all other attributes
        """
        left = dict()
        right = dict()
        if not strip_list:
            raise ValueError("strip_list must be non-empty")
        for k, v in in_dict.items():
            if k in strip_list:
                left[k] = v
            else:
                right[k] = v
        return left, right  # tuple

    def __dict__(self):
        """
        The graph element represented as a dictionary.
        :return: Dictionary of properties and the element's ID
        """
        return self._properties | {'id': self.id}

    def __iter__(self):
        """
        Iterate through all properties which can be queried
        :return: List of strings to feed to _get_property()_
        """
        key_list = list(self._properties.keys())
        key_list.append(self.id)
        for k in set(key_list):
            yield k

    def __repr__(self):
        """
        A quick representation of the object suitable for use in debuggers/IDEs.
        If the object has a `label` attribute, that is included, but if it is
        missing, it says that too.
        :return: a string
        """
        if self._properties.get('label'):
            return f'<{self.__class__.__name__} "{self._properties["label"]}" ' \
                   f'ID {str(self.id)}>'
        return f'<{self.__class__.__name__} ID {str(self.id)} (no "label" property)>'

    def serialize(self,
                  split_list: Optional[List[str]] = None) -> dict:
        """
        Generalized method to get all attributes in derived classes and
        serializing properties
        :return: dictionary for the object
        """
        if not split_list:
            split_list = [
                "id",
                "label",
                "description",
                "type",
            ]
        original = self.__dict__()
        outer, inner = self.split_dict(original, split_list)
        return outer | {"short_details": inner}


class Node(BaseGraphElement):
    """
    A noun in the Knowledge Graph.  It can be created with
    no parameters, but it will be difficult to discern what it represents.
    Each node can have properties, with a
    preference for properties _name_ and _type_ for visualization
    labels and visualization iconography, respectively.
    """
    pass


class Edge(BaseGraphElement):
    """
    Edge graph element used to associate two Node objects
    by UUID.  Each edge can also have properties, with a
    preference for properties _name_ and _type_ for visualization
    labels and visualization iconography, respectively.
    """
    def __init__(self,
                 from_id: Union[uuid.UUID, str], to_id: Union[uuid.UUID, str],
                 id: Optional[uuid.UUID] = None,
                 properties: Optional[dict] = None):
        """
        Constructor.  _id_ and _properties_ are optional.
        :param from_id: UUID for the start of the relationship
        :param to_id: UUID for the target of the relationship
        :param id: UUID for this edge, to make it unique
        :param properties: an optional dictionary of arbitrary attributes
        """
        super().__init__(id=id, properties=properties)
        self.from_id = from_id
        self.to_id = to_id

    def __dict__(self) -> dict:
        """
        The graph element represented as a dictionary.
        @return: Dictionary of properties and the element's ID
        """
        return self._properties | {
            'id': self.id,
            'start': self.from_id,
            'end': self.to_id
        }

    def serialize(self) -> dict:
        """
        The graph element represented in a format for lambda.
        :return:
        """
        split_list = [
            "id",
            "label",
            "description",
            "type",
            "start",
            "end",
        ]
        return super().serialize(split_list=split_list)

class InternalGraph:
    """
    Bootstrap concept to build a primitive, in memory property graph.
    The InternalGraph is meant for medium to small graphs, with less than
    a few hundred total nodes and a few thousand edges.  More may be possible,
    but more formal methods are recommended.
    The InternalGraph comes with two primitive traversal mechanisms.  Given
    an initial node, locate all attached edges.  Also, given an initial node,
    locate all adjacent nodes.  With these techniques, all connected nodes
    can be explored, but isolated nodes or subgraphs will be hidden.
    Graphs cannot be merged, but the public attributes `nodes` and `edges`
    can be copied over to another InternalGraph instance.
    """

    def __init__(self, nodes: Optional[list] = None,
                 edges: Optional[list] = None):
        """
        Constructor
        :param nodes: Optional, a list of pre-computed nodes to add to the graph
        :param edges: Optional, a list of pre-computed edges to add to the graph
        """
        self.nodes: List[Node] = nodes if nodes else list()
        self.edges: List[Edge] = edges if edges else list()
        self._all_node_ids = set()
        if nodes:
            for x in nodes:
                self._all_node_ids.add(x.id)

    def __str__(self) -> str:
        """
        Construct the JSON version of the graph
        :return: a JSON string
        """
        return self.as_json()

    def serialize(self) -> dict:
        """
        Return the object as a dict which can be rendered as JSON,
        although some types might need conversion prior to rendering
        (e.g. uuids)
        :return: dictionary
        """
        return {
            'nodes': [n.serialize() for n in self.nodes],
            'edges': [e.serialize() for e in self.edges]
        }

    @staticmethod
    def _json_serialize_defaults(value) -> Any:
        """
        A _default_ method for `json.dumps` that stringifies objects that
        cannot be handled by the _json_ module.  This is similar to the
        _Serializer_ part of the _rest_framework_, but much simpler as it
        does not need to support deserialization.
        :param value: A value whose type is unknown to the _json_ module
        :return: a string representation of the value
        Raises: TypeError if the value still cannot be handled
        """
        datetime_format: str = '%Y-%m-%dT%H:%M:%SZ'
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, datetime.datetime):
            return value.strftime(datetime_format)
        if isinstance(value, Node) or isinstance(value, Edge):
            return value.__dict__()
        raise TypeError(
            'Unserializable object {} of type {}'.format(str(value),
                                                         type(value))
        )

    def as_json(self, indent: Optional[int] = 2) -> str:
        """
        Translate an InternalGraph to JSON in the format:
        `{ "name": graph_name, "nodes": [], "edges": [] }`
        :param indent: Optional.  Integers make pretty strings.  None is minified.
        :return: a string
        """
        return json.dumps(self.serialize(),
                          default=self._json_serialize_defaults,
                          indent=indent)

    def as_javascript(self) -> str:
        """
        Create javascript suitable for use by the Orb graph visualization tool,
        namely that it can be statically included as an HTML script and used
        directly by the package in a way that works quickly with the examples.
        The output creates a `const nodes = []` line and `const edges = []`
        with both having an `id` and `label` parameter.  Edges also have
        a `start` and `end` parameters.
        :return: a string
        """
        output = [
           'if (typeof nodes === "undefined") { nodes = []; }',
           'if (typeof edges === "undefined") { edges = []; }',
        ]
        for node in self.nodes:
            output.append(
                'nodes.push(' + json.dumps(node.serialize(),
                                           default=self._json_serialize_defaults,
                                           indent=4) + ');'
            )
        for edge in self.edges:
            output.append(
                'edges.push(' + json.dumps(edge.serialize(),
                                           default=self._json_serialize_defaults,
                                           indent=4) + ');'
            )
        return "\n".join(output)

    def get_node_neighbors(self, id: Union[uuid.UUID, str]) -> Iterator[Union[uuid.UUID, str]]:
        """
        Given a node ID, find the IDs of all neighbor nodes.  A neighbor
        can either be upstream or downstream in a relationship.
        :param id: Node ID to search
        :return: Iterator of neighbor UUIDs
        """
        for e in self.edges:
            if id == e.from_id:
                yield e.to_id
            if id == e.to_id:
                yield e.from_id

    def get_all_edges(self, node_ids: List[Union[uuid.UUID, str]]) -> Iterator[Edge]:
        """
        Get the edges for a collection of nodes so that a subgraph can
        be shown.  This is good if the list of nodes has been filtered in
        some way.
        :param node_ids: List of node IDs
        :return: List of Edge objects
        """
        for e in self.edges:
            if e.from_id in node_ids and e.to_id in node_ids:
                yield e

    def add_node(self, node: Union[Node, List[Node]]) -> List:
        """
        Add a node to the graph if it doesn't already exist.  When synthesizing
        nodes, it is very likely that a new node will be synthesized and this
        avoids duplication.  Note that duplicate would still have the same
        UUID.
        :param node: Node object(s)
        :return: List of nodes added that were not duplicative.
        """
        added_nodes = list()
        if not isinstance(node, list):
            node = [node]
        for n in node:
            if n.id not in self._all_node_ids:
                self.nodes.append(n)
                self._all_node_ids.add(n.id)
                added_nodes.append(n)
        return added_nodes

    def add_edge(self, edge: Union[Edge, List[Edge]]) -> None:
        """
        Add an edge to the graph.
        :param edge: Edge object
        :return: None
        """
        if isinstance(edge, list):
            self.edges.extend(edge)
        else:
            self.edges.append(edge)

    def node_exists(self, id: Union[uuid.UUID, str]) -> bool:
        """
        Quick test to see if a node exists with the provided ID
        :param id: UUID object
        :return: True or False
        """
        return id in self._all_node_ids

    def get_all_edge_property_names(self) -> set:
        """
        Return a set (unique list) of all property names (not values)
        across all edges
        @return: set of "keys" or, if a filter key is provided, return those
                 values
        """
        total = {  # the set enforces uniqueness
            k
            for e in self.edges
            for k in e.__dict__().keys()
        }
        return total

    def get_all_node_property_values(self,
                                     filter_key: str) \
            -> set:
        """
        Return a set (unique list) of all property names (not values)
        across all nodes
        @param filter_key: key name to grab values across edges
        @return: set of "keys" or, if a filter key is provided, return those
                 values
        """
        total = {  # the set enforces uniqueness
            v
            for e in self.nodes
            for k, v in e.__dict__().items()
            if filter_key and k == filter_key
        }
        return total

    def get_all_node_property_names(self) -> set:
        """
        Return a set (unique list) of all property names (not values)
        across all nodes
        @return: set of "keys" or, if a filter key is provided, return those
                 values
        """
        total = {  # the set enforces uniqueness
            k
            for e in self.nodes
            for k in e.__dict__().keys()
        }
        return total

    def get_all_edge_property_values(self,
                                     filter_key: str) \
            -> set:
        """
        Return a set (unique list) of all property names (not values)
        across all edges
        @param filter_key: key name to grab values across edges
        @return: set of "keys" or, if a filter key is provided, return those
                 values
        """
        total = {  # the set enforces uniqueness
            v
            for e in self.edges
            for k, v in e.__dict__().items()
            if filter_key and k == filter_key
        }
        return total

    # _NODE_ID_TYPE = Union[uuid.UUID, str]
    # def find_node(self, node_id: _NODE_ID_TYPE) -> Optional[Node]:
    #     for n in self.nodes:
    #         if n.id == node_id:
    #             return n
    #     return None

    def __getitem__(self, name):
        if isinstance(name, Node):
            for x in self.nodes:
                if x.id == name:
                    return x
        elif isinstance(name, Edge):
            for x in self.edges:
                if x.id == name:
                    return x
        else:
            for x in self.nodes:
                if x.id == name:
                    return x
            for x in self.edges:
                if x.id == name:
                    return x

    def get_all_node_parents(self, start: Node,
                             parents: Optional[List[Node]] = None) -> Optional[List[Node]]:
        total = [
            self[e.to_id]
            for e in self.edges
            if e.from_id == start.id
        ]
        if not total or len(total) == 0:
            return None
        for found_node in total:
            if found_node.get_property("label").find(":") < 0:
                continue
            if not parents or found_node not in parents:
                children = self.get_all_node_parents(found_node, parents=total)
                if children:
                    for child in children:
                        if child not in total:
                            total.append(child)
        return total
