from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from src.db_utils import run_query
from src.llm_factory import get_models
from src.prompts import SYSTEM_PROMPT, VALIDATOR_PROMPT #our promtps
from langgraph.checkpoint.memory import MemorySaver #to keep memory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


# Five steps to Graph:
#1. Define the State class
#2. Start the Graph builder
#3. Create a node
#4. Create edges
#5. Compile the Graph


#1 - State Class
class State(TypedDict):
    question: str
    messages: List[BaseMessage]
    sql_query: str
    results: List[dict]
    validation: str
    final_answer: str
    iterations: int #using this for self correction

#2 Start Graph Builder
graph_builder=StateGraph(State)

#3 Nodes:
# Generator with OpenAI
# SQL in SQLite
# Validation with Groq

generator_llm, validator_llm=get_models()

def generate_sql(state: State):
    print('--- DECIDING NEXT STEP (SQL Generation) ---')
    
    # 1. Get history
    history = state.get("messages", [])
    
    # 2. Hard-code a requirement for a new turn
    # This tells the LLM: history is for WHO, SQL is for WHAT.
    turn_instruction = (
        "\n\n[INSTRUCTION]: Use history only to resolve pronouns (like 'they'). "
        "Do NOT answer from memory. If the user asks for information not in the "
        "CURRENT DATABASE RESULTS, you MUST generate a SQL query. "
        "If you do not write a SQL query, you are failing your task."
    )

    # 3. Invoke LLM with the context of what we already have
    current_data = state.get("results", [])
    
    response = generator_llm.invoke([
        ("system", SYSTEM_PROMPT + turn_instruction + f"\nExisting Data: {current_data}"), 
        *history, 
        ("human", state["question"])
    ])
    
    sql = response.content.replace("```sql", "").replace("```", "").strip()
    
    # 4. Update Message History
    if state.get("iterations", 0) == 0:
        new_messages = history + [HumanMessage(content=state["question"]), AIMessage(content=sql)]
    else:
        new_messages = history + [AIMessage(content=sql)]
        
    # 5. Clear old results so the answer node can't use them.
    return {
        "sql_query": sql, 
        "iterations": state.get("iterations", 0) + 1, 
        "messages": new_messages,
        "results": [],      # Force the graph to find NEW results
        "validation": "" 
    }
    
def execute_sql(state: State):
    query = state.get("sql_query", "").strip()

    # If the generator returned NO_QUERY, skip the SQL 
    if "NO_QUERY" in query.upper():
        print('Skipping SQL [Chat Mode]')
        return {"results": [{"chat_mode": True}]}
    
    # Otherwise, proceed to run the actual SQL
    print(f'Executing SQL [SQLite]: {query}')
    return {"results": run_query(query)}

def validate_results(state:State):
    print('Validating results [Groq]')
    # If we are in chat mode, it's automatically "Valid"
    if state.get("results") and state["results"][0].get("chat_mode"):
        return {"validation": "VALID"}

    prompt= VALIDATOR_PROMPT.format(
        question=state["question"],
        sql=state["sql_query"],
        results=state["results"]
    )
    response=validator_llm.invoke(prompt)
    return {"validation": response.content}

def generate_answer(state: State):
    history = state.get("messages", [])
    results = state.get("results", [])
    question = state.get("question", "")

    # 1. Identify if this was a "NO_QUERY" turn (like 'What is my name?')
    is_chat = "NO_QUERY" in state.get("sql_query", "").upper()

    # 2. Build a prompt that gives the LLM everything it needs
    # We include the results from DB AND the conversation history
    summary_prompt = (
        f"User Question: {question}\n"
        f"Database Results: {results}\n"
        f"Conversation History: {history}\n\n"
        "INSTRUCTION: Answer the question. If the answer is in the History (like a name), use it. "
        "If the answer is in the Database Results, use those. Be natural."
    )
    
    response = generator_llm.invoke(summary_prompt)
    return {"final_answer": response.content, "messages": history + [AIMessage(content=response.content)]}

def grade_analysis(state: State): #not a Node, it doesnt change the data
    # If valid, go to answer
    if "VALID" in state["validation"].upper():
        return "happy"
    # If we've tried 3 times, give up to save money/time
    if state.get("iterations", 0) >= 3:
        return "give_up"
    # Otherwise, try again
    return "try_again"  

#Now adding to the graph_builder:
graph_builder.add_node("generate_sql", generate_sql)
graph_builder.add_node("execute_sql", execute_sql)
graph_builder.add_node("validate_results", validate_results)
graph_builder.add_node("generate_answer", generate_answer)



#Edges:
graph_builder.set_entry_point("generate_sql")
graph_builder.add_edge("generate_sql", "execute_sql")
graph_builder.add_edge("execute_sql", "validate_results")

# If validation fails, we try again:
graph_builder.add_conditional_edges("validate_results",grade_analysis,
    {
        "happy": "generate_answer",
        "try_again": "generate_sql",
        "give_up": "generate_answer" 
    }
)

#graph_builder.add_edge("validate_results", "generate_answer")
graph_builder.add_edge("generate_answer", END)

# Step 5: Compile the Graph
memory = MemorySaver()
app = graph_builder.compile(checkpointer=memory)
