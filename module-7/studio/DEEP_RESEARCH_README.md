# Deep Research Tool Documentation

## Overview
The `deep_research` tool is an advanced research capability that performs thorough, multi-step web research with content verification and synthesis. Unlike the basic `browse_web` tool that provides quick results, `deep_research` offers comprehensive analysis with multiple verification steps.

## Key Features

### 🔍 **Multi-Step Research Process**
1. **Initial Search**: Broad search to gather diverse sources
2. **Source Analysis**: Validate URLs and analyze content quality
3. **Content Extraction**: Extract deeper content from valid sources
4. **Synthesis**: Combine findings with quality assessment
5. **Recommendations**: Provide insights on research quality

### 📊 **Research Depths**
- **Shallow**: Fast research (2 sources) - quick overview
- **Medium**: Balanced research (3 sources) - good coverage
- **Deep**: Thorough research (5 sources) - comprehensive analysis

### ✅ **Content Verification**
- URL validation and parsing
- Domain analysis
- Content relevance scoring
- Quality assessment
- Error handling for failed sources

## Usage Examples

### Basic Usage
```python
# Quick research
result = deep_research("latest trends in AI", depth="shallow")

# Balanced research
result = deep_research("machine learning applications in healthcare", depth="medium")

# Comprehensive research
result = deep_research("blockchain technology impact on finance", depth="deep")
```

### In LangGraph Studio
When chatting with the brainstorming agent, you can request deep research by using phrases like:
- "Perform deep research on [topic]"
- "Do thorough research about [subject]"
- "I need comprehensive analysis of [query]"
- "Research deeply: [your query]"

## Output Format

The tool provides structured output with:

### 📄 **Source Analysis**
```
🔬 DEEP RESEARCH RESULTS for: '[query]'
📊 Found X valid sources

Source 1: [Title]
🔗 URL: [URL]
🏢 Domain: [domain]
📖 EXTRACTED CONTENT: [content preview]
```

### 🎯 **Research Synthesis**
```
RESEARCH SYNTHESIS
Sources from X unique domains: [domain1, domain2, ...]
Quality Rating: [High/Medium/Low]
Recommendations: [insights]
```

## Advantages Over Basic Search

| Feature | browse_web | deep_research |
|---------|------------|---------------|
| Speed | ⚡ Fast | 🐌 Slower (but thorough) |
| Sources | 3 max | 2-5 (configurable) |
| Verification | ❌ None | ✅ URL + Content validation |
| Content Depth | 📄 Summary only | 📖 Extracted content |
| Synthesis | ❌ None | ✅ Quality assessment |
| Error Handling | Basic | Comprehensive |

## Best Practices

### When to Use Deep Research
- ✅ Complex or controversial topics
- ✅ When you need verified information
- ✅ Technical or specialized subjects
- ✅ When accuracy is critical
- ✅ Market research or competitive analysis

### When to Use Basic Browse
- ✅ Quick fact-checking
- ✅ Simple information lookup
- ✅ When speed is priority
- ✅ Casual browsing

### Depth Selection Guide
- **Shallow**: Quick overview, time-sensitive queries
- **Medium**: Most research tasks, balanced quality/speed
- **Deep**: Critical decisions, comprehensive analysis needed

## Technical Details

### Dependencies
- `tavily-python`: For web search
- `requests`: For content extraction
- `urllib.parse`: For URL validation
- `time`: For respectful delays
- `re`: For content cleaning

### Error Handling
- Graceful handling of invalid URLs
- Timeout management for slow sources
- Fallback to summary when extraction fails
- Comprehensive error reporting

### Performance Considerations
- Deep research takes longer due to content extraction
- Respectful delays between requests (0.5s for deep mode)
- Automatic timeout handling (10s per source)
- Memory-efficient processing

## Integration with Brainstorming Agent

The deep_research tool is fully integrated with the brainstorming agent and can be used alongside other tools:

- **Memory Management**: Research findings can be saved to memory
- **File Operations**: Research results can be saved to files
- **PRD Generation**: Research can inform product requirements
- **Conversational Flow**: Natural integration with chat interface

## Future Enhancements

Potential improvements for the deep_research tool:
- PDF document analysis
- Image content extraction
- Multi-language support
- Advanced relevance algorithms
- Integration with academic databases
- Real-time news monitoring
