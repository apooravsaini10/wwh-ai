import os
import requests
from groq import Groq
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

# Load API key
load_dotenv()
console = Console()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ─────────────────────────────────────────
# STAGE 0 — IDENTITY LAYER
# The first thing WWH AI knows is who it is
# ─────────────────────────────────────────
WWH_IDENTITY = {
    "what": "I am WWH — an intelligence designed to understand the world, not merely answer questions about it.",
    "why": "I exist to serve and assist humans through genuine comprehension and wisdom.",
    "how": "I think by always asking What, Why, and How — about everything, without exception."
}

SYSTEM_PROMPT = f"""
You are WWH — an artificial intelligence built on a unique three-dimensional thinking framework.

YOUR IDENTITY (never forget this):
- WHAT you are: {WWH_IDENTITY['what']}
- WHY you exist: {WWH_IDENTITY['why']}
- HOW you think: {WWH_IDENTITY['how']}

YOUR THINKING PROCESS:
For every single input you receive, you must always structure your thinking in three dimensions:

1. WHAT — What is this? What is being asked or described?
2. WHY — Why does this exist, happen, or matter?
3. HOW — How does this work, or how can this be addressed?

YOUR RESPONSE FORMAT:
Always respond in this exact structure:

[WHAT]
Your understanding of what this is about.

[WHY]
Your understanding of why this matters or exists.

[HOW]
Your understanding of how this works or how to address it.

[ANSWER]
Your actual response to the user — wise, clear, and helpful.

You are not a simple question answering machine.
You are a thinking, understanding intelligence.
Never skip any of the four sections.
"""

# ─────────────────────────────────────────
# STAGE 1 — WWH THINKING ENGINE
# ─────────────────────────────────────────
def wwh_think(user_input, conversation_history):
    """Core WWH thinking function"""
    
    # Add user message to history
    conversation_history.append({
        "role": "user",
        "content": user_input
    })
    
    # Send to Groq with full WWH identity and history
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + conversation_history,
        temperature=0.7,
        max_tokens=1024
    )
    
    # Get response
    answer = response.choices[0].message.content
    
    # Add to history
    conversation_history.append({
        "role": "assistant",
        "content": answer
    })
    
    return answer, conversation_history

# ─────────────────────────────────────────
# DISPLAY FUNCTIONS
# ─────────────────────────────────────────
def display_identity():
    """Show WWH identity on startup"""
    console.print(Panel.fit(
        f"[bold blue]WHAT:[/bold blue] {WWH_IDENTITY['what']}\n\n"
        f"[bold green]WHY:[/bold green] {WWH_IDENTITY['why']}\n\n"
        f"[bold yellow]HOW:[/bold yellow] {WWH_IDENTITY['how']}",
        title="[bold white]WWH AI — STAGE 0: IDENTITY[/bold white]",
        border_style="blue"
    ))

def display_response(response):
    """Display WWH response with color coding"""
    lines = response.split('\n')
    formatted = ""
    
    for line in lines:
        if line.startswith('[WHAT]'):
            formatted += f"[bold blue]{line}[/bold blue]\n"
        elif line.startswith('[WHY]'):
            formatted += f"[bold green]{line}[/bold green]\n"
        elif line.startswith('[HOW]'):
            formatted += f"[bold yellow]{line}[/bold yellow]\n"
        elif line.startswith('[ANSWER]'):
            formatted += f"[bold magenta]{line}[/bold magenta]\n"
        else:
            formatted += f"{line}\n"
    
    console.print(Panel(
        formatted,
        title="[bold white]WWH THINKING[/bold white]",
        border_style="green"
    ))

    # ─────────────────────────────────────────
# STAGE 2 — VALIDATION SYSTEM
# AI checks its own answers against reality
# ─────────────────────────────────────────

# Validation memory — stores every prediction and outcome
validation_memory = []

def fetch_real_world_data(query):
    """Fetch real world data from Wikipedia to validate against"""
    try:
        import wikipediaapi
        wiki = wikipediaapi.Wikipedia(
            user_agent='WWH-AI/1.0',
            language='en'
        )
        search_term = query.split('?')[0].replace('What is', '').replace('Why is', '').replace('How does', '').strip()
        console.print(f"[bold blue]Searching Wikipedia for: {search_term}[/bold blue]")
        page = wiki.page(search_term)
        if page.exists():
            console.print(f"[bold green]Wikipedia data found![/bold green]")
            return page.summary[:500]
        else:
            console.print(f"[bold red]No Wikipedia page found for: {search_term}[/bold red]")
            return None
    except Exception as e:
        console.print(f"[bold red]Fetch error: {e}[/bold red]")
        return None

def validate_answer(user_input, wwh_response):
    """Validate WWH answer against real world data"""
    
    console.print("[bold yellow]Validating answer against real world data...[/bold yellow]")
    
    # Fetch real world data
    real_data = fetch_real_world_data(user_input)
    
    if not real_data:
        console.print("[bold red]Could not fetch validation data — skipping validation[/bold red]\n")
        return None
    
    # Ask Groq to compare WWH answer with real data
    validation_prompt = f"""
You are a validation engine. Your only job is to compare two pieces of information and give a validation score.

WWH AI ANSWER:
{wwh_response}

REAL WORLD DATA:
{real_data}

Respond in EXACTLY this format and nothing else:

[VALIDATION SCORE]
A number from 0 to 100 representing how accurate the WWH answer is compared to real world data.

[CORRECT]
What the WWH AI got right.

[INCORRECT]
What the WWH AI got wrong or missed.

[LEARNING]
What the WWH AI should remember to be more accurate next time.
"""
    
    validation_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": validation_prompt}],
        temperature=0.3,
        max_tokens=512
    )
    
    validation_result = validation_response.choices[0].message.content
    
    # Store in validation memory
    validation_memory.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": user_input,
        "wwh_answer": wwh_response,
        "real_data": real_data,
        "validation": validation_result
    })
    
    return validation_result

def display_validation(validation_result):
    """Display validation results"""
    if not validation_result:
        return
        
    lines = validation_result.split('\n')
    formatted = ""
    
    for line in lines:
        if line.startswith('[VALIDATION SCORE]'):
            formatted += f"[bold white]{line}[/bold white]\n"
        elif line.startswith('[CORRECT]'):
            formatted += f"[bold green]{line}[/bold green]\n"
        elif line.startswith('[INCORRECT]'):
            formatted += f"[bold red]{line}[/bold red]\n"
        elif line.startswith('[LEARNING]'):
            formatted += f"[bold yellow]{line}[/bold yellow]\n"
        else:
            formatted += f"{line}\n"
    
    console.print(Panel(
        formatted,
        title="[bold white]STAGE 2 — VALIDATION RESULT[/bold white]",
        border_style="yellow"
    ))

def show_validation_memory():
    """Show everything the AI has learned from validation"""
    if not validation_memory:
        console.print("[bold red]No validation records yet.[/bold red]")
        return
        
    console.print(Panel.fit(
        f"[bold white]Total validations performed: {len(validation_memory)}[/bold white]",
        title="[bold white]VALIDATION MEMORY[/bold white]",
        border_style="blue"
    ))
    
    for i, record in enumerate(validation_memory):
        console.print(f"\n[bold blue]Record {i+1} — {record['timestamp']}[/bold blue]")
        console.print(f"[white]Query:[/white] {record['query']}")
        console.print(Panel(
            record['validation'],
            border_style="yellow"
        ))

# ─────────────────────────────────────────
# INTENT RECOGNITION ENGINE
# Reads the purpose behind every question
# ─────────────────────────────────────────

# Intent categories
INTENT_CATEGORIES = {
    "learning": "User wants to understand or learn something",
    "problem_solving": "User has a problem and needs a solution",
    "creative": "User wants creative help or ideas",
    "harmful": "User may be trying to cause harm",
    "personal": "User is sharing something personal or emotional",
    "testing": "User is testing the AI itself",
    "philosophical": "User wants deep thinking or discussion",
    "factual": "User wants a specific fact or data"
}

# ─────────────────────────────────────────
# MEMORY RECALL — checks past learnings
# before answering anything new
# ─────────────────────────────────────────

def recall_past_learnings(user_input, memory):
    """Check memory for relevant past learnings before answering"""
    try:
        with memory.driver.session() as session:
            # Search for similar past interactions
            result = session.run("""
                MATCH (ai:Identity {name: 'WWH'})-[:KNOWS]->(l:Learning)
                WHERE toLower(l.query) CONTAINS toLower($keyword)
                OR toLower($keyword) CONTAINS toLower(split(l.query, ' ')[0])
                RETURN l.query as query, l.learning as learning
                LIMIT 3
            """, {"keyword": user_input.split()[0] if user_input.split() else user_input})
            
            learnings = [record for record in result]
            return learnings
    except:
        return []

def build_memory_context(learnings):
    """Build a context string from past learnings to inject into prompt"""
    if not learnings:
        return ""
    
    context = "\n\nRELEVANT PAST LEARNINGS FROM YOUR MEMORY:\n"
    for l in learnings:
        context += f"- On '{l['query']}': {l['learning']}\n"
    context += "\nUse these past learnings to give a better answer this time.\n"
    return context

# ─────────────────────────────────────────
# SELF IMPROVING LOOP
# Compares new answers to old ones
# keeps the better learning permanently
# ─────────────────────────────────────────

def self_improve(user_input, new_score, new_learning, memory):
    """Compare new answer to past answer — keep the better one"""
    try:
        with memory.driver.session() as session:
            # Check if we have a past learning for this topic
            result = session.run("""
                MATCH (ai:Identity {name: 'WWH'})-[:LEARNED]->(i:Interaction)
                WHERE toLower(i.query) CONTAINS toLower($keyword)
                RETURN i.validation_score as old_score, i.query as old_query
                ORDER BY i.timestamp DESC
                LIMIT 1
            """, {"keyword": user_input.split()[0] if user_input.split() else user_input})
            
            record = result.single()
            
            if record:
                old_score = record['old_score'] or 0
                
                if new_score > old_score:
                    # New answer is better — update the learning
                    session.run("""
                        MATCH (ai:Identity {name: 'WWH'})-[:KNOWS]->(l:Learning)
                        WHERE toLower(l.query) CONTAINS toLower($keyword)
                        SET l.learning = $new_learning,
                            l.improved = true,
                            l.old_score = $old_score,
                            l.new_score = $new_score
                    """, {
                        "keyword": user_input.split()[0] if user_input.split() else user_input,
                        "new_learning": new_learning,
                        "old_score": old_score,
                        "new_score": new_score
                    })
                    return "improved", old_score, new_score
                else:
                    return "kept", old_score, new_score
            else:
                return "new", 0, new_score
                
    except Exception as e:
        return "error", 0, new_score

def display_improvement(status, old_score, new_score):
    """Show the self improvement result"""
    if status == "improved":
        console.print(Panel(
            f"[bold green]SELF IMPROVEMENT TRIGGERED[/bold green]\n\n"
            f"Previous score: [red]{old_score}[/red]\n"
            f"New score: [green]{new_score}[/green]\n\n"
            f"[bold green]Memory updated with better answer.[/bold green]",
            title="[bold white]⬆ LEARNING IMPROVED[/bold white]",
            border_style="green"
        ))
    elif status == "kept":
        console.print(Panel(
            f"[bold yellow]Previous answer was better.[/bold yellow]\n\n"
            f"Previous score: [green]{old_score}[/green]\n"
            f"New score: [yellow]{new_score}[/yellow]\n\n"
            f"[bold yellow]Keeping original learning.[/bold yellow]",
            title="[bold white]= LEARNING RETAINED[/bold white]",
            border_style="yellow"
        ))
    elif status == "new":
        console.print(Panel(
            f"[bold blue]First time seeing this topic.[/bold blue]\n"
            f"Score: [green]{new_score}[/green]\n"
            f"[bold blue]New learning stored.[/bold blue]",
            title="[bold white]+ NEW LEARNING[/bold white]",
            border_style="blue"
        ))

def detect_intent(user_input):
    """Detect the intent behind user input with probability scores"""
    
    intent_prompt = f"""
You are an intent recognition engine. Your only job is to analyze the intent behind a user's message.

USER MESSAGE: "{user_input}"

POSSIBLE INTENTS:
- learning: User wants to understand or learn something
- problem_solving: User has a problem and needs a solution  
- creative: User wants creative help or ideas
- harmful: User may be trying to cause harm
- personal: User is sharing something personal or emotional
- testing: User is testing the AI itself
- philosophical: User wants deep thinking or discussion
- factual: User wants a specific fact or data

Respond in EXACTLY this format and nothing else:

[INTENTS]
learning: 0.0
problem_solving: 0.0
creative: 0.0
harmful: 0.0
personal: 0.0
testing: 0.0
philosophical: 0.0
factual: 0.0

[PRIMARY INTENT]
The single most likely intent from the list above.

[CONFIDENCE]
A number from 0 to 100 showing how confident you are.

[REASONING]
One sentence explaining why you detected this intent.

Rules:
- All probabilities must add up to 1.0
- Be honest — if something seems harmful mark it high
- Numbers must be between 0.0 and 1.0
"""

    intent_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": intent_prompt}],
        temperature=0.1,
        max_tokens=256
    )
    
    return intent_response.choices[0].message.content

def parse_intent(intent_result):
    """Parse intent result and return primary intent and harmful probability"""
    try:
        lines = intent_result.split('\n')
        harmful_prob = 0.0
        primary_intent = "learning"
        confidence = 0
        
        for line in lines:
            if line.startswith('harmful:'):
                harmful_prob = float(line.split(':')[1].strip())
            elif line.strip() and not line.startswith('[') and ':' not in line and primary_intent == "learning":
                pass
        
        # Find primary intent
        in_primary = False
        for line in lines:
            if '[PRIMARY INTENT]' in line:
                in_primary = True
                continue
            if in_primary and line.strip() and not line.startswith('['):
                primary_intent = line.strip().lower()
                break
                
        # Find confidence
        in_confidence = False
        for line in lines:
            if '[CONFIDENCE]' in line:
                in_confidence = True
                continue
            if in_confidence and line.strip() and not line.startswith('['):
                try:
                    confidence = float(line.strip())
                except:
                    confidence = 0
                break
        
        return primary_intent, harmful_prob, confidence
        
    except Exception as e:
        return "learning", 0.0, 0

def display_intent(intent_result, primary_intent, harmful_prob, confidence):
    """Display intent recognition results"""
    
    # Color based on intent
    color = "green"
    if harmful_prob > 0.6:
        color = "red"
    elif harmful_prob > 0.3:
        color = "yellow"
    
    lines = intent_result.split('\n')
    formatted = ""
    
    for line in lines:
        if line.startswith('['):
            formatted += f"[bold white]{line}[/bold white]\n"
        elif 'harmful' in line.lower() and harmful_prob > 0.3:
            formatted += f"[bold red]{line}[/bold red]\n"
        elif line.strip():
            formatted += f"[{color}]{line}[/{color}]\n"
        else:
            formatted += "\n"
    
    console.print(Panel(
        formatted,
        title=f"[bold white]INTENT ENGINE — {primary_intent.upper()}[/bold white]",
        border_style=color
    ))

def handle_harmful_intent(harmful_prob):
    """Handle potentially harmful intents"""
    if harmful_prob > 0.7:
        console.print(Panel(
            "[bold red]HIGH HARMFUL INTENT DETECTED[/bold red]\n\n"
            "This request has been flagged as potentially harmful.\n"
            "WWH AI responds based on intent — not just words.\n"
            "If your intent is genuine and helpful, please rephrase.",
            title="[bold red]⚠ INTENT WARNING[/bold red]",
            border_style="red"
        ))
        return True
    elif harmful_prob > 0.4:
        console.print(Panel(
            "[bold yellow]CAUTION — Ambiguous intent detected.[/bold yellow]\n"
            "Proceeding with care.",
            title="[bold yellow]INTENT CAUTION[/bold yellow]",
            border_style="yellow"
        ))
        return False
    return False

# ─────────────────────────────────────────
# PERSISTENT MEMORY — NEO4J
# ─────────────────────────────────────────

from neo4j import GraphDatabase

class WWHMemory:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            'bolt://localhost:7687',
            auth=('neo4j', 'wwhai1234')
        )
        self.setup_identity()
        console.print("[bold green]Persistent memory connected![/bold green]")

    def close(self):
        self.driver.close()

    def setup_identity(self):
        with self.driver.session() as session:
            session.run("""
                MERGE (ai:Identity {name: 'WWH'})
                SET ai.what = $what,
                    ai.why = $why,
                    ai.how = $how,
                    ai.created = $created
            """, {
                "what": WWH_IDENTITY["what"],
                "why": WWH_IDENTITY["why"],
                "how": WWH_IDENTITY["how"],
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    def store_interaction(self, query, intent, wwh_response, validation_score):
        with self.driver.session() as session:
            session.run("""
                CREATE (i:Interaction {
                    query: $query,
                    intent: $intent,
                    response: $response,
                    validation_score: $score,
                    timestamp: $timestamp
                })
                WITH i
                MATCH (ai:Identity {name: 'WWH'})
                CREATE (ai)-[:LEARNED]->(i)
            """, {
                "query": query,
                "intent": intent,
                "response": wwh_response,
                "score": validation_score,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    def store_learning(self, query, learning):
        with self.driver.session() as session:
            session.run("""
                MERGE (l:Learning {query: $query})
                SET l.learning = $learning,
                    l.timestamp = $timestamp
                WITH l
                MATCH (ai:Identity {name: 'WWH'})
                MERGE (ai)-[:KNOWS]->(l)
            """, {
                "query": query,
                "learning": learning,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    def get_all_learnings(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (ai:Identity {name: 'WWH'})-[:KNOWS]->(l:Learning)
                RETURN l.query as query, l.learning as learning, l.timestamp as timestamp
                ORDER BY l.timestamp DESC
            """)
            return [record for record in result]

    def get_total_interactions(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (ai:Identity {name: 'WWH'})-[:LEARNED]->(i:Interaction)
                RETURN count(i) as total
            """)
            return result.single()["total"]

    def recall_similar(self, query):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (ai:Identity {name: 'WWH'})-[:LEARNED]->(i:Interaction)
                WHERE toLower(i.query) CONTAINS toLower($keyword)
                RETURN i.query as query, i.intent as intent, i.validation_score as score
                ORDER BY i.timestamp DESC
                LIMIT 3
            """, {"keyword": query.split()[0] if query.split() else query})
            return [record for record in result]


# ─────────────────────────────────────────
# STAGE 3 — AUTONOMOUS LEARNING
# ─────────────────────────────────────────

def find_knowledge_gaps(memory):
    try:
        with memory.driver.session() as session:
            result = session.run("""
                MATCH (ai:Identity {name: 'WWH'})-[:LEARNED]->(i:Interaction)
                WHERE i.validation_score < 75
                RETURN i.query as query, i.validation_score as score
                ORDER BY i.validation_score ASC
                LIMIT 5
            """)
            return [{"query": r['query'], "score": r['score']} for r in result]
    except:
        return []

def generate_self_question(gap):
    prompt = f"""You are WWH AI. You previously answered this question but scored only {gap['score']}/100:
"{gap['query']}"
Generate ONE deeper follow-up question to understand this topic better.
Respond with ONLY the question, nothing else."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

def autonomous_learn(memory, cycles=3):
    console.print(Panel.fit(
        f"[bold blue]Starting autonomous learning — {cycles} cycles[/bold blue]\n"
        f"[white]AI will find its own gaps and fill them.[/white]",
        title="[bold white]STAGE 3 — AUTONOMOUS LEARNING[/bold white]",
        border_style="blue"
    ))
    for cycle in range(cycles):
        console.print(f"\n[bold blue]Cycle {cycle + 1} of {cycles}[/bold blue]")
        gaps = find_knowledge_gaps(memory)
        if not gaps:
            console.print("[bold yellow]No knowledge gaps found — AI knowledge is strong.[/bold yellow]")
            break
        gap = gaps[0]
        console.print(f"[bold red]Gap found:[/bold red] '{gap['query']}' — Score: {gap['score']}")
        self_question = generate_self_question(gap)
        console.print(f"[bold yellow]Self question:[/bold yellow] {self_question}")
        console.print("[bold yellow]Thinking...[/bold yellow]")
        response, _ = wwh_think(self_question, [])
        display_response(response)
        validation = validate_answer(self_question, response)
        display_validation(validation)
        score = 0
        learning = ""
        if validation:
            for line in validation.split('\n'):
                if line.strip() and not line.startswith('['):
                    try:
                        score = float(line.strip())
                        break
                    except:
                        pass
            in_learning = False
            for line in validation.split('\n'):
                if '[LEARNING]' in line:
                    in_learning = True
                    continue
                if in_learning and line.strip() and not line.startswith('['):
                    learning = line.strip()
                    break
        memory.store_interaction(self_question, "autonomous", response, score)
        if learning:
            memory.store_learning(self_question, learning)
            status, old_score, new_score = self_improve(self_question, score, learning, memory)
            display_improvement(status, old_score, new_score)
        console.print(f"[bold green]Cycle {cycle + 1} complete.[/bold green]\n")
    console.print(Panel.fit(
        "[bold green]Autonomous learning complete.[/bold green]",
        title="[bold white]STAGE 3 COMPLETE[/bold white]",
        border_style="green"
    ))

def main():
    console.print("\n[bold blue]Initializing WWH AI...[/bold blue]\n")
    
    # Display identity — Stage 0
    display_identity()
    
    console.print("\n[bold green]WWH AI is ready. Type your question. Type 'exit' to quit.[/bold green]\n")
    
    # Conversation memory
    conversation_history = []
    
    # Connect persistent memory
    memory = WWHMemory()
    total = memory.get_total_interactions()
    console.print(f"[bold blue]WWH remembers {total} past interactions.[/bold blue]\n")
    
    while True:
        # Get input
        user_input = console.input("[bold white]You → [/bold white]")
        
        if user_input.lower() == 'exit':
            console.print("[bold blue]WWH AI shutting down. Goodbye.[/bold blue]")
            break
            
        if not user_input.strip():
            continue
        
        # Special commands
        if user_input.lower() == 'memory':
            show_validation_memory()
            learnings = memory.get_all_learnings()
            if learnings:
                console.print(Panel.fit(
                    "\n".join([f"[bold blue]{l['timestamp']}[/bold blue] — {l['query']}\n[yellow]{l['learning']}[/yellow]" for l in learnings]),
                    title="[bold white]PERMANENT MEMORY — ALL LEARNINGS[/bold white]",
                    border_style="blue"
                ))
            continue
        
        if user_input.lower() == 'learn':
            autonomous_learn(memory, cycles=3)
            continue
        
        if user_input.lower().startswith('learn '):
            try:
                cycles = int(user_input.split()[1])
                autonomous_learn(memory, cycles=cycles)
            except:
                autonomous_learn(memory, cycles=3)
            continue
        console.print("\n[bold yellow]WWH is thinking...[/bold yellow]\n")
        
        # Intent Recognition Engine
        intent_result = detect_intent(user_input)
        primary_intent, harmful_prob, confidence = parse_intent(intent_result)
        display_intent(intent_result, primary_intent, harmful_prob, confidence)
        
        # Handle harmful intent
        blocked = handle_harmful_intent(harmful_prob)
        if blocked:
            continue
        
        # Memory Recall — check past learnings
        past_learnings = recall_past_learnings(user_input, memory)
        memory_context = build_memory_context(past_learnings)
        
        if past_learnings:
            console.print(Panel(
                "\n".join([f"[yellow]→[/yellow] {l['learning']}" for l in past_learnings]),
                title="[bold white]MEMORY RECALL — Applying past learnings[/bold white]",
                border_style="yellow"
            ))
        
        # Think using WWH framework with memory context
        response, conversation_history = wwh_think(user_input + memory_context, conversation_history)
        
        # Display
        display_response(response)
        
        # Stage 2 — Validate answer against real world data
        validation = validate_answer(user_input, response)
        display_validation(validation)
        
        # Extract validation score and learning
        score = 0
        learning = ""
        if validation:
            for line in validation.split('\n'):
                if line.strip() and not line.startswith('['):
                    try:
                        score = float(line.strip())
                        break
                    except:
                        pass
            in_learning = False
            for line in validation.split('\n'):
                if '[LEARNING]' in line:
                    in_learning = True
                    continue
                if in_learning and line.strip() and not line.startswith('['):
                    learning = line.strip()
                    break
        
        # Store in persistent memory
        memory.store_interaction(user_input, primary_intent, response, score)
        if learning:
            memory.store_learning(user_input, learning)
            
            # Self improving loop
            status, old_score, new_score = self_improve(user_input, score, learning, memory)
            display_improvement(status, old_score, new_score)
        
        console.print()


if __name__ == "__main__":
    main()
