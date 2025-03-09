import plotly.graph_objects as go
import networkx as nx
from .. import SimplePipeline

def visualize_pipeline(pipeline: SimplePipeline):
    """Generates an interactive left-to-right visualization of a SimplePipeline using Plotly without Graphviz."""
    
    G = nx.DiGraph()

    # Define colors for different node types
    color_map = {
        "ingest": "#66c2a5",    # Green
        "process": "#fc8d62",   # Orange
        "condition": "#8da0cb", # Blue
        "output": "#e78ac3"     # Pink
    }

    node_colors = []
    node_labels = []
    node_positions = {}

    # Track x-coordinates per layer to enforce left-to-right
    x_layer = 0
    y_spacing = 3  # Space between nodes

    # Add ingest nodes
    for i, ingest_name in enumerate(pipeline.ingests.keys()):
        G.add_node(ingest_name)
        node_labels.append(ingest_name)
        node_colors.append(color_map["ingest"])
        node_positions[ingest_name] = (x_layer, i * y_spacing)  # Spread out vertically

    x_layer += 1  # Move processing steps to the next layer

    # Add pipeline steps
    prev_step = None
    for i, step in enumerate(pipeline.steps):
        step_name = step["name"]
        step_type = step["type"]
        
        G.add_node(step_name)
        node_labels.append(step_name)
        node_colors.append(color_map[step_type])
        node_positions[step_name] = (x_layer, i * y_spacing)  # Arrange nodes left to right

        if prev_step:
            G.add_edge(prev_step, step_name)
        else:
            for ingest_name in pipeline.ingests.keys():
                G.add_edge(ingest_name, step_name)

        if step_type == "condition":
            x_layer += 1  # Branches go further right
            for j, (cond_fn, branch_fn) in enumerate(step["conditions"].items()):
                branch_name = f"{step_name} → {branch_fn.__name__}"
                G.add_node(branch_name)
                G.add_edge(step_name, branch_name)
                node_labels.append(branch_name)
                node_colors.append(color_map["process"])
                node_positions[branch_name] = (x_layer, (i * y_spacing) + (j + 1) * y_spacing)

            default_branch_name = f"{step_name} → Default"
            G.add_node(default_branch_name)
            G.add_edge(step_name, default_branch_name)
            node_labels.append(default_branch_name)
            node_colors.append(color_map["process"])
            node_positions[default_branch_name] = (x_layer, (i * y_spacing) - y_spacing)

        prev_step = step_name
        x_layer += 1  # Move next processing step further right

    # Extract edge positions for Plotly
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = node_positions[edge[0]]
        x1, y1 = node_positions[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color="#888"),
        hoverinfo="none",
        mode="lines"
    )

    # Extract node positions
    node_x, node_y = zip(*[node_positions[node] for node in G.nodes()])

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=node_labels,
        marker=dict(
            size=25,
            color=node_colors,
            line=dict(width=2, color="black")
        ),
        textposition="top center"
    )

    # Create legend
    legend_labels = ["Ingest", "Processing Step", "Condition", "Output"]
    legend_colors = [color_map["ingest"], color_map["process"], color_map["condition"], color_map["output"]]

    legend_trace = go.Scatter(
        x=[None] * 4,
        y=[None] * 4,
        mode="markers",
        marker=dict(size=20, color=legend_colors),
        text=legend_labels,
        textposition="middle right",
        hoverinfo="text"
    )

    fig = go.Figure(data=[edge_trace, node_trace, legend_trace])
    fig.update_layout(
        title=f"Pipeline Visualization: {pipeline.name}",
        title_x=0.5,
        showlegend=False,
        hovermode="closest",
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    fig.show()
