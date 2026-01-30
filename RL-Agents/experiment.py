import numpy as np
import matplotlib.pyplot as plt
from logging_utils import save_to_csv
from datetime import datetime
import time
from ExperimentLogger import ExperimentLogger





# make the code correct with the correct classes and the correct names for the experiments plots in a next iteration


class Experiment:

    def __init__(self, agent, env, exptype):
        self.agent = agent
        self.env = env
        self.exptype = exptype
        self.rewards = []
        self.actions = []

        self.logger = ExperimentLogger(
            experiment_name=f"{exptype}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )




        # we added  live plot handles 
        self.live_fig = None
        self.ax_avg = None
        self.ax_bar = None

        self.arm_fig = None
        self.arm_axes = {}



    def run(self, n_trials):
        for i in range(n_trials):

            
            print(f"Entering trial number: {i + 1}")
            if self.exptype == 'optimal_channel':
                 arm = self.agent.select_arm()
                 channel = self.env.channels[arm]
                 print(f"DEBUG - selected arm index: {arm}, channel value: {channel}")  # Add this too
                 reward = self.env.get_reward(channel)
                 self.agent.update(arm, reward)
                 self.actions.append(channel)
                 self.rewards.append(reward)
                 row = [{
                    "Iteration": i,
                    "Channel": channel,
                    "Reward": reward,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                 }]
            elif self.exptype == 'optimal_route':
                arm = self.agent.select_arm() 
                print(arm)
                device = self.env.devices[arm]
                print(device)
                print(f"DEBUG - selected arm index: {arm}, device ip value: {device}")
                #time.sleep(1)
                reward = self.env.get_reward(device)
                self.agent.update(arm, reward)
                self.actions.append(device)
                self.rewards.append(reward)
                row = [{
                    "Iteration": i,
                    "Device": device,
                    "Reward": reward,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                 }]


            #save_to_csv(row) # we save each iteration as a row of a data bank so we can replay the experiment again if we desire
            q_values = self.agent.get_estimated_values()

            self.logger.log_step(
                    iteration=i,
                    arm_index=arm,
                    arm_label=self.actions[-1],
                    reward=reward,
                    q_values=q_values
                )
            self.update_live_main_plot(i)
            self.update_live_arm_plots(i)
            self.update_live_arm_plots_for_each(i)


            if i == 200 or i == n_trials - 1:
                plt.ioff()
                print(f"Iteration {i}: All diagrams frozen. Close windows to exit.")
                plt.show(block=True)
            
        
            # halfway checkpoint
            """
            if i + 1 == n_trials // 2:
                print("\n📊 Halfway through — generating mid-run plot...\n")
                print("\n We are on the iteration: ", i)
                self.plot()
                self.plot_avg_reward_per_arm_over_time()  # show the first-half plot
            """

    def plot(self):

        # --- LABELS BASED ON EXPERIMENT TYPE ---
        if self.exptype == 'optimal_route':
            entity_singular = "Route"
            entity_plural = "Routes"
            main_title = "Epsilon-Greedy Optimal Route Selection: Final Results"
        else:
            entity_singular = "Channel"
            entity_plural = "Channels"
            main_title = "Epsilon-Greedy Wireless Channel Selection: Final Results"
        # 1. Apply a modern style
        plt.style.use('ggplot')
        
        if len(self.rewards) == 0:
            raise ValueError("No data to plot. Run experiment.run(n_trials) first.")

        steps = np.arange(1, len(self.rewards) + 1)
        avg_reward = np.cumsum(self.rewards) / steps  # cumulative average reward

        # 2. Increase figure size for better clarity
        fig, axs = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle(main_title,
             fontsize=18, fontweight='bold', color='#444444')

        # --- Subplot 1: Cumulative Average Reward ---
        axs[0].plot(steps, avg_reward, color='#E69F00', linewidth=3) # Use a distinctive color and thicker line
        axs[0].set_title("Average Reward vs Steps (Iterations)", loc='left', fontsize=14, fontweight='bold')
        axs[0].set_xlabel("Step (Iteration)", fontsize=12)
        axs[0].set_ylabel("Cumulative Average Reward", fontsize=12)
        axs[0].grid(True, linestyle='-', alpha=0.4)
        
        # Remove top and right spines
        axs[0].spines['right'].set_visible(False)
        axs[0].spines['top'].set_visible(False)
        
        # Add final value annotation
        axs[0].text(steps[-1], avg_reward[-1], f'Final: {avg_reward[-1]:.2f}', 
                    color='black', fontsize=11, ha='right', va='bottom', fontweight='bold')


        # --- Subplot 2: Average Reward per Channel (Bar Chart) ---
        unique_channels = list(dict.fromkeys(self.actions))
        avg_rewards_per_channel = []
        for ch in unique_channels:
            ch_rewards = [r for (a, r) in zip(self.actions, self.rewards) if a == ch]
            avg_rewards_per_channel.append(np.mean(ch_rewards))
            
        # Sort channels by their average reward for better visual comparison
        sorted_data = sorted(zip(avg_rewards_per_channel, unique_channels), reverse=True)
        sorted_rewards = [d[0] for d in sorted_data]
        sorted_channels = [str(d[1]) for d in sorted_data]

        bars = axs[1].bar(sorted_channels, sorted_rewards, color='#56B4E9') # Use a complementary color
        axs[1].set_title(
            f"Average Reward per {entity_singular} (Arm)",
            loc='left', fontsize=14, fontweight='bold'
        )
        axs[1].set_xlabel(f"{entity_singular} (Arm)", fontsize=12)
        axs[1].set_ylabel("Average Reward", fontsize=12)
        axs[1].grid(axis='y', linestyle='-', alpha=0.4)
        
        # Add reward labels on top of the bars
        for bar in bars:
            height = bar.get_height()
            axs[1].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=10)

        # Remove top and right spines
        axs[1].spines['right'].set_visible(False)
        axs[1].spines['top'].set_visible(False)


        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
        
        # Restore default style
        plt.style.use('default')


    # line plots for each arm
    def plot_avg_reward_per_arm_over_time(self):
        # 1. Apply a modern style
        plt.style.use('ggplot')
        
        if len(self.rewards) == 0:
            raise ValueError("No data to plot. Run experiment.run(n_trials) first.")

        arms = list(dict.fromkeys(self.actions))  # unique arm labels
        n_arms = len(arms)

        # 2. Adjust figure size and apply main title styling
        fig, axs = plt.subplots(n_arms, 1, figsize=(12, 5 * n_arms), sharex=True)
        fig.suptitle("Average Reward per Arm Over Time: Individual Performance", 
                     fontsize=18, fontweight='bold', color='#444444')

        # If there is only one arm, axs is not a list → convert it
        if n_arms == 1:
            axs = [axs]

        # 3. Get distinct colors for each arm
        colors = plt.cm.get_cmap('Dark2', n_arms) 

        for idx, arm in enumerate(arms):
            cumulative_sum = 0
            count = 0
            arm_avg_rewards = []
            steps = []

            # Build the arm-specific average reward over time
            for t, (a, r) in enumerate(zip(self.actions, self.rewards), start=1):
                if a == arm:
                    count += 1
                    cumulative_sum += r
                    arm_avg_rewards.append(self.rewards)  # cumulative_sum / count
                    steps.append(t)

            ax = axs[idx]
            color = colors(idx)
            
            # 4. Use styled plot line and fill
            ax.plot(steps, arm_avg_rewards, 
                    color=color, 
                    linewidth=3, 
                    marker='o' if count < 10 else None, # Only show markers for small number of selections
                    markersize=6
            )
            ax.fill_between(steps, arm_avg_rewards, color=color, alpha=0.15)

            # 5. Enhanced Title, Labels, and Spines
            ax.set_title(f"Arm {arm} (Selections: {count})", loc='left', fontsize=14, fontweight='bold')
            ax.set_ylabel("Avg Reward", fontsize=12)
            ax.grid(True, linestyle='-', alpha=0.4)
            
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            
            # Add final average text
            if count > 0:
                 ax.text(steps[-1], arm_avg_rewards[-1] + 0.05 * (max(arm_avg_rewards) - min(arm_avg_rewards) if len(arm_avg_rewards) > 1 else 1), 
                        f'{arm_avg_rewards[-1]:.2f}',
                        color='black', fontsize=10, ha='right', fontweight='bold')


        axs[-1].set_xlabel("Step (Iteration)", fontsize=14)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
        
        # Restore default style
        plt.style.use('default')
    
    def update_live_main_plot(self, iteration):
        # --- LABELS BASED ON EXPERIMENT TYPE ---
        if self.exptype == 'optimal_route':
            entity_singular = "Route"
            entity_plural = "Routes"
            main_title = "Live Optimal Route Selection"
        else:
            entity_singular = "Channel"
            entity_plural = "Channels"
            main_title = "Live Channel Performance"
        # 1. Apply a modern style
        plt.style.use('ggplot')
        plt.ion()

        # Get all channels from environment (needed for consistent bar colors)
        all_arms = self.env.channels
        colors = plt.cm.get_cmap('Dark2', len(all_arms))

        # --- GET ESTIMATED Q-VALUES FOR DYNAMIC SUBTITLE ---
        # Call the getter method to retrieve the current estimated values (Q-values)
        current_q_values = self.agent.get_estimated_values()
        
        # Find the index (channel number) of the maximum Q-value
        # Use np.argmax to find the index of the best channel
        best_channel_index = np.argmax(current_q_values) #best_device_index = np.argmax(current_q_values) 
        best_value = current_q_values[best_channel_index]#best_value = current_q_values[best_device_index]
        # Assuming channel names are what's in all_arms, which corresponds to the index
        # Note: If all_arms is a list of channel identifiers, use all_arms[best_channel_index]
        best_channel_name = all_arms[best_channel_index]#best_device_name = all_arms[best_device_index]
        
        # Create the dynamic text string
        dynamic_subtitle = f"Best Estimated {entity_singular}: {best_channel_name} (Value: {best_value:.2f})"
        # --------------------------------------------------
        
        if self.live_fig is None:
            # Increase figure size for better visual separation
            self.live_fig, (self.ax_avg, self.ax_bar) = plt.subplots(2, 1, figsize=(12, 9))
            self.live_fig.suptitle(main_title,
                       fontsize=18, fontweight='bold', color='#444444')
            # --- INITIAL SUBTITLE PLACEMENT (Placeholder) ---
            # Initialize the dynamic text object; we will update its content later
            # We store the reference to update it efficiently
            self.best_channel_text = self.live_fig.text(x=0.5, 
                                                        y=0.93, # Positioning the subtitle
                                                        s=dynamic_subtitle, 
                                                        fontsize=12, 
                                                        color='#008000', # Use a bold color like green
                                                        fontweight='semibold',
                                                        ha='center')
        else:
            # --- UPDATE SUBTITLE ---
            # If the figure already exists, just update the text object's content
            # self.best_channel_text.set_text(dynamic_subtitle)
            print("")

        steps = np.arange(1, len(self.rewards)+ 1)
        avg_reward = np.cumsum(self.rewards) / steps

        # --- Update line plot (Cumulative Average) ---
        self.ax_avg.clear()
        
        # 2. Add bold markers and use fill
        self.ax_avg.plot(steps, avg_reward, 
                         color='#E69F00', 
                         linewidth=3, 
                         marker='o',          # Add marker
                         markersize=7,        # Bold marker size
                         markeredgecolor='black',
                         markerfacecolor='#E69F00',
                         label="Cumulative Avg Reward"
        )
        self.ax_avg.fill_between(steps, avg_reward, color='#E69F00', alpha=0.1)
        
        # 3. Add text annotation above each marker
        for s, avg in zip(steps, avg_reward):
            # Only annotate every 5th step or the last step to prevent clutter
            if s % 5 == 0 or s == steps[-1]:
                self.ax_avg.text(s, avg + (max(avg_reward) - min(avg_reward)) * 0.02, # Offset text slightly above
                                 f'{avg:.2f}',
                                 color='black', fontsize=9, ha='center', va='bottom', fontweight='bold')


        # Refined titles, labels, and grid
        self.ax_avg.set_title("Cumulative Average Reward Over Time", loc='left', fontsize=14, fontweight='bold')
        self.ax_avg.set_xlabel("Step (Iteration)", fontsize=12)
        self.ax_avg.set_ylabel("Avg Reward", fontsize=12)
        self.ax_avg.grid(True, linestyle='-', alpha=0.4)
        
        # Remove top and right spines
        self.ax_avg.spines['right'].set_visible(False)
        self.ax_avg.spines['top'].set_visible(False)


        # --- Update bar chart (Channel Comparison) ---
        unique = list(dict.fromkeys(self.actions))
        bar_values = [
            np.mean([r for (a, r) in zip(self.actions, self.rewards) if a == ch])
            for ch in unique
        ]

        # Sort bars by value for easy comparison
        sorted_data = sorted(zip(bar_values, unique), reverse=True)
        sorted_rewards = [d[0] for d in sorted_data]
        sorted_channels = [str(d[1]) for d in sorted_data]
        
        self.ax_bar.clear()
        
        # 4. Determine colors for the bars based on their original channel value position in all_arms
        bar_colors = [colors(all_arms.index(float(ch))) for ch in sorted_channels]
        
        # Plot bars using the consistent colors
        bars = self.ax_bar.bar(sorted_channels, sorted_rewards, color=bar_colors)
        
        # Add reward labels on top of the bars
        for bar in bars:
            height = bar.get_height()
            self.ax_bar.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                             f'{height:.2f}',
                             ha='center', va='bottom', fontsize=10)


        self.ax_bar.set_title(
            f"Average Reward per {entity_singular} (Current)",
            loc='left', fontsize=14, fontweight='bold', pad=20
        )
        self.ax_bar.set_xlabel(entity_singular, fontsize=12)
        self.ax_bar.set_ylabel("Avg Reward", fontsize=12)
        self.ax_bar.grid(axis='y', linestyle='-', alpha=0.4)

        # Remove top and right spines
        self.ax_bar.spines['right'].set_visible(False)
        self.ax_bar.spines['top'].set_visible(False)

        # update subtitle FIRST
        self.live_fig.tight_layout(rect=[0, 0, 1, 0.96])
        self.live_fig.canvas.draw()
        self.live_fig.canvas.flush_events()

        if iteration == 0:
            self.best_channel_text.set_text(f"Best Estimated {entity_singular}: None")

        else:
            self.best_channel_text.set_text(dynamic_subtitle)

        # One more lightweight draw to update just the subtitle
        self.live_fig.canvas.draw_idle()
        # Restore default style
        plt.style.use('default')

       
    def update_live_arm_plots(self, iteration):
        plt.style.use('ggplot')
        plt.ion()

        all_arms = self.env.channels
        
        # --- TRACKING THE LEARNING CURVE ---
        if not hasattr(self, 'q_value_history_per_arm'):
            self.q_value_history_per_arm = {arm: [] for arm in all_arms}
            self.step_history_per_arm = {arm: [] for arm in all_arms}

        if len(self.actions) > 0:
            last_action = self.actions[-1]
            current_estimates = self.agent.get_estimated_values()
            action_idx = all_arms.index(last_action)
            
            # Capture the actual estimate at this specific moment
            self.q_value_history_per_arm[last_action].append(current_estimates[action_idx])
            self.step_history_per_arm[last_action].append(len(self.actions))

        if self.arm_fig is None:
            n_arms = len(all_arms)
            # Increase height significantly to prevent squashing
            self.arm_fig, axs = plt.subplots(n_arms, 1, figsize=(12, 5 * n_arms)) 
            self.arm_axes = axs if n_arms > 1 else [axs]
            self.arm_fig.suptitle("Live Agent Q-Value Estimates", fontsize=20, fontweight='bold')

        colors = plt.cm.get_cmap('Dark2', len(all_arms)) 

        for idx, ax in enumerate(self.arm_axes):
            arm_identity = all_arms[idx]
            steps = self.step_history_per_arm[arm_identity]
            q_vals = self.q_value_history_per_arm[arm_identity]

            ax.clear()
            
            if len(steps) > 1:
                color = colors(idx)
                ax.plot(steps, q_vals, color=color, linewidth=3, marker='o', markersize=6)
                ax.fill_between(steps, q_vals, color=color, alpha=0.1)

                # --- THE "ZOOM" FIX: LOGARITHMIC OR WINDOWED SCALING ---
                # We ignore the first few points if they are outliers (the 300+ values)
                # to focus on the stabilized values (the 15-40 range)
                focus_data = q_vals[int(len(q_vals)*0.2):] if len(q_vals) > 5 else q_vals
                
                v_min, v_max = min(focus_data), max(focus_data)
                # Add a tiny 10% margin
                margin = (v_max - v_min) * 0.1 if v_max != v_min else 1.0
                
                # FORCE the axis to stay within the 'learned' range
                ax.set_ylim(v_min - margin, v_max + margin)

                # Final value label
                ax.annotate(f'Final: {q_vals[-1]:.2f}', xy=(steps[-1], q_vals[-1]), 
                            xytext=(10, 0), textcoords='offset points',
                            bbox=dict(boxstyle='round', fc='white', ec=color, alpha=0.8),
                            fontweight='bold')
            
            elif len(steps) == 1:
                # Single point case
                ax.scatter(steps, q_vals, color=colors(idx), s=100)
                ax.text(steps[0], q_vals[0], f'Initial: {q_vals[0]:.2f}')
            else:
                ax.text(0.5, 0.5, 'ARM NOT YET SAMPLED', ha='center', va='center', 
                        transform=ax.transAxes, color='gray', fontsize=12)

            ax.set_title(f"Channel {arm_identity}", loc='left', fontsize=15, fontweight='bold')
            ax.set_ylabel("Estimate")
            ax.grid(True, linestyle=':', alpha=0.6)

        self.arm_axes[-1].set_xlabel("Iterations")
        self.arm_fig.tight_layout(rect=[0, 0, 1, 0.95])
        
        self.arm_fig.canvas.draw()
        self.arm_fig.canvas.flush_events()

        plt.style.use('default')


    def update_live_arm_plots_for_each(self, iteration):
        plt.style.use('ggplot')
        plt.ion()

        all_arms = self.env.channels
        
        # --- FIX: INITIALIZE THE DICTIONARIES IF THEY DON'T EXIST ---
        if not hasattr(self, 'individual_figs'):
            self.individual_figs = {}
        if not hasattr(self, 'individual_axes'):
            self.individual_axes = {}

        # --- TRACKING THE LEARNING CURVE ---
        if not hasattr(self, 'q_value_history_per_arm'):
            self.q_value_history_per_arm = {arm: [] for arm in all_arms}
            self.step_history_per_arm = {arm: [] for arm in all_arms}

        if len(self.actions) > 0:
            last_action = self.actions[-1]
            current_estimates = self.agent.get_estimated_values()
            action_idx = all_arms.index(last_action)
            
            # Capture the actual estimate at this specific moment
            self.q_value_history_per_arm[last_action].append(current_estimates[action_idx])
            self.step_history_per_arm[last_action].append(len(self.actions))

        colors = plt.cm.get_cmap('Dark2', len(all_arms)) 

        for idx, arm_identity in enumerate(all_arms):
            # Create a separate window for this arm if it doesn't exist
            if arm_identity not in self.individual_figs:
                # Each call here creates a brand new independent window
                fig, ax = plt.subplots(figsize=(10, 6))
                fig.canvas.manager.set_window_title(f"Channel {arm_identity} - Live Estimate")
                self.individual_figs[arm_identity] = fig
                self.individual_axes[arm_identity] = ax

            ax = self.individual_axes[arm_identity]
            fig = self.individual_figs[arm_identity]
            
            steps = self.step_history_per_arm[arm_identity]
            q_vals = self.q_value_history_per_arm[arm_identity]

            ax.clear()
            
            if len(steps) > 1:
                color = colors(idx)
                ax.plot(steps, q_vals, color=color, linewidth=3, marker='o', markersize=6)
                ax.fill_between(steps, q_vals, color=color, alpha=0.1)

                # --- YOUR "ZOOM" FIX LOGIC ---
                focus_data = q_vals[int(len(q_vals)*0.2):] if len(q_vals) > 5 else q_vals
                v_min, v_max = min(focus_data), max(focus_data)
                margin = (v_max - v_min) * 0.1 if v_max != v_min else 1.0
                ax.set_ylim(v_min - margin, v_max + margin)

                # Final value label
                ax.annotate(f'Final: {q_vals[-1]:.2f}', xy=(steps[-1], q_vals[-1]), 
                            xytext=(10, 0), textcoords='offset points',
                            bbox=dict(boxstyle='round', fc='white', ec=color, alpha=0.8),
                            fontweight='bold')
            
            elif len(steps) == 1:
                ax.scatter(steps, q_vals, color=colors(idx), s=100)
                ax.text(steps[0], q_vals[0], f'Initial: {q_vals[0]:.2f}')
            else:
                ax.text(0.5, 0.5, 'ARM NOT YET SAMPLED', ha='center', va='center', 
                        transform=ax.transAxes, color='gray', fontsize=12)

            ax.set_title(f"Channel {arm_identity}", loc='left', fontsize=15, fontweight='bold')
            ax.set_ylabel("Estimate")
            ax.set_xlabel("Iterations")
            ax.grid(True, linestyle=':', alpha=0.6)

            fig.canvas.draw()
            fig.canvas.flush_events()

        # --- FREEZE AT 100 ---
        plt.style.use('default')
