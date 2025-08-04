import os
import openai
import asyncio
from agents import Agent, Runner, RunContextWrapper
from agents.mcp import MCPUtil
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv(override=True)

# Ensure your OpenAI key is available from .env file
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Initialize MCP utility
mcp_util = MCPUtil()

# MCP server URL
mcp_server_url = "https://b842d3af-890b-4010-8f14-3f103b2af0ca-00-1anjj7yu4gpae.riker.replit.dev/sse/"

# Initialize session state for chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to create agent with MCP tools only
def create_texting_assistant():
    tools = []
    
    # Read instructions from prompt.txt file (no fallback)
    with open('prompt.txt', 'r') as f:
        instructions = f.read().strip()

    return Agent(
        name="Texting Strategist",
        instructions=instructions,
        tools=tools,
    )

# Async wrapper for running the agent with MCP tools
async def get_texting_response(question, history):
    # Create agent
    texting_assistant = create_texting_assistant()
    
    # Always load MCP tools
    try:
        # Create a simple context object for MCP tools
        class SimpleContext:
            def __init__(self):
                self.agent = texting_assistant
                self.turn = 0
                self.messages = []
        
        run_context = RunContextWrapper(SimpleContext())
        
        # Get MCP tools asynchronously using the actual agent
        mcp_tools = await mcp_util.get_all_function_tools(
            [mcp_server_url],  # Pass as a list
            convert_schemas_to_strict=True,
            run_context=run_context,
            agent=texting_assistant
        )
        texting_assistant.tools.extend(mcp_tools)
    except Exception as e:
        st.error(f"Could not load MCP tools: {e}")
        return "Sorry, I'm unable to access the Texting OS modules at the moment. Please try again later."
    
    # Combine history and current question to provide context
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    prompt = f"Context of our conversation:\n{context}\n\nCurrent question: {question}"
    
    result = await Runner.run(texting_assistant, prompt)
    return result.final_output

# Streamlit UI
st.set_page_config(page_title="Texting Strategist", layout="wide")
st.title("💬 Texting Strategist")
st.write("I'm your Texting OS strategist. Share your texting scenario and I'll help you navigate it using proven strategies from the Texting OS playbook.")

# Sidebar info
st.sidebar.title("Texting OS Modules")
st.sidebar.info("""
I have access to all 8 Texting OS modules:
• Strategy
• Match to Date  
• Meet to Date
• Second Date
• Momentum
• Spicing It Up
• When Things Go Awry
• Rekindling Old Flames
""")

# Conversation controls
st.sidebar.subheader("Conversation")
if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []
    st.experimental_rerun()

# Display some helpful examples
with st.sidebar.expander("Example Scenarios"):
    st.markdown("""
    **Format your question like this:**
    
    <user_problem>
    I matched with someone on Hinge and sent a message, but she hasn't responded in 2 days. Should I send a follow-up?
    </user_problem>
    
    **Other examples:**
    - "Had a great first date, when should I text her?"
    - "She flaked on our second date, what should I do?"
    - "We've been texting for a week, how do I ask her out?"
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("🐙 Made by the Lonely Octopus Team")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_question = st.chat_input("Share your texting scenario...")

if user_question:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_question})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_question)
    
    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your scenario..."):
            response_placeholder = st.empty()
            
            # Get response from agent
            response = asyncio.run(get_texting_response(user_question, st.session_state.messages))
            
            # Update response placeholder
            response_placeholder.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})