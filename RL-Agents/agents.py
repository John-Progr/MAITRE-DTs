import numpy as np


class EpsilonGreedy:

    
    def __init__(self, n_arms, epsilon, update_rule, alpha):
        self.n_arms = n_arms 
        self.epsilon = epsilon
        self.update_rule = update_rule
        self.alpha = alpha
        self.counts = np.zeros(n_arms)   # Number of times each arm is pulled, basically how often each channel is used 
        self.values = np.full(n_arms, 500)
        #self.values = np.zeros(n_arms) # Estimated values of each arm, basically estimated throughput per channel
        #np.random.seed()  # fixed seed





    def get_estimated_values(self):
        """
        Returns the current estimated action values (Q-values) for all arms.
        """
        return self.values


    def select_arm(self):
        """Choose an arm (explore or exploit)."""
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.n_arms)   # Explore
        else:
            return np.argmax(self.values)           # Exploit best so far

    def update(self, chosen_arm, reward):
        """Update estimated value of the chosen arm using incremental mean."""
        self.counts[chosen_arm] += 1
        n = self.counts[chosen_arm]
        value = self.values[chosen_arm]
        print(f"chosen_arm = {chosen_arm}")
        print(f"n = {n}")
        print(f"value = {value}")




        if self.update_rule == "incremental":

            # This is the incremental update rule of shutton and burton book
            # they prove this and the general form is 
            # NewEstimate = OldEstimate + StepSize[Target-OldEstimate]
            # step size denoted by at(a), a = 1/k (in a more informal way)
            
            self.values[chosen_arm] = value + (reward - value) / n

        elif self.update_rule == "exponential_smoothing":
            self.values[chosen_arm] = value + self.alpha *(reward-value)
            something = self.values[chosen_arm]
            print(f"value after update = {something}")
 

        else:
            raise ValueError("update_rule must be 'incremental' or 'exponential_smoothing'")


