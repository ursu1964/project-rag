
# ProjectRAG Master Plan - Part 5
# Physical Architecture and Deployment Engineering

## Volume AF - Physical Architecture

### Current Platform

Ubuntu Linux 24.x

Hardware:

- 32 GB RAM
- 1 TB HDD
- 4 GB GPU

### Recommended Resource Allocation

Ubuntu:
4 GB

PostgreSQL:
4 GB

GraphDB:
4 GB

Ollama:
12–16 GB

FastAPI + LangGraph:
2 GB

Cache and OS:
remaining memory

---

## Volume AG - Filesystem Layout

Recommended:

/home/RAG/

Structure:

/home/RAG/docs
/home/RAG/data
/home/RAG/backups
/home/RAG/project-rag
/home/RAG/models
/home/RAG/logs

Purpose:

Clear operational separation.

---

## Volume AH - Docker Architecture

Containers:

projectrag-postgres
projectrag-graphdb
projectrag-api

Future:

projectrag-monitoring
projectrag-worker
projectrag-grafana

---

## Volume AI - Network Architecture

Ports:

8000 FastAPI

5432 PostgreSQL

7200 GraphDB

11434 Ollama

Rule:

Expose only required services.

---

## Volume AJ - PostgreSQL Capacity Planning

Expected Growth

Documents:
1000+

Chunks:
100000+

Embeddings:
100000+

Recommendation:

Use pgvector indexes.

---

## Volume AK - GraphDB Capacity Planning

Store:

Entities
Relationships
Ontology

Expected Growth:

Millions of triples.

Recommendation:

Separate repositories later.

---

## Volume AL - Ollama Model Management

Model Lifecycle

Development:
phi3

Testing:
qwen2.5:7b

Production Prototype:
llama3.1:8b

Embedding:
nomic-embed-text

---

## Volume AM - Backup Strategy

PostgreSQL

Daily dump

GraphDB

Daily export

Project Files

GitHub

Documents

External storage

---

## Volume AN - Disaster Recovery

Recovery Objectives

RPO:
24 hours

RTO:
4 hours

---

Recovery Sequence

Restore PostgreSQL

Restore GraphDB

Restore Documents

Restore Application

Validate

---

## Volume AO - Logging Architecture

Application Logs

FastAPI

Agent Logs

LangGraph

Database Logs

PostgreSQL

Graph Logs

GraphDB

---

## Volume AP - Monitoring Architecture

Metrics

CPU
Memory
Disk
Latency
Tokens

Tools

Prometheus

Grafana

OpenTelemetry

---

## Volume AQ - GitHub Actions

Future Pipeline

Lint

Unit Tests

Integration Tests

Security Scan

Docker Build

---

## Volume AR - Security Hardening

Ubuntu

Automatic updates

Firewall

UFW

SSH Key Authentication

Fail2Ban

---

## Volume AS - Development Workflow

Feature Branch

Implementation

Testing

Review

Merge

---

## Volume AT - Release Workflow

Development

Staging

Production

---

## Volume AU - Local to Server Migration

Phase 1

Laptop

Phase 2

Dedicated Server

Phase 3

Multi-node Environment

---

## Volume AV - Scaling Strategy

Scale Retrieval

Scale GraphDB

Scale Agents

Scale Reasoning

Scale Storage

---

## Volume AW - Future Kubernetes Design

Components

API

Workers

PostgreSQL

GraphDB

Vector Services

Monitoring

---

## Volume AX - Hardware Sizing

Prototype

32 GB RAM

Recommended Server

64 GB RAM

Enterprise

128–256 GB RAM

---

## Volume AY - Performance Engineering

Targets

API < 1 sec

Retrieval < 500 ms

Graph Query < 500 ms

Reasoning < 5 sec

---

## Volume AZ - Operational Runbook

Daily

Check containers

Check logs

Check backups

Weekly

Review metrics

Review ingestion

Monthly

Capacity review

Security review

---

## Volume BA - Final Enterprise Vision

ProjectRAG becomes:

Knowledge Platform

GraphRAG Engine

Memory Platform

Topology Intelligence Platform

Infrastructure Analysis System

DevOps AI Assistant

Agent Execution Platform

This volume completes the physical deployment and operational architecture.
