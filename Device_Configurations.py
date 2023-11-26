# import for connecting to devices and running commands
from netmiko.ssh_dispatcher import ConnectHandler
# import for colours!
from colorama import Fore



# defining a module for global configuration commands, provide the function with device, and the device_connection_parameters
def Global_Configuration(device, **device_connection_parameters):
    try:
        # create an object for the connection
        device_connection = ConnectHandler(**device_connection_parameters)
        # creating a set with the commands to execute
        Global_Config_Commands = [ 
            f"hostname {device['Hostname']}",
            f"banner motd {device['Banner']}",
            "No ip domain lookup",
            "username cisco priv 15 secret cisco",
            f"ip domain name {device['Domain_Name']}",
            "line vty 0 4",
            "transport input ssh",
            "Exit"
            ]
        # check if the device has a Default_gateway set in the inventory file
        if device["Default_gateway"]:
            Global_Config_Commands.append(f"ip default-gateway {device['Default_gateway']}")
        # executing commands from the set variable Global_Config_Commands
        device_connection.send_config_set(Global_Config_Commands)
        print(Fore.GREEN, f"SUCCESS: Global Configuration on {device['Hostname']}".center(50))
    except:
        print(Fore.RED, f"An error occured while trying to apply global configurations on {device['Hostname']} ".center(50))

# defining a module for interface configuration, provide the function with device, and the device_connection_parameters
def Interface_Configuration(device, **device_connection_parameters):
    try:
        interface_commands = []
        # create an object for the connection using ConnectHandler from netmiko and provide device_connection_parameters
        device_connection = ConnectHandler(**device_connection_parameters)
        # loop through all interfaces of the current device
        for interface in device["Interfaces"]:
            interface_commands.append(f"int {interface['Name']} ")
            # if the interface status is enabled, send the No shut command
            if interface['status'] == "enabled":
                interface_commands.append("No shut")
            # if the status was not enabled, send the shut command
            else:
                interface_commands.append("shut")

            # loop through the ip and subnet masks for the current interface and assign the values (allows secondary ip address configuration)
            # https://stackoverflow.com/questions/1663807/how-do-i-iterate-through-two-lists-in-parallel
            for i in range(len(interface['ipv4'])):
                # assign the first ip address and subnet mask as normal
                if i == 0:
                    interface_commands.append(f"ip address {interface['ipv4'][i]} {interface['subnetmask'][i]}")
   
                # assign the rest of the ip and subnet masks with the keyword "secondary"
                else:
                    interface_commands.append(f"ip address {interface['ipv4'][i]} {interface['subnetmask'][i]} secondary")
        # send the interface commands           
        device_connection.send_config_set(interface_commands)

        print(Fore.GREEN, f"SUCCESS: Interface Configuration on {device['Hostname']}".center(50))
    except:
        print(Fore.RED, f"An error occured while trying to configure interfaces on {device['Hostname']}".center(50))

        
        
# defining a module for routing configuration (OSPF), provide the function with device, and the device_connection_parameters
def routing_configuration(device, **device_connection_parameters):
    try:
        # create an empty list for the OSPF commands
        OSPF_commands =[]
        # append the command set the process id to the list
        OSPF_commands.append(f"router ospf {device['OSPF']['process_id']}")
        # append the command to set the router-id to the list
        OSPF_commands.append(f"router-id {device['OSPF']['Router-id']}")
        
        # loop through to find the networks and their areas
        for network_to_advertise in device['OSPF']['networks']:
            # add the network, wildcard, and area id command to the list
            OSPF_commands.append(f"network {network_to_advertise['network']} {network_to_advertise['wildcard_mask']} area {network_to_advertise['area']}")
        
        # create an object for the connection using ConnectHandler from netmiko and provide device_connection_parameters
        device_connection = ConnectHandler(**device_connection_parameters)
        # send the OSPF_commands
        device_connection.send_config_set(OSPF_commands)
  
        # display a SUCCESS message
        print(Fore.GREEN, f"SUCCESS: Routing Configuration on {device['Hostname']}".center(50))

    except:
        print(Fore.RED, f"An error occured while trying to configure OSPF on {device['Hostname']}".center(50))
        

# defining a module to verify connectivity of all devices, provide the function with ip_addresses_to_ping, device, and the device_connection_parameters
def Connectivity_Verification(ip_addresses_to_ping,device, **device_connection_parameters):
    
    # create an object for the connection using ConnectHandler from netmiko and provide device_connection_parameters
    device_connection = ConnectHandler(**device_connection_parameters)
    # print message to user
    print()
    print(Fore.LIGHTBLUE_EX,f"Testing Connectivity of {device['Hostname']}".center(50))
    Fore.RESET
    # loop through all the ip's in the list of ip_addresses_to_ping
    for ip in ip_addresses_to_ping:
        try:
            # ping the current ip with a repeat of 2 and store the output in the result variable
            result = device_connection.send_command(f"ping {ip} repeat 2")
            # if there is a ! in the output, display a successful message
            if "!" in result:
                print(Fore.GREEN, f"{device['Hostname']} Can Reach {ip}".center(50))
            # if there is not a ! in the output, display an unsuccessful message
            else:
                print(Fore.RED, f"{device['Hostname']} Cannot Reach {ip}".center(50))

        except:
            print(Fore.RED, f"An error occured while trying to verify connectivity on {device['Hostname']}".center(50))

            