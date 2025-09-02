# Deep Research Tool - Usage Examples

## Example Conversations with the Brainstorming Agent

### Example 1: Basic Deep Research Request
```
User: Can you do deep research on the latest developments in quantum computing?

Agent: I'll perform a comprehensive deep research on quantum computing developments. Let me analyze multiple sources and verify the information.

🔬 DEEP RESEARCH RESULTS for: 'latest developments in quantum computing'
📊 Found 5 valid sources

Source 1: Quantum Computing Breakthroughs 2024
🔗 URL: https://example.com/quantum-2024
🏢 Domain: example.com
📖 EXTRACTED CONTENT: Recent breakthroughs include...

[Additional sources and synthesis...]
```

### Example 2: Technical Research with Depth Specification
```
User: I need thorough research on machine learning applications in autonomous vehicles, please use deep analysis.

Agent: I'll conduct deep research on ML applications in autonomous vehicles with comprehensive analysis.

🔬 DEEP RESEARCH RESULTS for: 'machine learning applications in autonomous vehicles'
📊 Found 5 valid sources

[Deep analysis with content extraction from 5 sources...]

🎯 RESEARCH SYNTHESIS
🌐 Sources from 4 unique domains: arxiv.org, nature.com, ieee.org, mit.edu
⭐ Quality Rating: High (avg relevance: 8.2)
💡 RECOMMENDATIONS: Multiple reliable sources found - information appears comprehensive
```

### Example 3: Market Research Scenario
```
User: Do comprehensive research on the competitive landscape for fintech payment solutions.

Agent: I'll perform deep research on the fintech payment solutions competitive landscape.

🔬 DEEP RESEARCH RESULTS for: 'competitive landscape for fintech payment solutions'
📊 Found 5 valid sources

[Analysis of market leaders, emerging players, regulatory factors...]

🎯 RESEARCH SYNTHESIS
🌐 Sources from 5 unique domains: cbinsights.com, statista.com, crunchbase.com, forrester.com, mckinsey.com
⭐ Quality Rating: High (avg relevance: 9.1)
💡 RECOMMENDATIONS: Excellent source diversity - comprehensive market view
```

### Example 4: Quick Research (Shallow Depth)
```
User: Quick research on sustainable energy trends.

Agent: I'll do shallow research on sustainable energy trends for a fast overview.

🔬 DEEP RESEARCH RESULTS for: 'sustainable energy trends'
📊 Found 2 valid sources

[Fast analysis with 2 key sources...]

🎯 RESEARCH SYNTHESIS
🌐 Sources from 2 unique domains: iea.org, reuters.com
⭐ Quality Rating: Medium (avg relevance: 6.8)
💡 RECOMMENDATIONS: Good coverage for overview - consider medium depth for more detail
```

## Command-Line Testing Examples

### Test the Tool Structure
```bash
cd /home/zeihanaulia/langchain-academy/module-7/studio
source ../../.venv/bin/activate
python -c "
from brainstorming_agent import deep_research
print('Tool available:', deep_research.__name__)
print('Parameters:', list(deep_research.__code__.co_varnames[:deep_research.__code__.co_argcount]))
"
```

### Test with Mock Data
```python
# Example of how the tool processes results
from brainstorming_agent import deep_research

# This would normally call Tavily API
# For testing, you can see the processing logic
print("Deep research tool is ready for use in LangGraph Studio!")
```

## Integration Examples

### With Memory Management
```
User: Research AI ethics frameworks and save the key findings to memory.

Agent: I'll research AI ethics frameworks and save the key findings.

[Deep research results...]

✅ Saved key findings about AI ethics frameworks to memory.
```

### With File Operations
```
User: Do deep research on blockchain scalability solutions and save the report to a file.

Agent: I'll research blockchain scalability and create a comprehensive report.

[Deep research results...]

✅ Research report saved to: blockchain_scalability_research.md
```

### With PRD Generation
```
User: Research user authentication trends and generate a PRD for our new auth system.

Agent: I'll research authentication trends and generate a comprehensive PRD.

[Deep research on auth trends...]

✅ PRD generated: user_authentication_system_prd.md
```

## Error Handling Examples

### Network Issues
```
User: Deep research on [topic]

Agent: ❌ Deep research failed: Connection timeout
💡 Try using the basic browse_web tool instead.
```

### Invalid Query
```
User: Deep research on [empty query]

Agent: ❌ Deep research failed: No information found for the query.
💡 Try broadening your search terms.
```

### API Issues
```
User: Deep research on [topic]

Agent: ❌ Deep research failed: Tavily API error
💡 Check your TAVILY_API_KEY configuration.
```

## Performance Comparison

| Scenario | browse_web | deep_research (shallow) | deep_research (deep) |
|----------|------------|-------------------------|----------------------|
| Speed | ~2-3 seconds | ~5-8 seconds | ~15-25 seconds |
| Sources | 3 | 2 | 5 |
| Content Depth | Summary | Extracted content | Full extraction |
| Verification | None | Basic | Comprehensive |
| Synthesis | None | Basic | Advanced |

## Best Practices for Users

### When to Request Deep Research
- Complex technical topics
- Market analysis
- Competitive research
- Regulatory compliance
- Academic or scientific subjects
- Business strategy decisions

### How to Phrase Requests
✅ Good:
- "Do deep research on quantum computing breakthroughs"
- "Perform comprehensive analysis of AI in healthcare"
- "Thorough research on sustainable energy solutions"

❌ Avoid:
- "Search for quantum computing" (too vague)
- "Find information about AI" (too broad)
- "Research everything" (too general)

### Depth Selection Tips
- **Shallow**: Quick answers, time-sensitive
- **Medium**: Most research tasks
- **Deep**: Critical business decisions, comprehensive analysis

## Troubleshooting

### Common Issues
1. **Slow Response**: Deep research takes longer - this is normal
2. **API Errors**: Check TAVILY_API_KEY environment variable
3. **No Results**: Try different keywords or broader search terms
4. **Timeout**: Some sources may be slow - tool handles this automatically

### Getting Help
- Check the tool's error messages for specific guidance
- Use basic `browse_web` tool for quick searches
- Review the synthesis section for quality assessment
