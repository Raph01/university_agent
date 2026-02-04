import gradio as gr
from src.agent import app
#import uuid

def chat_with_agent(message, history, request: gr.Request):
    """
    message: The current user input string
    history: A list of previous messages in the chat
    """
    
    # 1. Create a unique thread_id for this specific session if it doesn't exist
    # This ensures memory works correctly for this specific user.
    thread_id = request.session_hash
    config = {"configurable": {"thread_id": thread_id}}
    
    # 2. Prepare the input for the Graph
    # Reset iterations to 0 for every NEW question from the user
    inputs = {"question": message, "iterations":0}
    
    # 3. Stream the response
    # We yield strings so Gradio updates the chat bubble in real-time
    last_node_output = ""
    
    for event in app.stream(inputs, config=config):
        for node_name, state_update in event.items():
            
            # This part helps you see what's happening 'under the hood'
            if node_name == "generate_sql":
                yield f"**Drafting SQL:** `{state_update.get('sql_query')}`"
            
            elif node_name == "execute_sql":
                yield "**Thinking**"
            
            elif node_name == "validate_results":
                val = state_update.get("validation", "")
                if "VALID" in val.upper():
                    yield "Preparing answer..."
                else:
                    yield f" **Validation failed.** Retrying... (Error: {val[:50]}...)"
            
            elif node_name == "generate_answer":
                # This is the final human-friendly response
                yield state_update["final_answer"]

# 4. Gradio Interface
demo = gr.ChatInterface(
    fn=chat_with_agent,
    title="University AI Assistant",
    description="Ask me about students, teachers, and courses",
    textbox=gr.Textbox(placeholder="Ask me a question...", container=True, scale=7, autofocus=True),
    examples=[
        "Who are the MIT teachers?", 
        "How many students are enrolled in each university?",
        "Who are the students enrolled in more than one class?"
    ])

if __name__ == "__main__":
    demo.launch(theme="ocean")