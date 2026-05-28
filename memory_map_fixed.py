from flask import Flask, render_template_string
from neo4j import GraphDatabase

app = Flask(__name__)

driver = GraphDatabase.driver(
    'bolt://localhost:7687',
    auth=('neo4j', 'wwhai1234')
)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>WWH AI — Memory Map</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/vis-network.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/vis-network.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0a1a; color: #ffffff; font-family: Arial, sans-serif; }
        #header {
            background: linear-gradient(135deg, #1B3A7A, #0a0a1a);
            padding: 20px 40px;
            border-bottom: 2px solid #1B3A7A;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        #header h1 { font-size: 28px; color: #4A90D9; letter-spacing: 3px; }
        #stats { display: flex; gap: 30px; }
        .stat { text-align: center; }
        .stat .number { font-size: 32px; font-weight: bold; color: #4A90D9; }
        .stat .label { font-size: 12px; color: #888; letter-spacing: 1px; }
        #network { width: 100%; height: calc(100vh - 100px); background: #0a0a1a; }
        #legend {
            position: fixed; bottom: 20px; left: 20px;
            background: rgba(27, 58, 122, 0.8);
            padding: 15px 20px; border-radius: 10px; border: 1px solid #1B3A7A;
        }
        .legend-item { display: flex; align-items: center; gap: 10px; margin: 5px 0; font-size: 13px; }
        .legend-dot { width: 14px; height: 14px; border-radius: 50%; }
        #info-panel {
            position: fixed; top: 100px; right: 20px; width: 300px;
            background: rgba(27, 58, 122, 0.9); padding: 20px;
            border-radius: 10px; border: 1px solid #4A90D9; display: none;
        }
        #info-panel h3 { color: #4A90D9; margin-bottom: 10px; font-size: 14px; }
        #info-content { font-size: 13px; color: #ccc; line-height: 1.6; }
    </style>
</head>
<body>
<div id="header">
    <h1>⬡ WWH AI — MEMORY MAP</h1>
    <div id="stats">
        <div class="stat">
            <div class="number">{{ total_interactions }}</div>
            <div class="label">INTERACTIONS</div>
        </div>
        <div class="stat">
            <div class="number">{{ total_learnings }}</div>
            <div class="label">LEARNINGS</div>
        </div>
        <div class="stat">
            <div class="number">{{ avg_score }}</div>
            <div class="label">AVG SCORE</div>
        </div>
    </div>
</div>
<div id="network"></div>
<div id="legend">
    <div class="legend-item"><div class="legend-dot" style="background:#4A90D9"></div><span>WWH Identity</span></div>
    <div class="legend-item"><div class="legend-dot" style="background:#50C878"></div><span>Interaction</span></div>
    <div class="legend-item"><div class="legend-dot" style="background:#C8A951"></div><span>Learning</span></div>
</div>
<div id="info-panel">
    <h3>NODE DETAILS</h3>
    <div id="info-content"></div>
</div>
<script>
    const nodes = new vis.DataSet({{ nodes | safe }});
    const edges = new vis.DataSet({{ edges | safe }});
    const container = document.getElementById('network');
    const network = new vis.Network(container, { nodes, edges }, {
        nodes: { shape: 'dot', font: { color: '#ffffff', size: 13 }, borderWidth: 2 },
        edges: {
            color: { color: '#1B3A7A', highlight: '#4A90D9' },
            smooth: { type: 'continuous' },
            arrows: { to: { enabled: true, scaleFactor: 0.5 } }
        },
        physics: {
            stabilization: { enabled: true, iterations: 300 },
            barnesHut: { gravitationalConstant: -2000, centralGravity: 0.5, springLength: 120 }
        }
    });
    network.on('stabilizationIterationsDone', function() {
        network.fit({ animation: { duration: 1000, easingFunction: 'easeInOutQuad' } });
    });
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const node = nodes.get(params.nodes[0]);
            document.getElementById('info-panel').style.display = 'block';
            document.getElementById('info-content').innerHTML = node.info || node.label;
        }
    });
</script>
</body>
</html>
"""

@app.route('/')
def memory_map():
    with driver.session() as session:
        # Get identity
        ai_result = session.run("MATCH (ai:Identity {name: 'WWH'}) RETURN ai")
        ai_record = ai_result.single()
        ai_node = dict(ai_record['ai']) if ai_record else {}

        # Get interactions
        i_result = session.run("MATCH (i:Interaction) RETURN i")
        interactions = [dict(r['i']) for r in i_result]

        # Get learnings
        l_result = session.run("MATCH (l:Learning) RETURN l")
        learnings = [dict(r['l']) for r in l_result]

    nodes = []
    edges = []

    # Identity node
    nodes.append({
        "id": 0,
        "label": "WWH AI",
        "size": 40,
        "color": "#4A90D9",
        "info": "<b>IDENTITY</b><br><br><b>WHAT:</b> " + ai_node.get('what', '') +
                "<br><br><b>WHY:</b> " + ai_node.get('why', '') +
                "<br><br><b>HOW:</b> " + ai_node.get('how', '')
    })

    # Interaction nodes
    for i, interaction in enumerate(interactions):
        node_id = i + 1
        score = interaction.get('validation_score', 0)
        color = "#50C878" if score > 70 else "#C8A951" if score > 40 else "#E74C3C"
        nodes.append({
            "id": node_id,
            "label": interaction.get('query', '')[:30] + "...",
            "size": 20,
            "color": color,
            "info": "<b>QUERY:</b> " + interaction.get('query', '') +
                    "<br><br><b>INTENT:</b> " + interaction.get('intent', '') +
                    "<br><br><b>SCORE:</b> " + str(score) +
                    "<br><br><b>TIME:</b> " + interaction.get('timestamp', '')
        })
        edges.append({"from": 0, "to": node_id, "label": "LEARNED"})

    # Learning nodes
    offset = len(interactions) + 1
    for i, learning in enumerate(learnings):
        node_id = offset + i
        nodes.append({
            "id": node_id,
            "label": learning.get('query', '')[:25] + "...",
            "size": 15,
            "color": "#C8A951",
            "info": "<b>LEARNING:</b><br>" + learning.get('learning', '') +
                    "<br><br><b>TIME:</b> " + learning.get('timestamp', '')
        })
        edges.append({"from": 0, "to": node_id, "label": "KNOWS"})

    scores = [i.get('validation_score', 0) for i in interactions]
    avg_score = round(sum(scores) / len(scores)) if scores else 0

    return render_template_string(
        HTML,
        nodes=nodes,
        edges=edges,
        total_interactions=len(interactions),
        total_learnings=len(learnings),
        avg_score=avg_score
    )

@app.route('/debug')
def debug():
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN labels(n) as labels, n")
        records = [str(dict(r['n'])) for r in result]
        return "<br><br>".join(records) if records else "NO DATA"

if __name__ == '__main__':
    print("WWH Memory Map running at http://localhost:5000")
    app.run(debug=False, port=5000)
