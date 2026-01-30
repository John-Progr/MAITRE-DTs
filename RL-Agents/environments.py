import numpy as np 
import requests
import time


#Make a super class for wirelessEnv and subclasses wirelesschannelEnv and wirelessroutingEnv 

class WirelessChannelEnv:

    def __init__(self, source_ip, dest_ip, channels,reward_endpoint, reward_machine):

        """
        Request to a testbed as a service environment to get throughput (our reward)


        Args:
            channels: List of available channels.
            reward_endpoint: API endpoint to fetch rewards from.

        """
      
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.channels = channels
        self.reward_endpoint = reward_endpoint
        self.reward_machine = reward_machine
        #self.reward_url = reward_url  # store the private URL
        """
        if self.reward_machine == 3 and self.reward_url:
            try:
                df = pd.read_csv(self.reward_url, header=None)  # ⬅️ NO HEADER
                # assuming reward is in column index 2
                self.reward_iter = iter(df[2].tolist())
            except Exception as e:
                raise RuntimeError(f"Failed to load reward data: {e}")
       """

    def send_request(self, channel):
        request_data = {
            "source": self.source_ip,
            "destination": self.dest_ip,
            "path": [],
            "wireless_channel": channel
        }


        max_retries = 3
        delay = 2

        for attempt in range (1, max_retries + 1):

            try:
                time.sleep(2)
                response = requests.post(self.reward_endpoint, json=request_data, timeout = 100)

                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"❌ Attempt {attempt}: HTTP {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Attempt {attempt}: Request error: {e}")
            

            if attempt < max_retries:
                sleep_time = delay * ( 2 ** (attempt - 1))
                print(f"⏳ Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print("🚫 All retries failed.")
                return None


    def get_reward(self, channel):
        """
        Fetch reward for a given channel, either via API or simulation

        """
        if self.reward_machine == 0:
            json_response = self.send_request(channel)
            print(json_response)
                
            if json_response is None or "rate_mbps" not in json_response or json_response["rate_mbps"] is None:
                    reward = 18
            else:
                reward = json_response["rate_mbps"]
            return reward
            
             
        elif self.reward_machine == 1:
            return np.clip(np.random.rayleigh(scale=5.0) + 5, 5, 40)

        elif self.reward_machine == 2:
            return np.clip( np.random.normal(loc=22.5, scale=5), 5, 40)
        
        elif self.reward_machine == 3:
            try:
                return next(self.reward_iter)
            except StopIteration:
                raise RuntimeError("No more rewards available in CSV")

        elif self.reward_machine == 4:
            return 10
          

#Make a super class for wirelessEnv and subclasses wirelesschannelEnv and wirelessroutingEnv 

class WirelessRouteEnv:

    def __init__(self, source_ip, dest_ip,devices, reward_endpoint, reward_machine, channel):

        """
        Request to a testbed as a service environment to get throughput (our reward)


        Args:
            channels: List of available channels.
            reward_endpoint: API endpoint to fetch rewards from.

        """
      
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.devices = devices
        self.reward_endpoint = reward_endpoint
        self.reward_machine = reward_machine
        self.channel = channel
        #self.reward_url = reward_url  # store the private URL
        """
        if self.reward_machine == 3 and self.reward_url:
            try:
                df = pd.read_csv(self.reward_url, header=None)  # ⬅️ NO HEADER
                # assuming reward is in column index 2
                self.reward_iter = iter(df[2].tolist())
            except Exception as e:
                raise RuntimeError(f"Failed to load reward data: {e}")
       """

    def send_request(self, device):
        request_data = {
            "source": self.source_ip,
            "destination": self.dest_ip,
            "path": [f"192.168.2.{device}"],
            "wireless_channel": self.channel
        }


        max_retries = 3
        delay = 2

        for attempt in range (1, max_retries + 1):

            try:
                time.sleep(2)
                response = requests.post(self.reward_endpoint, json=request_data, timeout = 100)

                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"❌ Attempt {attempt}: HTTP {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Attempt {attempt}: Request error: {e}")
            

            if attempt < max_retries:
                sleep_time = delay * ( 2 ** (attempt - 1))
                print(f"⏳ Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print("🚫 All retries failed.")
                return None

    

    def get_reward(self, device):
        """
        Fetch reward for a given channel, either via API or simulation

        """
        if self.reward_machine == 0:
            json_response = self.send_request(device)
            print(json_response)
                
            if json_response is None or "rate_mbps" not in json_response or json_response["rate_mbps"] is None:
                    reward = -100000
            else:
                reward = json_response["rate_mbps"]
            return reward
            
             
        elif self.reward_machine == 1:
            return np.clip(np.random.rayleigh(scale=5.0) + 5, 5, 40)

        elif self.reward_machine == 2:
            return np.clip( np.random.normal(loc=22.5, scale=5), 5, 40)
        
        elif self.reward_machine == 3:
            try:
                return next(self.reward_iter)
            except StopIteration:
                raise RuntimeError("No more rewards available in CSV")

        elif self.reward_machine == 4:
            return 10
          




