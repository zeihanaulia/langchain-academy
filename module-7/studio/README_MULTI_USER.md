# Multi-User Brainstorming Agent with LangGraph

## Overview

This implementation demonstrates **proper multi-user session management** using LangGraph's built-in memory and thread management capabilities. Unlike the previous approach that manually managed user isolation in a database, this leverages LangGraph's native features for robust, scalable multi-user support.

## Key Concepts from LangGraph Memory Documentation

### Short-term Memory (Thread-scoped)
- **Thread**: Organizes multiple interactions in a session (like email conversations)
- **State Management**: Agent state persisted via thread-scoped checkpoints
- **Automatic Isolation**: Each thread maintains separate conversation history
- **Persistence**: State includes messages, memory, and other contextual data

### Long-term Memory (Cross-session)
- **Store**: JSON documents stored with custom namespaces
- **Namespace + Key**: Hierarchical organization (user_id, memory_type)
- **Cross-thread Access**: Available across all user sessions
- **User-specific Data**: Perfect for user profiles, preferences, and PRDs

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Alice    │    │  LangGraph Agent │    │   User Bob      │
│                 │    │                  │    │                 │
│ Thread: alice_001│───▶│  Thread Manager │───▶│ Thread: bob_001 │
│ Memory: alice/* │    │                  │    │ Memory: bob/*   │
└─────────────────┘    │  Store:          │    └─────────────────┘
                       │  - (alice, prd)  │
                       │  - (bob, prd)    │
                       │  - (alice, pref) │
                       │  - (bob, pref)   │
                       └──────────────────┘
```

## Implementation Features

### ✅ Automatic Session Isolation
- Each user gets their own thread: `{user_id}_{session_id}`
- Conversation history automatically isolated per thread
- No manual session management required

### ✅ User-specific Long-term Memory
- PRDs stored with user-specific namespaces: `(user_id, "prd")`
- User preferences and profiles isolated by namespace
- Cross-session data persistence

### ✅ Built-in Persistence
- Checkpointer handles conversation state
- Store manages long-term user data
- Automatic state recovery on restart

### ✅ Scalable Architecture
- No shared global state
- Thread-safe operations
- Horizontal scaling support

## Usage Examples

### Starting a User Session
```python
config = {
    "configurable": {
        "thread_id": "alice_session_001",
        "user_id": "alice"
    }
}

result = await graph.ainvoke({
    "messages": [HumanMessage(content="Generate PRD for authentication")],
    "memory": [],
    "user_id": "alice",
    "session_id": "session_001"
}, config=config)
```

### Continuing a Session
```python
# Get current state
current_state = await graph.aget_state(config)

# Continue conversation
result = await graph.ainvoke({
    "messages": current_state.values["messages"] + [new_message],
    "memory": current_state.values.get("memory", []),
    "user_id": "alice",
    "session_id": "session_001"
}, config=config)
```

### Accessing User-specific Data
```python
# Store user PRD
namespace = ("alice", "prd")
store.put(namespace, "auth_feature", prd_data)

# Retrieve user PRD
item = store.get(namespace, "auth_feature")
```

## Benefits Over Manual Implementation

### ❌ Previous Approach (Manual Database)
- Manual user ID management
- Complex SQL queries for isolation
- Risk of data leakage
- Manual session cleanup
- Difficult to scale

### ✅ LangGraph Native Approach
- Automatic thread isolation
- Built-in state management
- Declarative configuration
- Automatic persistence
- Built-in scalability

## Running the Demo

```bash
cd /home/zeihanaulia/langchain-academy/module-7/studio
python multi_user_demo.py
```

## Key Takeaways

1. **Leverage LangGraph's Built-in Features**: Don't reinvent session management
2. **Use Threads for Conversation Isolation**: Automatic per-user conversation separation
3. **Use Store for Long-term Memory**: Namespace-based user data isolation
4. **Configure Properly**: Use `configurable` with `thread_id` and custom user context
5. **Scale Naturally**: LangGraph handles concurrency and persistence automatically

## Migration Path

If you have existing user data in a custom database:

1. **Export existing data** from your current database
2. **Import to LangGraph Store** using user-specific namespaces
3. **Update your application** to use LangGraph's session management
4. **Test thoroughly** with multi-user scenarios
5. **Gradually phase out** the old database

This approach provides **enterprise-grade multi-user support** with minimal code complexity, leveraging LangGraph's battle-tested architecture for session management and data isolation.
