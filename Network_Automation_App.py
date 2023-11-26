from netmiko.ssh_dispatcher import ConnectHandler
import json
import Device_Configurations
from colorama import Fore
import time
import Generate_Report

# defining module to work with the inventory file
def Opening_inventory_file():
    # define the file_path variable to the files absolute path
    file_path = r"inventory_file.json"

    # open the inventory file in read mode
    with open(file_path, 'r') as file:
        # assign the contents of the file to the inventory variable
        inventory = json.load(file)
    # return the inventory variable
    return inventory

# defining module for collecting all the ips for the verification
def Collecting_IPs(inventory):
    # create empty list for connectivity verification
    ip_addresses_to_ping = []
    # loop through and collect all the ips
    for each in inventory:
        all_ips = each["Interfaces"]
        for ip in all_ips:
            ip_addresses_to_ping.extend(ip["ipv4"])
    # return the populated list of ips
    return ip_addresses_to_ping

# defining a module to Configure devices 
def Configuring_Devices(inventory):
    # print statements to show what the program is currently doing
    # Fore.XXXX to change the colour of text
    print(Fore.WHITE,"#"*50)
    print(Fore.BLUE,"Configuring All Devices".center(50))
    print(Fore.WHITE,"#"*50)
    print()

    # loop through all the devices in the inventory file
    for device in inventory:
        try:
            # define the connection parameters to connect using netmiko
            device_connection_parameters = {
                'device_type': device["Operating_System"],
                'ip': device['Management_ip'],
                'username': device['Username'],
                'password': device['Password']
            }
        
            # apply the Global Configurations
            Device_Configurations.Global_Configuration(device, **device_connection_parameters)
            # apply the Interface Configurations
            Device_Configurations.Interface_Configuration(device, **device_connection_parameters)
            # if the device has OSPF information do the following
            if device["OSPF"]:
                # apply the Routing Configuration
                Device_Configurations.routing_configuration(device, **device_connection_parameters)
            # print blank line
            print()
        except:
            # if any error, display error message
            print(Fore.RED,f"The application ran into an error while working on {device['Hostname']}", Fore.RESET)
            

# defining a module to run the verification check
def Running_Verification(inventory, ip_addresses_to_ping):
    # print statements to show what the program is currently doing
    # Fore.XXXX to change the colour of text
    print(Fore.WHITE,"#"*50)
    print(Fore.BLUE,"Starting Connectivity Test".center(50))
    print(Fore.WHITE,"#"*50)
    
    # loop through devices in the inventory
    for device in inventory:
        # define the connection parameters to connect using netmiko
        device_connection_parameters = {
                'device_type': device["Operating_System"],
                'ip': device['Management_ip'],
                'username': device['Username'],
                'password': device['Password']
            }
        # call the Connectiviity_Verification module and pass ip_addresses_to_ping, device, and device_connection_parameters
        Device_Configurations.Connectivity_Verification(ip_addresses_to_ping,device, **device_connection_parameters)
    # print blank line
    print()
    # print 50 # signs in white
    print(Fore.WHITE,"#"*50, Fore.RESET)   


# defining the order and structure to run the application
if __name__ == "__main__":
    # assign inventory variable by running the Opening_inventory_file function
    inventory = Opening_inventory_file()
    # collect the ip_addresses_to_ping by running the Collecting_IPs function and passing the inventory variable
    ip_addresses_to_ping = Collecting_IPs(inventory)
    # call the Configuring_Devices function and pass the inventory variable
    Configuring_Devices(inventory)
    # wait 10 seconds to allow network to converge
    time.sleep(10)
    # call the Running_Verification function and pass it the inventory and ip_addresses_to_ping variables
    Running_Verification(inventory, ip_addresses_to_ping)
    # call the Generating_Report function from Generate_Report file, passing it the inventory variable
    Generate_Report.Generating_Report(inventory)

