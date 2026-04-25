## RL Agent Folder

This folder contains the code that runs the RL agent.  
It consists of 9 files but not all of them are needed to run it.

---

## run.py

<div style="padding: 12px; border-left: 4px solid #2e7d32; background-color: #f5f5f5;">

In a general software project, run.py acts as the entry point used to initilize, configure, and execute the entire program. It serves as the "orchestrator" that brings together modular components  
In our case, the agent,environments, data loaders etc.

</div>

---

## Description

In a more specific wat run.py script sxecutes a loop of 200 iterations where an Epsilon- Greedy agents selects a wrieless channel (or a relay) and tests its  
performance via a network API (Agent doesn't need to know anything else). Thorugh this process, the agent uses exponential smoothing to learn which channel  
(or relay) provides the highest data transfer rate.
