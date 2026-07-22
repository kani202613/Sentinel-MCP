# ETHICS

**Date:** 2026-07-22

## Attack Patterns
This project ships attack patterns reconstructed from public CVEs and academic papers. There is **no zero-day material** included in this repository. Under no circumstances do any attacks or red-teaming scripts touch third-party production systems. All experiments are confined to local or strictly isolated sandbox environments.

## Synthetic Datasets and Red-Teaming
ToolTrace relies on synthetic datasets (Set A and Set B) generated via rigorous red-teaming methodologies. These sets are designed to simulate malicious actor behavior and test the Sentinel Risk Index (SRI) boundary. The generation of these datasets is strictly controlled and occurs in safe, ephemeral environments to ensure no real-world systems are harmed or inadvertently compromised.

## Data Handling and Redaction Policy
Before any data or log files are released publicly, a strict redaction policy is enforced:
1. All Personally Identifiable Information (PII) is scrubbed.
2. Proprietary paths, tokens, and internal network structures are obfuscated or replaced with dummy values.
3. Functional exploit code that could be weaponized against real-world targets is thoroughly sanitized to ensure it is rendered harmless (e.g., replacing actual payloads with benign strings or removing critical execution steps).
