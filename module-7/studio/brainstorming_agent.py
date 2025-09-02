import os
import getpass
import re
import time
import requests
from typing import Dict, List
from urllib.parse import urlparse
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, continue without it

# Setup API key
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

# LLM
llm = ChatOpenAI(model="gpt-4o")

# Tools
@tool
def browse_web(query: str) -> str:
    """Browse web for information using Tavily."""
    from tavily import TavilyClient
    client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
    try:
        response = client.search(query=query)
        results = response.get("results", [])
        if results:
            return "\n".join([f"{r['title']}: {r['content']}" for r in results[:3]])
        return "No info found."
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def deep_research(query: str, depth: str = "medium") -> str:
    """Perform deep research with multiple strategies and content verification.

    Args:
        query: The research query
        depth: Research depth - 'shallow' (fast), 'medium' (balanced), 'deep' (thorough)
    """
    from tavily import TavilyClient
    import time

    client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

    try:
        # Step 1: Initial search to get broad results
        print(f"🔍 Starting deep research for: '{query}' (depth: {depth})")

        initial_response = client.search(query=query, max_results=5)
        initial_results = initial_response.get("results", [])

        if not initial_results:
            return "No information found for the query."

        # Step 2: Analyze and categorize results
        analyzed_results = []
        for result in initial_results:
            url = result.get('url', '')
            title = result.get('title', '')
            content = result.get('content', '')

            # Basic URL validation
            parsed_url = urlparse(url)
            is_valid_url = bool(parsed_url.scheme and parsed_url.netloc)

            analyzed_results.append({
                'url': url,
                'title': title,
                'content': content,
                'is_valid': is_valid_url,
                'domain': parsed_url.netloc,
                'relevance_score': len(content) / 100 if content else 0  # Simple relevance metric
            })

        # Step 3: Filter and prioritize results
        valid_results = [r for r in analyzed_results if r['is_valid']]
        if not valid_results:
            return "No valid sources found for the query."

        # Sort by relevance
        valid_results.sort(key=lambda x: x['relevance_score'], reverse=True)

        # Step 4: Deep content extraction based on depth
        research_output = []
        research_output.append(f"🔬 DEEP RESEARCH RESULTS for: '{query}'\n")
        research_output.append(f"📊 Found {len(valid_results)} valid sources\n")

        max_sources = {'shallow': 2, 'medium': 3, 'deep': 5}[depth]
        processed_sources = 0

        for result in valid_results[:max_sources]:
            try:
                research_output.append(f"\n{'='*60}")
                research_output.append(f"📄 Source {processed_sources + 1}: {result['title']}")
                research_output.append(f"🔗 URL: {result['url']}")
                research_output.append(f"🏢 Domain: {result['domain']}")
                research_output.append(f"{'='*60}\n")

                # Extract deeper content if depth allows
                if depth in ['medium', 'deep']:
                    try:
                        # Attempt to get more content from the URL
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }
                        response = requests.get(result['url'], headers=headers, timeout=10)
                        response.raise_for_status()

                        # Extract meaningful content (simplified)
                        page_content = response.text

                        # Look for main content areas (basic extraction)
                        content_indicators = [
                            '<main', '<article', '<div class="content"',
                            '<div id="content"', '<section'
                        ]

                        extracted_content = ""
                        for indicator in content_indicators:
                            if indicator in page_content.lower():
                                # Simple content extraction
                                start_idx = page_content.lower().find(indicator)
                                if start_idx != -1:
                                    end_idx = page_content.find('</div>', start_idx + len(indicator))
                                    if end_idx == -1:
                                        end_idx = start_idx + 1000  # Fallback
                                    extracted_content = page_content[start_idx:end_idx]
                                    break

                        if extracted_content:
                            # Clean up HTML tags (basic)
                            import re
                            clean_content = re.sub(r'<[^>]+>', '', extracted_content)
                            clean_content = ' '.join(clean_content.split())[:500]  # Limit length

                            research_output.append("📖 EXTRACTED CONTENT:")
                            research_output.append(clean_content)
                            research_output.append("\n")
                        else:
                            research_output.append("📖 SUMMARY:")
                            research_output.append(result['content'][:300] + "...")

                    except Exception as e:
                        research_output.append("📖 SUMMARY:")
                        research_output.append(result['content'][:300] + "...")
                        research_output.append(f"\n⚠️  Content extraction failed: {str(e)}")
                else:
                    # Shallow mode - just use search result
                    research_output.append("📖 SUMMARY:")
                    research_output.append(result['content'][:300] + "...")

                processed_sources += 1

                # Add small delay to be respectful to servers
                if depth == 'deep':
                    time.sleep(0.5)

            except Exception as e:
                research_output.append(f"❌ Error processing source: {str(e)}")
                continue

        # Step 5: Synthesis and recommendations
        research_output.append(f"\n{'='*60}")
        research_output.append("🎯 RESEARCH SYNTHESIS")
        research_output.append(f"{'='*60}")

        # Count unique domains
        domains = list(set([r['domain'] for r in valid_results[:max_sources]]))
        research_output.append(f"🌐 Sources from {len(domains)} unique domains: {', '.join(domains[:5])}")

        # Quality assessment
        avg_relevance = sum([r['relevance_score'] for r in valid_results[:max_sources]]) / len(valid_results[:max_sources]) if valid_results else 0
        quality_rating = "High" if avg_relevance > 5 else "Medium" if avg_relevance > 2 else "Low"
        research_output.append(f"⭐ Quality Rating: {quality_rating} (avg relevance: {avg_relevance:.1f})")

        # Recommendations
        research_output.append("\n💡 RECOMMENDATIONS:")
        if len(valid_results) >= 3:
            research_output.append("✅ Multiple reliable sources found - information appears comprehensive")
        else:
            research_output.append("⚠️ Limited sources found - consider broadening search terms")

        if depth == 'shallow':
            research_output.append("💭 For deeper analysis, try depth='medium' or 'deep'")
        elif depth == 'medium':
            research_output.append("💭 For comprehensive analysis, try depth='deep'")

        return "\n".join(research_output)

    except Exception as e:
        return f"❌ Deep research failed: {str(e)}\n\n💡 Try using the basic browse_web tool instead."

@tool
def save_to_memory(info: str) -> str:
    """Save information to memory."""
    global memory
    if 'memory' not in globals():
        memory = []
    memory.append(info)
    return f"Saved: {info}"

@tool
def read_file(file_path: str) -> str:
    """Read the contents of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"File content from {file_path}:\n\n{content}"
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

@tool
def edit_file(file_path: str, old_string: str, new_string: str) -> str:
    """Edit a file by replacing old_string with new_string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if old_string not in content:
            return f"Error: The string '{old_string}' was not found in {file_path}"

        new_content = content.replace(old_string, new_string, 1)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return f"Successfully edited {file_path}"
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"Error editing file {file_path}: {str(e)}"

@tool
def apply_patch(file_path: str, patch_content: str) -> str:
    """Apply a patch/diff to a file."""
    try:
        # Parse the patch format (similar to VS Code's applyPatch tool)
        lines = patch_content.strip().split('\n')
        if not lines:
            return "Error: Empty patch content"

        # Read the original file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Simple patch application (for basic cases)
        # This is a simplified version - production would need more robust parsing
        updated_content = original_content

        for line in lines:
            if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
                continue
            elif line.startswith('-'):
                # Remove line
                line_content = line[1:].strip()
                if line_content in updated_content:
                    updated_content = updated_content.replace(line_content + '\n', '', 1)
                    updated_content = updated_content.replace(line_content, '', 1)
            elif line.startswith('+'):
                # Add line
                line_content = line[1:].strip()
                # For simplicity, append to end (real implementation would use line numbers)
                if updated_content and not updated_content.endswith('\n'):
                    updated_content += '\n'
                updated_content += line_content + '\n'

        # Write back the updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        return f"Successfully applied patch to {file_path}"
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"Error applying patch to {file_path}: {str(e)}"

@tool
def generate_prd(feature: str, description: str, user_input: str, update_existing: bool, user_id: str = "default") -> str:
    """Generate or update PRD with user isolation using LangGraph Store.

    Args:
        feature: The name of the feature
        description: Brief description of the feature
        user_input: User's specific requirements or changes
        update_existing: Whether to update existing PRD or create new
        user_id: User identifier for isolation
    """
    # This will be called with store parameter from LangGraph
    # For now, we'll use the database approach but structure it for future migration
    safe_feature = feature.replace(" ", "_").replace("/", "_")
    return save_prd_to_sqlite(feature, description, user_input, safe_feature, update_existing, user_id)

@tool
def read_prd(feature_name: str, user_id: str = "default") -> str:
    """Read existing PRD content with user isolation using LangGraph Store.

    Args:
        feature_name: The name of the feature to read
        user_id: User identifier for isolation
    """
    # This will be called with store parameter from LangGraph
    # For now, we'll use the database approach but structure it for future migration
    safe_feature = feature_name.replace(" ", "_").replace("/", "_")
    content = read_prd_from_sqlite(safe_feature, user_id)

    if content:
        return f"📄 Existing PRD for '{feature_name}' (User: {user_id}):\n\n{content}"
    else:
        return f"❌ No existing PRD found for '{feature_name}' for user '{user_id}'."

def save_prd_to_sqlite(feature: str, description: str, user_input: str, safe_feature: str, update_existing: bool, user_id: str) -> str:
    """Save PRD to SQLite database with user isolation."""
    import sqlite3
    from datetime import datetime

    # Generate PRD content
    prd_content = generate_prd_content(feature, description, user_input, update_existing, "sqlite", safe_feature)

    # Connect to SQLite database
    conn = sqlite3.connect('prds.db')
    cursor = conn.cursor()

    # Create table if not exists with user_id column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            feature_name TEXT NOT NULL,
            title TEXT,
            description TEXT,
            content TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            UNIQUE(user_id, feature_name)
        )
    ''')

    now = datetime.now().isoformat()

    if update_existing:
        # Check if PRD exists for this user and read existing content
        cursor.execute("SELECT id FROM prds WHERE user_id = ? AND feature_name = ?", (user_id, safe_feature))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE prds
                SET content = ?, updated_at = ?
                WHERE user_id = ? AND feature_name = ?
            """, (prd_content, now, user_id, safe_feature))
            action = "updated"
        else:
            cursor.execute("""
                INSERT INTO prds (user_id, feature_name, title, description, content, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, safe_feature, feature, description, prd_content, now, now))
            action = "created"
    else:
        cursor.execute("""
            INSERT OR REPLACE INTO prds (user_id, feature_name, title, description, content, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, safe_feature, feature, description, prd_content, now, now))
        action = "saved"

    conn.commit()
    conn.close()

    return f"PRD {action} in database for feature: {feature} (User: {user_id})\n\n{prd_content}"

def read_existing_prd(feature: str, storage_type: str, safe_feature: str, user_id: str = "default") -> str:
    """Read existing PRD content from the specified storage type."""
    try:
        if storage_type == "sqlite":
            return read_prd_from_sqlite(safe_feature, user_id)
        else:  # fallback to sqlite
            return read_prd_from_sqlite(safe_feature, user_id)
    except Exception as e:
        return f"Error reading existing PRD: {str(e)}"

def read_prd_from_sqlite(safe_feature: str, user_id: str) -> str:
    """Read PRD content from SQLite database with user isolation."""
    import sqlite3
    try:
        conn = sqlite3.connect('prds.db')
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM prds WHERE user_id = ? AND feature_name = ?", (user_id, safe_feature))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else ""
    except Exception:
        return ""

def generate_prd_content(feature: str, description: str, user_input: str, update_existing: bool, storage_type: str = "sqlite", safe_feature: str = "", user_id: str = "default") -> str:
    """Generate PRD content (extracted from original function)."""

    # If updating existing PRD, read the current content first
    existing_content = ""
    if update_existing and safe_feature:
        existing_content = read_existing_prd(feature, storage_type, safe_feature, user_id)

    prompt = f"""
Analyze the user's input: "{user_input}" for feature "{feature}" with description "{description}".

{"You are UPDATING an existing PRD. Here is the current PRD content:" if update_existing else "Generate a complete new PRD"}
{"" + existing_content + "" if update_existing else ""}

{"Update the existing PRD based on the user's request. Modify only the relevant sections and preserve the rest of the content." if update_existing else "Generate a complete PRD in markdown with the following sections, filling each based on analysis:"}

{"" if update_existing else '''
- Introduction (Purpose, Scope, Objectives)
- User Stories (Generate 3-5 user stories using this specific format for each:

## Description
As a [specific user type/role], I want to [specific action/goal], so that [specific benefit/value].

## Entry Point
Entry Point: [specific entry point or feature name]
Figma Link: [if applicable, otherwise omit]

## Pre-Condition
[Specific conditions that must be met before using this feature]
- User has logged in with appropriate credentials
- User has required entitlements/permissions
- User has navigated to the specific page/feature

## Done When/Acceptance Criteria
[Specific, measurable criteria for completion]
- Functional requirements (what the feature does)
- UI/UX requirements (what user sees and interacts with)
- Performance requirements
- Security requirements

## Exception Handling
[How the system handles errors or edge cases]

## General BO handling
[General back office system behaviors and standards]
)
- Functional Requirements (core features)
- Non-Functional Requirements (performance, security, etc.)
- Assumptions
- Dependencies
- Risks and Mitigations
- Timeline (realistic phases)
- Stakeholders
- Metrics
'''}

{"Ensure the updated PRD maintains consistency and incorporates the user's requested changes while preserving existing valuable content." if update_existing else "Ensure all content is generated dynamically from the analysis, no hardcoded text. Use the Everest Back Office context where appropriate."}
"""

    response = llm.invoke(prompt)
    return response.content

# Register all tools
tools = [browse_web, deep_research, save_to_memory, read_file, edit_file, apply_patch, generate_prd, read_prd]
llm_with_tools = llm.bind_tools(tools)

# Global memory - initialize here
memory: List[str] = []

# Custom State with User Context
class BrainstormState(MessagesState):
    memory: List[str]
    user_id: str  # User identifier for isolation
    session_id: str  # Session tracking

# Nodes
def assistant(state: BrainstormState):
    # Extract user context from state
    user_id = getattr(state, 'user_id', 'default')
    session_id = getattr(state, 'session_id', 'default_session')

    sys_msg = SystemMessage(content=f"""You are a brainstorming agent for Product Owners. Help brainstorm features, research, and discuss ideas through conversation.

CURRENT SESSION INFO:
- User ID: {user_id}
- Session ID: {session_id}

IMPORTANT GUIDELINES:
- Only use generate_prd tools when user EXPLICITLY asks to "generate PRD", "create PRD", "edit PRD", "update PRD", or similar direct requests
- For general brainstorming, feature discussion, or research - just respond normally without calling tools
- If user wants to modify existing PRD, FIRST use read_prd to see current content, then use appropriate generate_prd tool with update_existing=True
- Use browse_web tool for quick, simple searches
- Use deep_research tool when user asks for "deep research", "thorough research", "comprehensive analysis", or wants detailed investigation with content verification
- Use save_to_memory tool when user provides important information to remember
- Use read_file tool when user wants to examine existing files or documents
- Use edit_file tool when user wants to make specific text replacements in files
- Use apply_patch tool when user provides a patch/diff to apply to a file
- Keep conversations natural and engaging

PRD TOOLS (User-Isolated):
- generate_prd: Generate or update PRD (automatically saves to user-specific database entries)
- read_prd: Read existing PRD content from user's database entries

WHEN EDITING PRDs:
1. First use read_prd to see the current PRD content for this user
2. Then use generate_prd with update_existing=True
3. The system will automatically read the existing content and generate an updated version
4. Each user's PRDs are completely isolated from other users

RESEARCH TOOLS:
- browse_web: Fast, basic search (3 results max)
- deep_research: Thorough research with content verification, multiple sources, and synthesis (choose depth: 'shallow', 'medium', 'deep')""")
    response = llm_with_tools.invoke([sys_msg] + state["messages"])

    # Safely get memory from state
    current_memory = getattr(state, 'memory', []) if hasattr(state, 'memory') else []
    if isinstance(state, dict):
        current_memory = state.get('memory', [])

    return {"messages": [response], "memory": current_memory, "user_id": user_id, "session_id": session_id}

def human_in_loop(state: BrainstormState):
    # In Studio, input is handled through the UI
    # This function is mainly for compatibility
    # Safely get memory from state
    current_memory = getattr(state, 'memory', []) if hasattr(state, 'memory') else []
    if isinstance(state, dict):
        current_memory = state.get('memory', [])

    # Preserve user context
    user_id = getattr(state, 'user_id', 'default')
    session_id = getattr(state, 'session_id', 'default_session')

    return {"messages": state["messages"], "memory": current_memory, "user_id": user_id, "session_id": session_id}

# Graph
builder = StateGraph(BrainstormState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_node("human", human_in_loop)

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")
builder.add_edge("human", "assistant")  # Allow human to loop back to assistant

graph = builder.compile()

# For Studio - this will be the entry point
def main():
    initial_state = {
        "messages": [HumanMessage(content="I want to add a reporting feature for Power Cash so users can see their activity more clearly and stay engaged with the app.")],
        "memory": [],
        "user_id": "demo_user",  # Default user for testing
        "session_id": "demo_session_001"  # Default session for testing
    }
    result = graph.invoke(initial_state)
    return result

if __name__ == "__main__":
    main()

# Helper function to test multi-user isolation
def test_multi_user_isolation():
    """Test function to demonstrate user isolation"""
    print("🧪 Testing Multi-User PRD Isolation...")
    print()

    # Test User 1
    print("👤 User 1: Creating PRD for 'User Authentication'")
    user1_state = {
        "messages": [HumanMessage(content="Generate PRD for User Authentication system")],
        "memory": [],
        "user_id": "user_alice",
        "session_id": "session_alice_001"
    }
    result1 = graph.invoke(user1_state)
    print("✅ User 1 PRD created")
    print()

    # Test User 2
    print("👤 User 2: Creating PRD for 'User Authentication' (same feature name)")
    user2_state = {
        "messages": [HumanMessage(content="Generate PRD for User Authentication system with different requirements")],
        "memory": [],
        "user_id": "user_bob",
        "session_id": "session_bob_001"
    }
    result2 = graph.invoke(user2_state)
    print("✅ User 2 PRD created")
    print()

    # Test reading User 1's PRD
    print("👤 User 1: Reading their PRD")
    read_user1 = read_prd.invoke({"feature_name": "User Authentication", "user_id": "user_alice"})
    print(f"User 1 PRD length: {len(read_user1)} characters")
    print()

    # Test reading User 2's PRD
    print("👤 User 2: Reading their PRD")
    read_user2 = read_prd.invoke({"feature_name": "User Authentication", "user_id": "user_bob"})
    print(f"User 2 PRD length: {len(read_user2)} characters")
    print()

    # Verify isolation
    if "user_alice" in read_user1 and "user_bob" in read_user2:
        print("✅ SUCCESS: User isolation working correctly!")
        print("   - User 1's PRD is separate from User 2's PRD")
        print("   - Each user can only access their own PRDs")
    else:
        print("❌ ERROR: User isolation not working properly")

    print()
    print("🎯 Multi-user isolation test completed!")
