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



agents.py

This file offers the class in order to implement a Multi-Armed Bandit (MAB) agent based on the foundational concepts from Sutto and Barto ( specifically the e-greedy method). It is designed to balance exploring new network channels versus exploiting the best-known one to maximize throughput.

__init__ 
This configures agent's parameters. Notably, it initializes self.values to 500 for all arms. In sutto and barto terms, this is called Optimistic Initial Values, which encourages exploration early on because the actual rewards will likely be lower than this high starting estimate. The other values are initiualized as they are given from the file run.py

get_estimated_values 
A simpler getter function that returns the agent's current internal belief (Q-values) for each channel's (or relay's) performance

select_arm
This function makes the decision. It implements the e-greedy logic
With probability e, it chooses an arm at random (Exploration)
With probability 1-e, it chooses the arm with the highest estimated value (Exploitation)

update 
Adjusts the agent's knowledge after receiving a reward ( The Data rate\Throughput) from the environment. It supports two mathematical approaches mentioned on Sutto and Barto. (We currently use the second one as it fits our environment better)

📐 Formulas (Sutton & Barto)Both update rules in your code follow the General Update Form described by Sutton and Barto:$$NewEstimate = OldEstimate + StepSize [Target - OldEstimate]$$Rule 1: Incremental Uniform AverageUsed for stationary problems where the reward distribution doesn't change over time. The step size $\alpha$ is dynamic and equals $1/n$.$$Q_{n+1} = Q_n + \frac{1}{n} [R_n - Q_n]$$$Q_n$: Current estimate.$R_n$: The reward (throughput) just received.$n$: The number of times this specific arm has been pulled.Rule 2: Exponential Smoothing (Constant Step-Size)Used for non-stationary problems (like real networks where traffic fluctuates). It gives more weight to recent rewards than old ones.$$Q_{n+1} = Q_n + \alpha [R_n - Q_n]$$$\alpha$: A constant parameter (your self.alpha = 0.5).This results in a weighted average where the influence of past rewards decays exponentially at a rate of $(1-\alpha)^n$.




