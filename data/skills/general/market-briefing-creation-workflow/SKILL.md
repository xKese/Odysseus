---
name: market-briefing-creation-workflow
description: Market Briefing Creation Workflow
version: 1.0.0
category: general
tags: [briefing, market-analysis, research, document-creation, workflow]
status: published
confidence: 0.85
source: learned
owner: kese
created: "2026-06-20T17:46:40Z"
---

## When to Use

Need to create structured daily/weekly market briefings combining research data with a standard template for internal teams.

## Procedure

1. Trigger research with specific market topics, timeframes, and data points (prices, sectors, risks)
2. Wait for research completion notification from user or system
3. Read the completed research report using manage_research with the report ID
4. Create the briefing document using create_document with standard template structure
5. Include key findings, timestamps, target audience, and sourced data points

Use a three-step workflow: trigger deep research, read the research results, then create a formatted briefing document using the house template.
