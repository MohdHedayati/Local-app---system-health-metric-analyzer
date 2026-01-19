# AI Chatbot & RAG

## Purpose

The AI chatbot helps users:
- Understand performance issues
- Interpret reports
- Get OS-specific optimization advice

## RAG Strategy

- Base LLM handles reasoning
- OS-specific documents injected as context
- Separate knowledge bases for:
  - Windows
  - Ubuntu
  - Arch Linux

## Example Queries

- "Why is my CPU usage high on Windows?"
- "How do I optimize swap usage on Ubuntu?"
