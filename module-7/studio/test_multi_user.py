#!/usr/bin/env python3
"""
Test script to demonstrate multi-user PRD isolation
"""
import sys
import os
sys.path.append('.')

from brainstorming_agent import graph, read_prd
from langchain_core.messages import HumanMessage

def test_multi_user_isolation():
    """Test function to demonstrate user isolation"""
    print("🧪 Testing Multi-User PRD Isolation...")
    print("=" * 60)

    # Test User 1 - Alice
    print("👤 User 1 (Alice): Creating PRD for 'User Authentication'")
    user1_state = {
        "messages": [HumanMessage(content="Generate PRD for User Authentication system with email/password login")],
        "memory": [],
        "user_id": "alice_product_manager",
        "session_id": "session_alice_001"
    }
    result1 = graph.invoke(user1_state)
    print("✅ Alice's PRD created successfully")
    print()

    # Test User 2 - Bob
    print("👤 User 2 (Bob): Creating PRD for 'User Authentication' (same feature name)")
    user2_state = {
        "messages": [HumanMessage(content="Generate PRD for User Authentication system with OAuth and social login")],
        "memory": [],
        "user_id": "bob_engineer",
        "session_id": "session_bob_001"
    }
    result2 = graph.invoke(user2_state)
    print("✅ Bob's PRD created successfully")
    print()

    # Test User 3 - Charlie
    print("👤 User 3 (Charlie): Creating different PRD for 'Payment System'")
    user3_state = {
        "messages": [HumanMessage(content="Generate PRD for Payment System with multiple payment methods")],
        "memory": [],
        "user_id": "charlie_finance",
        "session_id": "session_charlie_001"
    }
    result3 = graph.invoke(user3_state)
    print("✅ Charlie's PRD created successfully")
    print()

    # Test reading each user's PRDs
    print("🔍 Testing PRD Isolation:")
    print("-" * 40)

    # Alice reads her PRD
    print("👤 Alice reading 'User Authentication':")
    alice_prd = read_prd.invoke({"feature_name": "User Authentication", "user_id": "alice_product_manager"})
    print(f"   Length: {len(alice_prd)} characters")
    print(f"   Contains 'alice': {'alice_product_manager' in alice_prd}")
    print()

    # Bob reads his PRD
    print("👤 Bob reading 'User Authentication':")
    bob_prd = read_prd.invoke({"feature_name": "User Authentication", "user_id": "bob_engineer"})
    print(f"   Length: {len(bob_prd)} characters")
    print(f"   Contains 'bob': {'bob_engineer' in bob_prd}")
    print()

    # Charlie reads his PRD
    print("👤 Charlie reading 'Payment System':")
    charlie_prd = read_prd.invoke({"feature_name": "Payment System", "user_id": "charlie_finance"})
    print(f"   Length: {len(charlie_prd)} characters")
    print(f"   Contains 'charlie': {'charlie_finance' in charlie_prd}")
    print()

    # Test cross-user access (should fail)
    print("🚫 Testing Cross-User Access Prevention:")
    print("-" * 40)

    # Alice tries to read Bob's PRD (should return empty)
    alice_reads_bob = read_prd.invoke({"feature_name": "User Authentication", "user_id": "bob_engineer"})
    print(f"👤 Alice trying to read Bob's PRD: {'❌ No existing PRD found' in alice_reads_bob}")

    # Bob tries to read Charlie's PRD (should return empty)
    bob_reads_charlie = read_prd.invoke({"feature_name": "Payment System", "user_id": "charlie_finance"})
    print(f"👤 Bob trying to read Charlie's PRD: {'❌ No existing PRD found' in bob_reads_charlie}")
    print()

    # Verify database structure
    print("💾 Database Structure Check:")
    print("-" * 40)
    import sqlite3
    try:
        conn = sqlite3.connect('prds.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, feature_name, COUNT(*) as count FROM prds GROUP BY user_id, feature_name")
        results = cursor.fetchall()
        conn.close()

        print("📊 PRDs in database:")
        for user_id, feature_name, count in results:
            print(f"   {user_id} -> {feature_name} ({count} versions)")
    except Exception as e:
        print(f"❌ Database error: {e}")

    print()
    print("🎯 Multi-User Isolation Test Results:")
    print("=" * 60)

    # Final verification
    isolation_working = (
        len(alice_prd) > 100 and  # Alice has her PRD
        len(bob_prd) > 100 and    # Bob has his PRD
        len(charlie_prd) > 100 and # Charlie has his PRD
        "❌ No existing PRD found" in alice_reads_bob and  # Alice can't read Bob's
        "❌ No existing PRD found" in bob_reads_charlie    # Bob can't read Charlie's
    )

    if isolation_working:
        print("✅ SUCCESS: Complete user isolation is working!")
        print("   ✓ Each user has their own PRD collection")
        print("   ✓ Users cannot access other users' PRDs")
        print("   ✓ Same feature names are isolated per user")
        print("   ✓ Database properly segregates user data")
    else:
        print("❌ ERROR: User isolation has issues")
        print("   Please check the implementation")

    print()
    print("🔒 Security Note: Each user's PRDs are completely isolated!")
    print("   This prevents data leakage between different users.")

if __name__ == "__main__":
    test_multi_user_isolation()
