# Model Context Protocol (MCP) - TransferEdu

## 1. What is MCP?

Model Context Protocol (MCP) is an open standard that allows developers to build secure, two-way connections between their data sources and AI models. It replaces fragmented integrations with a universal standard.

## 2. Core Architecture

- MCP Hosts: AI applications that initiate connections.
- MCP Clients: Maintain protocol-standard connections with servers.
- MCP Servers: Provide specialized data or tools (e.g., Google Drive, Slack, SQL DB).

## 3. Implementation for TransferEdu

For TransferEdu's Phase 2, MCP can simplify how the AI Assistant retrieves academic keywords and definitions from your SQL Database without needing custom RAG logic for every data type.