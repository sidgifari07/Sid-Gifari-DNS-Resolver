import os
import subprocess
import shutil
import sys
import time
from pathlib import Path
import ctypes


# ===============================
# BANNER
# ===============================
BANNER = """
███████╗██╗██████╗       ██████╗ ███╗   ██╗███████╗              
██╔════╝██║██╔══██╗      ██╔══██╗████╗  ██║██╔════╝              
███████╗██║██║  ██║█████╗██║  ██║██╔██╗ ██║███████╗              
╚════██║██║██║  ██║╚════╝██║  ██║██║╚██╗██║╚════██║              
███████║██║██████╔╝      ██████╔╝██║ ╚████║███████║              
╚══════╝╚═╝╚═════╝       ╚═════╝ ╚═╝  ╚═══╝╚══════╝              
                                                                 
██████╗ ███████╗███████╗ ██████╗ ██╗    ██╗   ██╗███████╗██████╗ 
██╔══██╗██╔════╝██╔════╝██╔═══██╗██║    ██║   ██║██╔════╝██╔══██╗
██████╔╝█████╗  ███████╗██║   ██║██║    ██║   ██║█████╗  ██████╔╝
██╔══██╗██╔══╝  ╚════██║██║   ██║██║    ╚██╗ ██╔╝██╔══╝  ██╔══██╗
██║  ██║███████╗███████║╚██████╔╝███████╗╚████╔╝ ███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝ ╚═══╝  ╚══════╝╚═╝  ╚═╝
                                                                 
Dns-resolve tool By Sid Gifari 
From:  Gifari Industries - BD Cyber Security Team
"""

def print_banner():
    """Print the banner with colors if available"""
    try:
        import colorama
        colorama.init()
        CYAN = colorama.Fore.CYAN
        GREEN = colorama.Fore.GREEN
        YELLOW = colorama.Fore.YELLOW
        RESET = colorama.Style.RESET_ALL
        
        lines = BANNER.strip().split('\n')
        # Print first part in cyan
        for i, line in enumerate(lines):
            if i < 7:  # First part
                print(CYAN + line + RESET)
            elif i < 14:  # Second part
                print(GREEN + line + RESET)
            else:  # Last lines
                print(YELLOW + line + RESET)
        print()
    except ImportError:
        print(BANNER)



# ===============================
# CONFIG
# ===============================
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR / "SidGifari-dns-resolver"

EXE_NAME = "SidGifari-dns-resolver.exe"
EXE_PATH = BASE_DIR / EXE_NAME

CONFIG_FILE = BASE_DIR / "dns-resolver.toml"
BLACKLIST_FILE = BASE_DIR / "black.txt"
IP_BLOCKLIST_FILE = BASE_DIR / "blocklist.txt"

SERVICE_NAME = "Dns-resolve"

# ===============================
# HELPERS
# ===============================

def print_status(message, status="info"):
    """Print status messages with formatting"""
    try:
        import colorama
        colorama.init()
        if status == "success":
            print(f"{colorama.Fore.GREEN}[✓]{colorama.Style.RESET_ALL} {message}")
        elif status == "error":
            print(f"{colorama.Fore.RED}[✗]{colorama.Style.RESET_ALL} {message}")
        elif status == "warning":
            print(f"{colorama.Fore.YELLOW}[!]{colorama.Style.RESET_ALL} {message}")
        else:
            print(f"{colorama.Fore.CYAN}[*]{colorama.Style.RESET_ALL} {message}")
    except ImportError:
        if status == "success":
            print(f"[✓] {message}")
        elif status == "error":
            print(f"[✗] {message}")
        elif status == "warning":
            print(f"[!] {message}")
        else:
            print(f"[*] {message}")

def run(cmd, check=False, capture_output=False, verbose=True):
    """Run a shell command"""
    if verbose:
        print_status(f"Executing: {cmd}")
    
    if capture_output:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        return result
    else:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        return result

def ensure_directory():
    """Ensure base directory exists"""
    if not BASE_DIR.exists():
        BASE_DIR.mkdir(parents=True, exist_ok=True)
        print_status(f"Created directory: {BASE_DIR}", "success")
    
    # Copy executable if not exists
    current_exe = Path(sys.argv[0]).parent / EXE_NAME
    if current_exe.exists() and not EXE_PATH.exists():
        shutil.copy2(current_exe, EXE_PATH)
        print_status(f"Copied executable to: {EXE_PATH}", "success")

# ===============================
# WRITE CONFIG FILES
# ===============================

def write_config_files():
    """Write all configuration files"""
    ensure_directory()
    
    print_status("Creating configuration files...")
    
    # Write main config
    CONFIG_FILE.write_text("""
listen_addresses = ['127.0.0.1:53', '[::1]:53']
path = '/dns-query'

http3 = false
http3_probe = false

# ==============================
# Server type settings
# ==============================
dnscrypt_servers = true
doh_servers = true
odoh_servers = false
force_tcp = false
refuse_any = false

# ==============================
# Server exclusions
# ==============================
disabled_server_names = []

# Network probing settings
netprobe_timeout = 60
netprobe_address = '9.9.9.9:53'

[forwarding_rules]
corp.local = ['8.8.8.8', '9.9.9.9', '1.0.0.1', '1.1.1.1']

allowed_ips = [
  '127.0.0.0/8',
  '9.9.9.9/32',
  '1.1.1.1/32',
  '8.8.8.8/32'
]

bootstrap_resolvers = [
  '1.1.1.1',
  '1.0.0.1',
  '8.8.8.8',
  '8.8.4.4',
  '9.9.9.9'
]

blocked_query_response = 'refused'
ipv4_servers = true
ipv6_servers = true

block_unqualified = true
block_undelegated = true
enable_hot_reload = false
offline_mode = false
dnssec = false
require_nolog = false

cert_refresh_concurrency = 10
cert_refresh_delay = 240
cert_ignore_timestamp = false

server_names = [
    'cloudflare',
    'quad9',
    'google',
    'adguard'
]

# ==============================
# DNSCrypt Resolver Sources
# ==============================
[sources.'public-resolvers']
urls = [
  'https://download.dnscrypt.info/resolvers-list/v3/public-resolvers.md'
]
cache_file = 'public-resolvers.md'
minisign_key = 'RWQf6LRCGA9i53mlYecO4IzT51TGPpvWucNSCh1CBM0QTaLn73Y7GFO3'
refresh_delay = 24

[sources.'relays']
urls = [
  'https://download.dnscrypt.info/resolvers-list/v3/relays.md'
]
cache_file = 'relays.md'
minisign_key = 'RWQf6LRCGA9i53mlYecO4IzT51TGPpvWucNSCh1CBM0QTaLn73Y7GFO3'
refresh_delay = 24

# Static resolvers for Apple
[static]
[static.'apple-doh-1']
stamp = "sdns://AgcAAAAAAAAABzE3LjEzMi44Mi4zABRkb2guZG5zLmFwcGxlLmNvbQ"
""".strip())
    print_status("Main configuration written", "success")

    # Write blacklist
    BLACKLIST_FILE.write_text("""
# Ad networks
doubleclick.net
googleadservices.com
googlesyndication.com
google-analytics.com
amazon-adsystem.com
adsrvr.org
adnxs.com
criteo.com
pubmatic.com
rubiconproject.com

# Analytics
segment.com
mixpanel.com
amplitude.com
hotjar.com

# Social trackers
analytics.twitter.com
platform.twitter.com

# Malware domains (examples)
000webhost.com
""".strip())

    # Write IP blocklist
    IP_BLOCKLIST_FILE.write_text("""
# Known ad networks
23.32.0.0/11
23.192.0.0/11
104.64.0.0/10
172.224.0.0/12

# Private ranges (should already be blocked)
10.0.0.0/8
172.16.0.0/12
192.168.0.0/16
""".strip())

    print_status("Blocklists written", "success")

# ===============================
# SERVICE MANAGEMENT
# ===============================

def manage_service():
    """Install and configure the service"""
    
    print_status(f"Setting up {SERVICE_NAME} service...")
    
    # Check if port 53 is already in use
    print_status("Checking if port 53 is available...")
    result = run("netstat -ano | findstr :53", capture_output=True)
    if "LISTENING" in result.stdout:
        print_status("Port 53 is in use. Attempting to free it...", "warning")
        run("sc stop Dnscache", check=False)
        run("sc stop Dnscache", check=False)
        time.sleep(2)
    
    # Stop if running
    result = run(f'sc stop "{SERVICE_NAME}"', capture_output=True)
    time.sleep(2)
    
    # Uninstall old service
    if EXE_PATH.exists():
        result = run(f'cmd /c "cd /d {BASE_DIR} && \"{EXE_PATH}\" -service uninstall"', capture_output=True)
        if result.returncode == 0:
            print_status("Old service uninstalled", "success")
        time.sleep(2)
    
    # Install new service
    if EXE_PATH.exists():
        print_status("Installing service...")
        result = run(f'cmd /c "cd /d {BASE_DIR} && \"{EXE_PATH}\" -service install"', capture_output=True)
        if result.returncode == 0:
            print_status("Service installed", "success")
        else:
            print_status(f"Service install failed: {result.stderr[:100]}", "error")
            return False
        time.sleep(2)
    else:
        print_status(f"Executable not found: {EXE_PATH}", "error")
        return False
    
    # Configure service
    result = run(f'sc config "{SERVICE_NAME}" start= auto', capture_output=True)
    if result.returncode == 0:
        print_status("Service configured for auto-start", "success")
    time.sleep(2)
    
    # Start service
    result = run(f'sc start "{SERVICE_NAME}"', capture_output=True)
    if result.returncode == 0:
        print_status("Service started", "success")
    else:
        print_status(f"Service start failed: {result.stderr[:100]}", "error")
    
    # Check service status
    time.sleep(3)
    result = run(f'sc query "{SERVICE_NAME}"', capture_output=True)
    if "RUNNING" in result.stdout:
        print_status("Service is running", "success")
        return True
    else:
        print_status("Service may not be running", "warning")
        return False

# ===============================
# DNS CONFIGURATION
# ===============================

def configure_dns():
    """Configure system DNS settings"""
    
    print_status("Configuring system DNS...")
    
    # Get active network interfaces
    result = run("netsh interface show interface", capture_output=True)
    interfaces = []
    
    for line in result.stdout.split('\n'):
        if "Connected" in line and "Loopback" not in line:
            parts = line.split()
            if len(parts) >= 4:
                interface_name = " ".join(parts[3:])
                interfaces.append(interface_name)
    
    print_status(f"Found {len(interfaces)} active interfaces")
    
    # Configure DNS for each interface
    for interface in interfaces:
        print_status(f"Configuring {interface}...")
        
        # Clear existing DNS
        run(f'netsh interface ipv4 set dnsservers "{interface}" source=dhcp', check=False)
        run(f'netsh interface ipv6 set dnsservers "{interface}" source=dhcp', check=False)
        time.sleep(1)
        
        # Set static DNS
        result = run(f'netsh interface ipv4 set dnsservers "{interface}" static 127.0.0.1 primary', capture_output=True)
        if result.returncode == 0:
            print_status(f"IPv4 DNS configured for {interface}", "success")
        else:
            print_status(f"Failed to configure IPv4 for {interface}: {result.stderr[:100]}", "warning")
        
        result = run(f'netsh interface ipv6 set dnsservers "{interface}" static ::1 primary', capture_output=True)
        if result.returncode == 0:
            print_status(f"IPv6 DNS configured for {interface}", "success")
        else:
            print_status(f"Failed to configure IPv6 for {interface}: {result.stderr[:100]}", "warning")
    
    # Configure registry
    print_status("Setting registry keys...")
    
    # IPv4
    result = run(
        r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" '
        r'/v NameServer /t REG_SZ /d "127.0.0.1" /f',
        capture_output=True
    )
    if result.returncode == 0:
        print_status("IPv4 registry configured", "success")
    
    # IPv6
    result = run(
        r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip6\Parameters" '
        r'/v NameServer /t REG_SZ /d "::1" /f',
        capture_output=True
    )
    if result.returncode == 0:
        print_status("IPv6 registry configured", "success")
    
    # Flush DNS cache
    print_status("Flushing DNS cache...")
    run("ipconfig /flushdns", capture_output=True)
    print_status("DNS cache flushed", "success")

# ===============================
# TESTING
# ===============================

def test_dns():
    """Test DNS functionality"""
    
    print_status("Testing DNS configuration...")
    time.sleep(5)  # Give service time to start
    
    # First check if service is running
    result = run(f'sc query "{SERVICE_NAME}"', capture_output=True)
    if "RUNNING" not in result.stdout:
        print_status("Service is not running. Attempting to start...", "warning")
        run(f'sc start "{SERVICE_NAME}"', capture_output=True)
        time.sleep(3)
    
    # Test DNS resolution
    test_domains = ["google.com", "cloudflare.com", "example.com"]
    
    print_status("Testing DNS resolution through 127.0.0.1:")
    success_count = 0
    
    for domain in test_domains:
        try:
            result = subprocess.run(
                ["nslookup", domain, "127.0.0.1"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0 and "Address" in result.stdout:
                print_status(f"{domain} resolved successfully", "success")
                success_count += 1
                # Extract and display the resolved IP
                for line in result.stdout.split('\n'):
                    if "Address:" in line and "127.0.0.1" not in line:
                        print(f"    → {line.strip()}")
            else:
                print_status(f"{domain} lookup failed", "error")
                print(f"    Error: {result.stderr[:100]}")
                
        except subprocess.TimeoutExpired:
            print_status(f"{domain} lookup timed out", "error")
        except Exception as e:
            print_status(f"{domain} test failed: {e}", "error")
    
    # Display current DNS configuration
    print_status("Current DNS configuration:")
    result = run("ipconfig /all | findstr /i \"dns\"", capture_output=True)
    for line in result.stdout.split('\n'):
        if "DNS" in line.upper():
            print(f"    {line.strip()}")
    
    return success_count >= 2  # At least 2 out of 3 should succeed

# ===============================
# MAIN EXECUTION


def main():
    """Main execution function"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    print("=" * 70)
    print("        Sid-DNS Encrypt Tool")
    print("=" * 70)
    
    try:
        # Step 1: Write configuration files
        print_status("\n[STEP 1/4] Creating configuration files...")
        write_config_files()
        
        # Step 2: Install and configure service
        print_status("\n[STEP 2/4] Setting up DNS service...")
        service_ok = manage_service()
        if not service_ok:
            print_status("Service setup had issues, but continuing...", "warning")
        
        # Step 3: Configure system DNS
        print_status("\n[STEP 3/4] Configuring system DNS settings...")
        configure_dns()
        
        # Step 4: Test
        print_status("\n[STEP 4/4] Testing configuration...")
        test_result = test_dns()
        
        print("\n" + "=" * 70)
        if test_result:
            print_status("SETUP COMPLETED SUCCESSFULLY!", "success")
        else:
            print_status("SETUP COMPLETED WITH WARNINGS", "warning")
        print("=" * 70)
        
        print("\n" + "=" * 70)
        print("                      IMPORTANT NOTES")
        print("=" * 70)
        print("\nCommands:")
        print("  Check service status: sc query Dns-resolve")
        print("  Stop service: sc stop Dns-resolve")
        print("  Start service: sc start Dns-resolve")
        print("  Uninstall service: Run the executable with -service uninstall")
        
        print("\nTroubleshooting:")
        print("  1. If DNS isn't working, check if port 53 is free:")
        print("     netstat -ano | findstr :53")
        print("  2. Restart the service if needed:")
        print("     sc stop Dns-resolve && sc start Dns-resolve")
        print("  3. Reset DNS if needed:")
        print("     netsh interface ipv4 set dnsservers \"Ethernet\" dhcp")
        
        print("\n" + "=" * 70)
        print("    For best results, RESTART YOUR COMPUTER")
        print("=" * 70)
        
    except Exception as e:
        print_status(f"\n[ERROR] Setup failed: {e}", "error")
        print("\nTroubleshooting steps:")
        print("1. Make sure {EXE_NAME} exists in {BASE_DIR}")
        print("2. Check if port 53 is already in use (netstat -ano | findstr :53)")
        print("3. Try running the service manually first")
        print("4. Check Windows Firewall settings")
        return 1
    
    return 0

if __name__ == "__main__":

    try:
        exit_code = main()
    except KeyboardInterrupt:
        print_status("\n\nSetup cancelled by user.", "warning")
        exit_code = 1
    except Exception as e:
        print_status(f"\n\nUnexpected error: {e}", "error")
        exit_code = 1

    print("\n" + "=" * 70)
    print("          Thank you for using Sid-DNS Encrypt Tool")
    print("=" * 70)

    input("\nPress Enter to exit...")
    sys.exit(exit_code)
