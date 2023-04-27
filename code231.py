os.system(f'netsh advfirewall firewall add rule name="Block Port {PORT}" dir=in action=block protocol=TCP localport={PORT}')
os.system("netsh advfirewall set allprofiles state on")
