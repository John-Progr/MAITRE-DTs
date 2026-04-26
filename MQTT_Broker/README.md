# MQTT_setup
This script sets up your mqtt broker on ubuntu system ( currently ubuntu 24.04)



The script performs an existence check using command -v. This checks if mosquitto is in the system path. If not, it sxecutes a silent update and installs both the broker and clients tools(mosquitto_sub). We need the broker one for the experiments, but mosquitto_sub is extemely useful for debugging.


It targets the master config file at /etc/mosquitto/mosquitto.conf. It searches for the include_dir string; ig missing, it appends it. This hooks the master config into a modular folder (conf.d), allowing us to inject custom network settings without touching the core system files. ( the same logic has been applied to raspberry pi configuration)

It uses mkdir -p to ensure the /etc/mosquitto/conf.d directory exists. This ensures that the subsequent Write commands have a valid destination on the disk, preventing Directory not found errors during the configuration phase.

Using a TEE command and a HEREDOC, it creates a localized config file. IT defines three strict rules for our Testbed.
1. Listener 1883: Standardizes the communication port
2. Allow_anonymous_false: Forces the system to reject any data packet that doesn't have a valid username/password
3. Password_file: Maps the broker to a specific credential database

It uses systemctl to pull the service into the active memory.
Start: launches the process immediately 
Enable: Writes a symlink to the boot sequence so the MQTT broker starts automatically when the server power cycles


And as the validation which is the final part. It checks if the service is active. If it is, it runs mosquitto_passwd wit hthe -c flag to create a fresh, encrypted fil;e for our specified $USERNAME. If the service failed to start, it kills the script with an error code (exit 1) to prevent a " zombie" configuration

