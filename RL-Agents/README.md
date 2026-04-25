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



## agents.py

This file offers the class in order to implement a Multi-Armed Bandit (MAB) agent based on the foundational concepts from Sutto and Barto ( specifically the e-greedy method). It is designed to balance exploring new network channels versus exploiting the best-known one to maximize throughput.

---

### __init__ 

This configures agent's parameters. Notably, it initializes self.values to 500 for all arms. In sutto and barto terms, this is called Optimistic Initial Values, which encourages exploration early on because the actual rewards will likely be lower than this high starting estimate. The other values are initiualized as they are given from the file run.py

---

### get_estimated_values 

A simpler getter function that returns the agent's current internal belief (Q-values) for each channel's (or relay's) performance

---

### select_arm

This function makes the decision. It implements the e-greedy logic

With probability e, it chooses an arm at random (Exploration)  
With probability 1-e, it chooses the arm with the highest estimated value (Exploitation)

---

### update 

Adjusts the agent's knowledge after receiving a reward ( The Data rate\Throughput) from the environment. It supports two mathematical approaches mentioned on Sutto and Barto. (We currently use the second one as it fits our environment better)

---

### 📐 Formulas (Sutton & Barto)

Both update rules in your code follow the General Update Form described by Sutton and Barto:

$$NewEstimate = OldEstimate + StepSize [Target - OldEstimate]$$

#### Rule 1: Incremental Uniform Average

Used for stationary problems where the reward distribution doesn't change over time. The step size $\alpha$ is dynamic and equals $1/n$.

$$Q_{n+1} = Q_n + \frac{1}{n} [R_n - Q_n]$$

$Q_n$: Current estimate.  
$R_n$: The reward (throughput) just received.  
$n$: The number of times this specific arm has been pulled.

---

#### Rule 2: Exponential Smoothing (Constant Step-Size)

Used for non-stationary problems (like real networks where traffic fluctuates). It gives more weight to recent rewards than old ones.

$$Q_{n+1} = Q_n + \alpha [R_n - Q_n]$$

$\alpha$: A constant parameter (your self.alpha = 0.5).

This results in a weighted average where the influence of past rewards decays exponentially at a rate of $(1-\alpha)^n$.



## environments.py

This file offers the environment class for the reinforcement learning loop. They act as the interface between the Agent's mathematical decisions and the physical (or simulated) network performance.

---

### __init__

Initializes the network parameters. It stores the Source/Destination IPs and sets the reward_machine, which determines if the environment is a real testbed (fetch reward from an API like pulling a lever) or a simulation (using math distributions). Someone can implement using past measuerements from example in order to replay the experiment. That's a cool idea we has in mind.

---

### send_request

This is the networking engine. It sends a POST request to the reward_endpoint with a JSON payload containing the chosen channel or route. It includes a Retry Logic with Exponential Backoff:  

If a request fails, it waits $delay \times 2^{(attempt-1)}$ seconds before trying again.This ensures the script doesn't crash if the network has a momentary "hiccup."  

This is necessary as it is very sad to lose a measurement because an error occured somewhere, or server wasnt responding for some reason or raspberry pis are not responding due to dynamic settings. This respects the algorithm decision.

---

### get_reward

This maps the result of an action to a numerical value(the "Reward"). Depending on the reward_machine value, it calculates the reward differently.

0(Live API): calls send_request to get the actual data rate (rate_mbps)  
1 and 2 (Simulated) : Generates random throughput values based on statistical distributions. (Very useful for testing the algorithm before moving to production)(Also not bad the measurements weren't so off but nothing like the wireless network randomness)  
3 (Historical) : Pulls the next value from a csv file ( The cool idea)  
4 (Static): Returns a constant value of 10 (We had somehow to confirm everything is working perfectly, and this was the way)

---

These classes serve as the Environment in your Reinforcement Learning loop. They act as the interface between the Agent's mathematical decisions and the physical (or simulated) network performance.

---

🛠️ Function Descriptions

#### 1. __init__ (The Setup)

Initializes the network parameters. It stores the Source/Destination IPs and sets the reward_machine, which determines if the environment is a real testbed (connected via API) or a simulation (using math distributions).

#### 2. send_request (The Communicator)

This is the networking engine. It sends a POST request to the reward_endpoint with a JSON payload containing the chosen channel or route. It includes a Retry Logic with Exponential Backoff:  

If a request fails, it waits $delay \times 2^{(attempt-1)}$ seconds before trying again.This ensures the script doesn't crash if the network has a momentary "hiccup."

#### 3. get_reward (The Evaluator)

This maps the result of an action to a numerical value (the "Reward"). Depending on the reward_machine value, it calculates the reward differently:

0 (Live API): Calls send_request to get the actual rate_mbps.  
1 & 2 (Simulated): Generates random throughput values based on statistical distributions.  
3 (Historical): Pulls the next value from a CSV file.  
4 (Static): Returns a constant value of 10.

---

📐 Mathematical Reward Models

Your code uses two specific distributions to simulate network noise when not using the real API:

#### Rayleigh Distribution (reward_machine == 1)

Often used to model fading in wireless signals where there is no dominant line-of-sight.

$$f(x; \sigma) = \frac{x}{\sigma^2} e^{-x^2 / (2\sigma^2)}, \quad x \ge 0$$

In your code: np.random.rayleigh(scale=5.0) + 5.  
This creates a reward that is mostly low but occasionally has higher spikes.

---

#### Normal (Gaussian) Distribution (reward_machine == 2)

Models standard background noise or consistent traffic interference.

$$f(x \mid \mu, \sigma^2) = \frac{1}{\sqrt{2\pi\sigma^2}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$$

In your code: loc=22.5 ($\mu$) and scale=5 ($\sigma$).  
This creates a predictable bell curve of throughput centered around 22.5 Mbps.



