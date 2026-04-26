## RL Agent Folder

<p>
This folder contains the code that runs the RL agent.  
It consists of 9 files but not all of them are needed to run it.
</p>

---

## run.py

<div style="padding: 12px; border-left: 4px solid #2e7d32; background-color: #f5f5f5;">

In a general software project, run.py acts as the entry point used to initilize, configure, and execute the entire program. It serves as the "orchestrator" that brings together modular components  
In our case, the agent,environments, data loaders etc.

</div>

---

## Description

<p>
In a more specific wat run.py script sxecutes a loop of 200 iterations where an Epsilon- Greedy agents selects a wrieless channel (or a relay) and tests its  
performance via a network API (Agent doesn't need to know anything else). Thorugh this process, the agent uses exponential smoothing to learn which channel  
(or relay) provides the highest data transfer rate.
</p>

---

## agents.py

<p>
This file offers the class in order to implement a Multi-Armed Bandit (MAB) agent based on the foundational concepts from Sutto and Barto ( specifically the e-greedy method). It is designed to balance exploring new network channels versus exploiting the best-known one to maximize throughput.
</p>

---

### __init__

<p>
This configures agent's parameters. Notably, it initializes self.values to 500 for all arms. In sutto and barto terms, this is called Optimistic Initial Values, which encourages exploration early on because the actual rewards will likely be lower than this high starting estimate. The other values are initiualized as they are given from the file run.py
</p>

---

### get_estimated_values

<p>
A simpler getter function that returns the agent's current internal belief (Q-values) for each channel's (or relay's) performance
</p>

---

### select_arm

<p>
This function makes the decision. It implements the e-greedy logic
</p>

<p>
With probability e, it chooses an arm at random (Exploration)  
With probability 1-e, it chooses the arm with the highest estimated value (Exploitation)
</p>

---

### update

<p>
Adjusts the agent's knowledge after receiving a reward ( The Data rate\Throughput) from the environment. It supports two mathematical approaches mentioned on Sutto and Barto. (We currently use the second one as it fits our environment better)
</p>

---

### Formulas (Sutton & Barto)

<p>
Both update rules in your code follow the General Update Form described by Sutton and Barto:
</p>

$$NewEstimate = OldEstimate + StepSize [Target - OldEstimate]$$

---

#### Rule 1: Incremental Uniform Average

<p>
Used for stationary problems where the reward distribution doesn't change over time. The step size $\alpha$ is dynamic and equals $1/n$.
</p>

$$Q_{n+1} = Q_n + \frac{1}{n} [R_n - Q_n]$$

<p>
$Q_n$: Current estimate.  
$R_n$: The reward (throughput) just received.  
$n$: The number of times this specific arm has been pulled.
</p>

---

#### Rule 2: Exponential Smoothing (Constant Step-Size)

<p>
Used for non-stationary problems (like real networks where traffic fluctuates). It gives more weight to recent rewards than old ones.
</p>

$$Q_{n+1} = Q_n + \alpha [R_n - Q_n]$$

<p>
$\alpha$: A constant parameter (your self.alpha = 0.5).
</p>

<p>
This results in a weighted average where the influence of past rewards decays exponentially at a rate of $(1-\alpha)^n$.
</p>

---

## environments.py

<p>
This file offers the environment class for the reinforcement learning loop. They act as the interface between the Agent's mathematical decisions and the physical (or simulated) network performance.
</p>

---

### __init__

<p>
Initializes the network parameters. It stores the Source/Destination IPs and sets the reward_machine, which determines if the environment is a real testbed (fetch reward from an API like pulling a lever) or a simulation (using math distributions). Someone can implement using past measuerements from example in order to replay the experiment. That's a cool idea we has in mind.
</p>

---

### send_request

<p>
This is the networking engine. It sends a POST request to the reward_endpoint with a JSON payload containing the chosen channel or route. It includes a Retry Logic with Exponential Backoff:
</p>

<p>
If a request fails, it waits $delay \times 2^{(attempt-1)}$ seconds before trying again.This ensures the script doesn't crash if the network has a momentary "hiccup."
</p>

<p>
This is necessary as it is very sad to lose a measurement because an error occured somewhere, or server wasnt responding for some reason or raspberry pis are not responding due to dynamic settings. This respects the algorithm decision.
</p>

---

### get_reward

<p>
This maps the result of an action to a numerical value(the "Reward"). Depending on the reward_machine value, it calculates the reward differently.
</p>

<p>
0(Live API): calls send_request to get the actual data rate (rate_mbps)  
1 and 2 (Simulated) : Generates random throughput values based on statistical distributions. (Very useful for testing the algorithm before moving to production)(Also not bad the measurements weren't so off but nothing like the wireless network randomness)  
3 (Historical) : Pulls the next value from a csv file ( The cool idea)  
4 (Static): Returns a constant value of 10 (We had somehow to confirm everything is working perfectly, and this was the way)
</p>

---

<p>
These classes serve as the Environment in your Reinforcement Learning loop. They act as the interface between the Agent's mathematical decisions and the physical (or simulated) network performance.
</p>

---

### Function Descriptions

#### 1. __init__ (The Setup)

<p>
Initializes the network parameters. It stores the Source/Destination IPs and sets the reward_machine, which determines if the environment is a real testbed (connected via API) or a simulation (using math distributions).
</p>

---

#### 2. send_request (The Communicator)

<p>
This is the networking engine. It sends a POST request to the reward_endpoint with a JSON payload containing the chosen channel or route. It includes a Retry Logic with Exponential Backoff:
</p>

<p>
If a request fails, it waits $delay \times 2^{(attempt-1)}$ seconds before trying again.This ensures the script doesn't crash if the network has a momentary "hiccup."
</p>

---

#### 3. get_reward (The Evaluator)

<p>
This maps the result of an action to a numerical value (the "Reward"). Depending on the reward_machine value, it calculates the reward differently:
</p>

<p>
0 (Live API): Calls send_request to get the actual rate_mbps.  
1 & 2 (Simulated): Generates random throughput values based on statistical distributions.  
3 (Historical): Pulls the next value from a CSV file.  
4 (Static): Returns a constant value of 10.
</p>

---

### Mathematical Reward Models

<p>
Your code uses two specific distributions to simulate network noise when not using the real API:
</p>

---

#### Rayleigh Distribution (reward_machine == 1)

<p>
Often used to model fading in wireless signals where there is no dominant line-of-sight.
</p>

$$f(x; \sigma) = \frac{x}{\sigma^2} e^{-x^2 / (2\sigma^2)}, \quad x \ge 0$$

<p>
In your code: np.random.rayleigh(scale=5.0) + 5.  
This creates a reward that is mostly low but occasionally has higher spikes.
</p>

---

#### Normal (Gaussian) Distribution (reward_machine == 2)

<p>
Models standard background noise or consistent traffic interference.
</p>

$$f(x \mid \mu, \sigma^2) = \frac{1}{\sqrt{2\pi\sigma^2}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$$

<p>
In your code: loc=22.5 ($\mu$) and scale=5 ($\sigma$).  
This creates a predictable bell curve of throughput centered around 22.5 Mbps.
</p>

---

## experiments.py

<p>
The Experiment class is the actual experiment. It initializes the ExperimentLogger ( Which is very useful) with a timestamped name and creates placeholders for various Matplotlib figures. This ensures every run is uniquely identifiable for later analysis.
</p>

---

<p>
Basically experimentlogger records the data from every trial.
</p>

<p>
Apart from the initialization part, we use it when the logger's log_step function is called at the end of every iteration. This captures a snapshot of the agent's performance and internal state.
</p>

---

### run(n_trials)

<p>
This is the core loop. For each trial, it:
</p>

<p>
Selects an Action: Asks the agent for an arm (channel or device).  
Interacts: Calls env.get_reward() to get the throughput.  
Learns: Updates the agent’s internal Q-values based on that reward.  
Visualizes: Triggers the live plot updates so you can see the learning happen in real-time.
</p>

---

### plot() & plot_avg_reward_per_arm_over_time()

<p>
These are post-experiment analysis tools. They generate static, high-quality "ggplot" style charts showing the cumulative average reward and a comparative bar chart of which channel performed best overall.
</p>

---

### update_live_main_plot()

<p>
Creates a dynamic dashboard during the run. It clears and redraws the main figure to show:
</p>

<p>
Top Plot: The running average of rewards (cumulative throughput).  
Bottom Plot: A bar chart comparing the performance of all arms.  
Subtitle: A live "Best Estimated" indicator showing which choice the agent currently favors.
</p>

---

### update_live_arm_plots() & _for_each()

<p>
These track the Learning Curve (Q-values) for every individual arm.
</p>

<p>
They implement a "Zoom Fix": because the agent starts with an optimistic value (500) and the rewards are much lower (15-40), the plot automatically ignores the initial "drop" to focus on the stabilized learning range.
</p>

<p>
The _for_each version spawns independent windows for every channel, allowing you to monitor each frequency's stability separately.
</p>

---

### Formulas and Logic (Sutton & Barto)

<p>
The class calculates and visualizes the Sample-Average Method to show how well the agent is doing compared to its history:
</p>

---

#### Cumulative Average Reward

<p>
At each step $t$, the "Average Reward vs Steps" plot calculates:
</p>

$$\text{Average Reward}_t = \frac{1}{t} \sum_{i=1}^{t} R_i$$

<p>
This is the standard metric in Sutton and Barto to check if the agent is converging. If the line trends upward and levels off, the agent has successfully identified the best channel.
</p>

---

#### Q-Value History (The Learning Curve)

<p>
The individual arm plots visualize the internal state of the Agent's memory:
</p>

$$Q_t(a) \approx \mathbb{E}[R_t \mid A_t = a]$$

<p>
By plotting these over time, you can see the Optimistic Initial Value effect: the value starts high (500), drops sharply upon the first sample, and then uses your Exponential Smoothing formula to settle on the true mean of the network's throughput.
</p>

---

## experiments.py

<p>
This file offers the ExperimentLogger class which is basically the archivist of our project . Its primary role is to ensure that every decision made by the agent and every response from the network is permanently recorded for auditing, debugging and post-run analysis
</p>

---

### __init__

<p>
This method
</p>

<p>
1. creates an experiments\ directory and a specific sub-folder named after our current run (using the aforementioned timestamp)  
2. It initializes a steps.csv file and writes the header row, defining the strcuture of our data bank.
</p>

---

### log_step

<p>
This is called at the end of every trial in Experiment.run(). It performs the heavy lifting of data serialization.
</p>

<p>
1.It uses json.dumps(q_values.tolist()) to turn the array into a text string, since q_values is a NumPy array which csvs can't store drectly  
2.And appends a new line without overwiritng previous results, ensuring our data grows as the experiment progresses.
</p>

---

## replay.py

<p>
This basically replays the experiment as it was performed in order to make the visualization as someone desires, or experiment with different insights and statistics.  
It transforms the logged CSV files into visual proof of the agent's learning efficiency.
</p>

---

<p>
At first, the scripts reads the step.csv file generated by the ExperimentLogger. Because the Q-values were stored as JSON strings to fit in the CSV, it uses json.loads to convert them back into Python lists so they can be plotted.
</p>

---

<p>
It doesn't differentiate much from the live plots.
</p>

---

<p>
It offers The Cummulative Average visualization.
</p>

<p>
The plot calculates the running mean of all rewards .
</p>

---

<p>
It offers the Bar chart
</p>

<p>
Which groups the data by arm_label ( Channel or relay) and calculates the mean throughput for each.  
This is not useful to the algorithm, it just gives a general view of each channel and relay as individuals. Also it is not a very high fidelity view as a channel might not be picked each trial so it skips a lot of measurements.
</p>

---

<p>
The most important visualization is the Q-Learning Curves
</p>

---

<p>
These plots show the Q-Values over time
</p>

<p>
We have a combined plot which allows you to see the competition between arms. You observe as the best arm's Q-values rises above the others and it is extremely useful when making experimnets like making a channel interference as mentioned in the paper.
</p>

<p>
Indifivdual plots as well which focuses on the stability of a single arm. It highlights the Optimistic initial value drop (fro tnmeh starting 500) and the subsequent convergence to the try network speed. ( it won't actually converge but the number will appear to be closer each time to the data rate performance)
</p>

---

<p>
This script is the Post-Processor or Analyzer. While your previous files focused on generating data, this one focuses on interpreting it. It uses Pandas and Matplotlib to transform the logged CSV files into visual proof of the agent's learning efficiency.
</p>

---

### Functionality Breakdown

#### 1. Data Loading & Serialization Fix

<p>
The script reads the steps.csv file generated by the ExperimentLogger. Because the $Q$-values were stored as JSON strings to fit in the CSV, it uses json.loads to convert them back into Python lists so they can be plotted.
</p>

---

#### 2. Visualization 1: Cumulative Average (The "Profit" View)

<p>
This plot calculates the running mean of all rewards.
</p>

<p>
Purpose: In Sutton and Barto's research, this is the primary way to measure Regret.
</p>

<p>
Insight: An upward-sloping and then stabilizing curve proves the agent is moving away from random guessing (exploration) and successfully identifying high-throughput channels (exploitation).
</p>

---

#### 3. Visualization 2: Bar Chart (The "Ranking" View)

<p>
This groups the data by arm_label and calculates the mean throughput for each.
</p>

<p>
Purpose: It provides a "Final Standings" look at which network device or channel actually performed the best over the 200 trials.
</p>

---

#### 4. Visualization 3 & 4: Q-Value Learning Curves (The "Brain" View)

<p>
These plots show the $Q$-values (the agent's internal estimates) over time.
</p>

<p>
Combined Plot: Allows you to see the "competition" between arms—you can watch as the best arm's $Q$-value rises above the others.
</p>

<p>
Individual Plots: Focuses on the stability of a single arm. It highlights the Optimistic Initial Value drop (from the starting 500) and the subsequent convergence to the true network speed.
</p>

---

### Formulas and Logic (Sutton & Barto)

<p>
This script specifically visualizes the transition from Initial Estimates to Converged Beliefs.
</p>

---

#### The Learning Curve Formula

<p>
The points plotted on the Y-axis of the $Q$-value charts represent the result of the agent's update rule that you defined earlier:
</p>

$$Q_{n+1}(a) = Q_n(a) + \alpha [R_n - Q_n(a)]$$

<p>
By plotting this, the script allows you to verify that the Step Size ($\alpha$) is appropriate. If the line is too "jittery," $\alpha$ is too high; if it's too flat, $\alpha$ is too low.
</p>

---

#### Mean Reward per Arm

<p>
For the bar charts, the script calculates the simple arithmetic mean of all rewards received for that specific action $a$:
</p>

$$\bar{R}(a) = \frac{\sum \text{Rewards obtained from arm } a}{\text{Number of times arm } a \text{ was chosen}}$$
