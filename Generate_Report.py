import csv
from netmiko import ConnectHandler
from colorama import Fore


# defining module to generate csv report, passing inventory variable
def Generating_Report(inventory):
    # display message telling user what is happening
    print(Fore.BLUE,"Generating Reports".center(50))
    print(Fore.WHITE,"#"*50)
    print()
    # loop through all devices
    for device in inventory:
        try:
            # define the connection parameters to connect using netmiko
            device_connection_parameters = {
                    'device_type': device["Operating_System"],
                    'ip': device['Management_ip'],
                    'username': device['Username'],
                    'password': device['Password']
                }
            
            device_connection = ConnectHandler(**device_connection_parameters)
            show_version_output = device_connection.send_command("show version", use_textfsm=True)
            get_banner_motd = device_connection.send_command("show run | inc banner")
            get_number_of_interfaces = device_connection.send_command("show ip int br", use_textfsm=True)
            banner = get_banner_motd.strip("banner motd ^C")
            hostname = show_version_output[0]['hostname']
            MAC_Address = show_version_output[0]['mac_address']
            type = show_version_output[0]['hardware'][0]
            os = show_version_output[0]['rommon']
            os_version = show_version_output[0]['version']
            image = show_version_output[0]['software_image']
            uptime = show_version_output[0]['uptime']
            serial = show_version_output[0]['serial'][0]
            number_of_int = len(get_number_of_interfaces)

            
            Report_Headers = ['Device Name', 'MAC', 'Type', 'Serial Number', 'Number of Interfaces', 'System Image', 'Operating System', 'Operating System Version', 'Uptime', 'Banner Text' ]
            
            filename = f"{device['Hostname']}.csv"
            with open(filename, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=Report_Headers)
                writer.writeheader()
                writer.writerow({'Device Name': hostname , 'MAC': MAC_Address, 'Type': type, 'Serial Number': serial, 'Number of Interfaces': number_of_int, 'System Image': image, 'Operating System': os, 'Operating System Version': os_version, 'Uptime': uptime, 'Banner Text': banner })
            print(Fore.GREEN, f"SUCCESS: Report generated for {device['Hostname']}".center(50), Fore.RESET)
            print()
            
        except:
            print(Fore.RED, f"Could not generate report for {device['Hostname']}".center(50), Fore.RESET)
            
