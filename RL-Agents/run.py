from agents import EpsilonGreedy
from environments import WirelessChannelEnv, WirelessRouteEnv
from experiment import Experiment
from dotenv import load_dotenv


source_ip ="192.168.2.80"
dest_ip = "192.168.2.100"
channels = [2,3,4,11] 
devices = [10,40,50]
agent = EpsilonGreedy(n_arms=len(channels), epsilon=0.25,update_rule= "exponential_smoothing", alpha = 0.5)
envChannel = WirelessChannelEnv(source_ip,dest_ip,channels, "http://localhost:8000/network/data-transfer-rate",0)
envRoute = WirelessRouteEnv(source_ip,dest_ip,devices, "http://localhost:8000/network/data-transfer-rate", 0, 165)

# Here we will put type of experiment. its either optimal channel experiment or optimal route. 
exp = Experiment(agent, envChannel, 'optimal_channel')
exp.run(200)
#exp.plot()
#exp.plot_avg_reward_per_arm_over_time()



