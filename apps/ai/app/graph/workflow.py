from langgraph.graph import START, END, StateGraph

from app.graph.state import RAGState

from app.graph.nodes import generate_node, retrieve_node
from app.graph.rerank_node import (
    rerank_node
)

graph_builder = StateGraph(RAGState)

graph_builder.add_node(
    "retrieve",
    retrieve_node,
)
graph_builder.add_node("generate", generate_node)
graph_builder.add_node(
    "rerank",
    rerank_node,
)

graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "rerank")
graph_builder.add_edge("rerank", "generate")
graph_builder.add_edge("generate", END)


graph = graph_builder.compile()