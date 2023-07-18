# Internal Graph

Some problems need a simple graph data structure that can be quickly exported into JSON format or to a Javascript format.  This library is mainly geared towards building static graph files to be imported as Javascript and then visualized with [memgraph/orb](https://https://github.com/memgraph/orb).

There are three classes to use in your code:

* Node (`from internalgraph import Node`)
* Edge (`from internalgraph import Edge`)
* SimpleGraph (`from internalgraph import SimpleGraph`)

Generally, create a graph first, create and append nodes, and then connect nodes with edges that are also attached to the graph.

Adding nodes and edges is idempotent, which means that if node IDs are computed, say as a hash of text values, then repeatedly adding a node does not grow the graph as the duplicate is detected.  Edges _can_ be duplicated unless care is taken to also compute their ID, like hashing the text versions of the start/edge nodes.

Once the graph is built, export it with the `as_json()` or `as_javascript` methods.

## Graph Inspection

A couple of lightweight queries are available.  If more complex queries are needed, then this module should be abandoned for another modules like networkx or even move over to a property graph database.

`get_node_neighbors` will return all neighbor nodes for a provided node, regardless of the direction of the relationship.

`get_all_edges` will return all of the edges for a provided node - this is an intermediate step on the path to getting all node neighbors.

`node_exists` is a quick way to see if the provided ID is in the graph.  Duplicate IDs can always be inserted without concern about duplication.  This only makes sense if IDs are really hashes of fixed properties.

`get_all_node_property_names` returns a unique list of all node properties.  This is handy for a static UI that might want to enumerate all possible property names.

`get_all_node_parents` will return a list of all parent nodes until no parents are available.  This only makes sense for Directed, Acyclic Graphs (DAGs), but there is no enforcement and misuse might cause it to never return.  Perfect for dependency trees to find the core elements of the graph.


## Limitations

* The graph is in memory, and is limited to the amount of memory available
* While there is a `serialize()` method, there is no method to recreate the graph from that serialization
* Very primitive graph queries
