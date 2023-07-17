# Internal Graph

Some problems need a simple graph data structure that can be quickly exported into JSON format or to a Javascript format.  This library is mainly geared towards building static graph files to be imported as Javascript and then visualized with [memgraph/orb](https://https://github.com/memgraph/orb).

There are three classes to use in your code:

* Node (`from internalgraph import Node`)
* Edge (`from internalgraph import Edge`)
* SimpleGraph (`from internalgraph import SimpleGraph`)

Generally, create a graph first, create and append nodes, and then connect nodes with edges that are also attached to the graph.

Adding nodes and edges is idempotent, which means that if node IDs are computed, say as a hash of text values, then repeatedly adding a node does not grow the graph as the duplicate is detected.  Edges _can_ be duplicated unless care is taken to also compute their ID, like hashing the text versions of the start/edge nodes.

Once the graph is build, export it with the `as_json()` or `as_javascript` methods.
