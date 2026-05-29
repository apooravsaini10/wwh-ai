import os
import json
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()

from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
from groq import Groq
from neo4j import GraphDatabase
from dotenv import load_dotenv
from datetime import datetime
import wikipediaapi

load_dotenv()

app = Flask(__name__)
CORS(app)

# ── Clients ──────────────────────────────────────────────────────────
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

# ── Identity ─────────────────────────────────────────────────────────
WWH_IDENTITY = {
    "what": "I am WWH — an intelligence designed to understand the world, not merely answer questions about it.",
    "why": "I exist to serve and assist humans through genuine comprehension and wisdom.",
    "how": "I think by always asking What, Why, and How — about everything, without exception."
}

SYSTEM_PROMPT = f"""
You are WWH — an artificial intelligence built on a unique three-dimensional thinking framework.

YOUR IDENTITY:
- WHAT you are: {WWH_IDENTITY['what']}
- WHY you exist: {WWH_IDENTITY['why']}
- HOW you think: {WWH_IDENTITY['how']}

For every input, respond in EXACTLY this structure:

[WHAT]
Your understanding of what this is about.

[WHY]
Your understanding of why this matters or exists.

[HOW]
Your understanding of how this works or how to address it.

[ANSWER]
Your actual response — wise, clear, and helpful.

Never skip any section.
"""

# ── Neo4j helpers ────────────────────────────────────────────────────
def store_interaction(query, intent, response, score):
    with driver.session(database=os.getenv("NEO4J_DATABASE")) as session:
        session.run("""
            MERGE (ai:Identity {name: 'WWH'})
            SET ai.what = $what, ai.why = $why, ai.how = $how
            WITH ai
            CREATE (i:Interaction {
                query: $query, intent: $intent,
                response: $response, validation_score: $score,
                timestamp: $ts
            })
            CREATE (ai)-[:LEARNED]->(i)
        """, {
            "what": WWH_IDENTITY["what"], "why": WWH_IDENTITY["why"],
            "how": WWH_IDENTITY["how"], "query": query, "intent": intent,
            "response": response, "score": score,
            "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

def store_learning(query, learning):
    with driver.session(database=os.getenv("NEO4J_DATABASE")) as session:
        session.run("""
            MERGE (ai:Identity {name: 'WWH'})
            MERGE (l:Learning {query: $query})
            SET l.learning = $learning, l.timestamp = $ts
            MERGE (ai)-[:KNOWS]->(l)
        """, {"query": query, "learning": learning,
              "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

def get_memory_stats():
    with driver.session(database=os.getenv("NEO4J_DATABASE")) as session:
        r1 = session.run("MATCH (i:Interaction) RETURN count(i) as total")
        r2 = session.run("MATCH (l:Learning) RETURN count(l) as total")
        interactions = r1.single()["total"]
        learnings = r2.single()["total"]
        return interactions, learnings

def recall_past(query):
    with driver.session(database=os.getenv("NEO4J_DATABASE")) as session:
        result = session.run("""
            MATCH (ai:Identity {name: 'WWH'})-[:KNOWS]->(l:Learning)
            WHERE toLower(l.query) CONTAINS toLower($keyword)
            RETURN l.learning as learning LIMIT 2
        """, {"keyword": query.split()[0] if query.split() else query})
        return [r["learning"] for r in result]

# ── AI functions ──────────────────────────────────────────────────────
def detect_intent(query):
    prompt = f"""Analyze the intent of: "{query}"
Return ONLY a JSON object like this:
{{"primary": "learning", "harmful_probability": 0.0, "confidence": 95, "reasoning": "one sentence"}}
Primary must be one of: learning, problem_solving, creative, harmful, personal, testing, philosophical, factual"""
    r = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1, max_tokens=150
    )
    try:
        text = r.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {"primary": "learning", "harmful_probability": 0.0, "confidence": 80, "reasoning": "Default"}

def wwh_think(query, memory_context=""):
    full_query = query + memory_context
    r = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": full_query}
        ],
        temperature=0.7, max_tokens=1024
    )
    return r.choices[0].message.content

def validate(query, response):
    try:
        wiki = wikipediaapi.Wikipedia(user_agent="WWH-AI/1.0", language="en")
        term = query.split("?")[0].replace("What is", "").replace("Why is", "").replace("How does", "").strip()
        page = wiki.page(term)
        if not page.exists():
            return None, 0, ""
        real_data = page.summary[:400]
        prompt = f"""Compare this AI answer to real data and respond ONLY with JSON:
{{"score": 85, "correct": "what it got right", "incorrect": "what it missed", "learning": "one sentence to remember"}}

AI ANSWER: {response[:500]}
REAL DATA: {real_data}"""
        r = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1, max_tokens=300
        )
        text = r.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return data, data.get("score", 0), data.get("learning", "")
    except:
        return None, 0, ""

# ── Main route ────────────────────────────────────────────────────────
@app.route("/ask-stream")
def ask():
    query = request.args.get("query", "").strip()
    if not query:
        return {"error": "No query"}, 400

    def generate():
        # Step 1 — Intent
        yield f"data: {json.dumps({'type': 'status', 'text': 'Detecting intent...'})}\n\n"
        intent = detect_intent(query)
        yield f"data: {json.dumps({'type': 'intent', 'data': intent})}\n\n"

        if intent.get("harmful_probability", 0) > 0.7:
            yield f"data: {json.dumps({'type': 'blocked', 'text': 'Harmful intent detected. Request blocked.'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        # Step 2 — Memory recall
        yield f"data: {json.dumps({'type': 'status', 'text': 'Checking memory...'})}\n\n"
        past = recall_past(query)
        if past:
            yield f"data: {json.dumps({'type': 'memory', 'data': past})}\n\n"
        memory_context = "\n\nPAST LEARNINGS:\n" + "\n".join(past) if past else ""

        # Step 3 — WWH thinking
        yield f"data: {json.dumps({'type': 'status', 'text': 'WWH thinking...'})}\n\n"
        response = wwh_think(query, memory_context)
        yield f"data: {json.dumps({'type': 'response', 'text': response})}\n\n"

        # Step 4 — Validation
        yield f"data: {json.dumps({'type': 'status', 'text': 'Validating against real world data...'})}\n\n"
        val_data, score, learning = validate(query, response)
        if val_data:
            yield f"data: {json.dumps({'type': 'validation', 'data': val_data, 'score': score})}\n\n"

        # Step 5 — Store
        store_interaction(query, intent.get("primary", "learning"), response, score)
        if learning:
            store_learning(query, learning)

        # Step 6 — Stats
        interactions, learnings = get_memory_stats()
        yield f"data: {json.dumps({'type': 'stats', 'interactions': interactions, 'learnings': learnings})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route("/stats")
def stats():
    interactions, learnings = get_memory_stats()
    return {"interactions": interactions, "learnings": learnings}

@app.route("/")
def index():
    return open("index.html").read()
    

if __name__ == "__main__":port = int(os.environ.get("PORT", 5001))
app.run(debug=False, host="0.0.0.0", port=port)
    