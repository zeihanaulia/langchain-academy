# PRD Database Storage Tools - Quick Guide

## Overview
Brainstorming agent sekarang mendukung **4 opsi penyimpanan PRD** yang berbeda:

## 🗂️ Storage Options

### 1. **generate_prd** (Default - Markdown)
```python
# Save to markdown file
generate_prd("User Authentication", "Secure login system", "Add OAuth support")
```
- ✅ **File**: `prds/PRD_User_Authentication.md`
- ✅ **Format**: Human-readable markdown
- ✅ **Backup**: Easy to version control

### 2. **generate_prd_sqlite** (Database)
```python
# Save to SQLite database
generate_prd_sqlite("Payment Gateway", "Stripe integration", "Support multiple currencies")
```
- ✅ **File**: `prds.db` (SQLite database)
- ✅ **Features**: Structured queries, relationships
- ✅ **Performance**: Fast for read/write operations
- ✅ **Backup**: Single file backup

### 3. **generate_prd_json** (JSON Files)
```python
# Save to JSON file database
generate_prd_json("Analytics Dashboard", "User behavior tracking", "Real-time metrics")
```
- ✅ **Files**: `prds_json/feature_name.json`
- ✅ **Format**: Structured JSON with metadata
- ✅ **Flexibility**: Easy to parse and modify
- ✅ **Backup**: Individual file backups

### 4. **generate_prd_mongodb** (MongoDB)
```python
# Save to MongoDB
generate_prd_mongodb("AI Chatbot", "Conversational AI", "Natural language processing")
```
- ✅ **Database**: MongoDB collections
- ✅ **Features**: Document-based, scalable
- ✅ **Query**: Advanced querying capabilities
- ⚠️ **Requires**: `pip install pymongo`

## 💬 How to Use in Chat

### Basic Usage
```
User: Generate PRD for user notifications feature
Agent: I'll generate a PRD for the user notifications feature and save it to markdown.

✅ PRD generated and saved to prds/PRD_user_notifications.md
```

### Specify Storage Type
```
User: Create PRD for payment system and save to database
Agent: I'll generate a PRD for the payment system and save it to SQLite database.

✅ PRD saved in SQLite database for feature: Payment System
```

### Explicit Tool Selection
```
User: Generate PRD for analytics and save to JSON
Agent: I'll use the JSON storage option for the analytics PRD.

✅ PRD created in JSON database for feature: Analytics
```

## 🔍 Checking Stored PRDs

### SQLite Database
```bash
# Check SQLite database
sqlite3 prds.db
.schema prds
SELECT * FROM prds;
```

### JSON Files
```bash
# Check JSON files
ls prds_json/
cat prds_json/feature_name.json
```

### Markdown Files
```bash
# Check markdown files
ls prds/
cat prds/PRD_feature_name.md
```

## 📊 Comparison Table

| Feature | Markdown | SQLite | JSON | MongoDB |
|---------|----------|--------|------|---------|
| **File Type** | `.md` files | `.db` file | `.json` files | Database |
| **Readability** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Query Speed** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Backup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Version Control** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Scalability** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Setup Complexity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🚀 Best Practices

### When to Use Each Storage Type

#### Use **Markdown** (generate_prd) when:
- You want human-readable documentation
- Need easy version control integration
- Prefer simple file-based storage
- Documentation is primary goal

#### Use **SQLite** (generate_prd_sqlite) when:
- You need structured data queries
- Want fast read/write operations
- Prefer single-file database
- Need ACID compliance

#### Use **JSON** (generate_prd_json) when:
- You want structured data with metadata
- Need easy parsing by other systems
- Prefer file-based with JSON structure
- Want individual file backups

#### Use **MongoDB** (generate_prd_mongodb) when:
- You have large-scale requirements
- Need advanced querying capabilities
- Want document-based storage
- Have distributed system needs

## 🔧 Technical Details

### Database Schema (SQLite)
```sql
CREATE TABLE prds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_name TEXT UNIQUE,
    title TEXT,
    description TEXT,
    content TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### JSON Structure
```json
{
    "feature_name": "user_authentication",
    "title": "User Authentication",
    "description": "Secure login system",
    "content": "# PRD Content...",
    "created_at": "2025-09-01T12:00:00",
    "updated_at": "2025-09-01T12:00:00"
}
```

### Update Existing PRDs
All tools support updating existing PRDs:
```python
# Update existing PRD
generate_prd_sqlite("User Authentication", "Updated description", "New requirements", update_existing=True)
```

## 🎯 Quick Commands

### Generate PRD with different storages:
- **Markdown**: "Generate PRD for [feature]"
- **SQLite**: "Generate PRD for [feature] and save to database"
- **JSON**: "Generate PRD for [feature] and save to JSON"
- **MongoDB**: "Generate PRD for [feature] and save to MongoDB"

### Check existing PRDs:
- **Markdown**: Check `prds/` directory
- **SQLite**: Query `prds.db` database
- **JSON**: Check `prds_json/` directory
- **MongoDB**: Query MongoDB collections

Now you have full control over where your PRDs are stored! 🎉
