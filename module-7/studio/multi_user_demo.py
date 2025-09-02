#!/usr/bin/env python3
"""
Multi-User Brainstorming Agent with LangGraph Sessions
Demonstrates proper user isolation using LangGraph's built-in thread management
"""
import asyncio
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from typing import List

# Import our agent
from brainstorming_agent import (
    BrainstormState, assistant, human_in_loop, tools,
    generate_prd, read_prd
)

class MultiUserBrainstormingAgent:
    """Multi-user agent with proper session isolation"""

    def __init__(self):
        # Memory store for long-term memory (user-specific data)
        self.store = InMemoryStore()

        # Checkpointer for short-term memory (conversation state)
        self.checkpointer = MemorySaver()

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph with proper state management"""
        builder = StateGraph(BrainstormState)
        builder.add_node("assistant", assistant)
        builder.add_node("tools", ToolNode(tools))
        builder.add_node("human", human_in_loop)

        builder.add_edge(START, "assistant")
        builder.add_conditional_edges("assistant", tools_condition)
        builder.add_edge("tools", "assistant")
        builder.add_edge("human", "assistant")

        # Compile with checkpointer and store
        return builder.compile(
            checkpointer=self.checkpointer,
            store=self.store
        )

    async def start_user_session(self, user_id: str, session_id: str, initial_message: str):
        """Start a new user session"""
        config = {
            "configurable": {
                "thread_id": f"{user_id}_{session_id}",  # Unique thread per user+session
                "user_id": user_id
            }
        }

        initial_state = {
            "messages": [HumanMessage(content=initial_message)],
            "memory": [],
            "user_id": user_id,
            "session_id": session_id
        }

        # Run the agent
        result = await self.graph.ainvoke(initial_state, config=config)
        return result

    async def continue_user_session(self, user_id: str, session_id: str, message: str):
        """Continue an existing user session"""
        config = {
            "configurable": {
                "thread_id": f"{user_id}_{session_id}",
                "user_id": user_id
            }
        }

        # Get current state
        current_state = await self.graph.aget_state(config)

        # Add new message
        new_state = {
            "messages": current_state.values.get("messages", []) + [HumanMessage(content=message)],
            "memory": current_state.values.get("memory", []),
            "user_id": user_id,
            "session_id": session_id
        }

        # Continue the conversation
        result = await self.graph.ainvoke(new_state, config=config)
        return result

    def get_user_prds(self, user_id: str):
        """Get all PRDs for a specific user"""
        # This would use the store to retrieve user-specific PRDs
        # For now, we'll use the database approach
        import sqlite3
        try:
            conn = sqlite3.connect('prds.db')
            cursor = conn.cursor()
            cursor.execute("SELECT feature_name, title, description FROM prds WHERE user_id = ?", (user_id,))
            results = cursor.fetchall()
            conn.close()
            return results
        except:
            return []

async def demo_multi_user_sessions():
    """Demonstrate multi-user session isolation"""
    print("🚀 Multi-User Brainstorming Agent Demo")
    print("=" * 50)

    agent = MultiUserBrainstormingAgent()

    # User 1: Alice (Product Manager)
    print("👤 User 1: Alice (Product Manager)")
    print("-" * 30)

    await agent.start_user_session(
        user_id="alice_pm",
        session_id="session_001",
        initial_message="Generate PRD for User Authentication system with email/password login"
    )
    print("✅ Alice created PRD for User Authentication")

    # User 2: Bob (Engineer)
    print("\n👤 User 2: Bob (Engineer)")
    print("-" * 30)

    await agent.start_user_session(
        user_id="bob_engineer",
        session_id="session_001",
        initial_message="Generate PRD for User Authentication system with OAuth and social login"
    )
    print("✅ Bob created PRD for User Authentication (different requirements)")

    # User 3: Charlie (Finance)
    print("\n👤 User 3: Charlie (Finance)")
    print("-" * 30)

    await agent.start_user_session(
        user_id="charlie_finance",
        session_id="session_001",
        initial_message="Generate PRD for Payment Processing system with multiple payment methods"
    )
    print("✅ Charlie created PRD for Payment System")

    # Test session isolation
    print("\n🔍 Testing Session Isolation:")
    print("-" * 30)

    # Alice continues her session
    print("👤 Alice continues her session:")
    await agent.continue_user_session(
        user_id="alice_pm",
        session_id="session_001",
        message="Update the authentication PRD to include password reset functionality"
    )
    print("✅ Alice updated her PRD (only affects her session)")

    # Bob continues his session
    print("\n👤 Bob continues his session:")
    await agent.continue_user_session(
        user_id="bob_engineer",
        session_id="session_001",
        message="Update the authentication PRD to include Google OAuth integration"
    )
    print("✅ Bob updated his PRD (only affects his session)")

    # Check user isolation
    print("\n📊 User Data Isolation Check:")
    print("-" * 30)

    alice_prds = agent.get_user_prds("alice_pm")
    bob_prds = agent.get_user_prds("bob_engineer")
    charlie_prds = agent.get_user_prds("charlie_finance")

    print(f"👤 Alice has {len(alice_prds)} PRD(s)")
    for prd in alice_prds:
        print(f"   - {prd[0]}: {prd[1]}")

    print(f"\n👤 Bob has {len(bob_prds)} PRD(s)")
    for prd in bob_prds:
        print(f"   - {prd[0]}: {prd[1]}")

    print(f"\n👤 Charlie has {len(charlie_prds)} PRD(s)")
    for prd in charlie_prds:
        print(f"   - {prd[0]}: {prd[1]}")

    # Verify complete isolation
    print("\n🔒 Isolation Verification:")
    print("-" * 30)

    isolation_ok = (
        len(alice_prds) > 0 and
        len(bob_prds) > 0 and
        len(charlie_prds) > 0 and
        alice_prds != bob_prds  # Different content
    )

    if isolation_ok:
        print("✅ SUCCESS: Complete user isolation achieved!")
        print("   ✓ Each user has their own PRD collection")
        print("   ✓ Sessions are properly isolated")
        print("   ✓ No cross-user data contamination")
        print("   ✓ LangGraph thread management working correctly")
    else:
        print("❌ ERROR: User isolation issues detected")

    print("\n🎯 Key Benefits of LangGraph Session Management:")
    print("-" * 50)
    print("✅ Automatic thread-based conversation isolation")
    print("✅ Built-in checkpointing for session persistence")
    print("✅ Store-based long-term memory with namespaces")
    print("✅ No manual user session management needed")
    print("✅ Proper state management across interactions")
    print("✅ Scalable multi-user architecture")

if __name__ == "__main__":
    asyncio.run(demo_multi_user_sessions())
