import socket
import re
import time


def get_local_ipv4_address():
    """
    Retrieves the local IPv4 address of the machine.
    """
    try:
        # Get the local hostname
        hostname = socket.gethostname()
        # Resolve the hostname to its IP address
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except socket.gaierror:
        return "Could not resolve hostname to IP address."


def update_index_html(ip_address):
    """
    Updates the index.html file with the current local IP address.
    """
    try:
        # Read the file content
        with open("index.html", "r") as f:
            content = f.read()

        # Replace the IP address in the JavaScript variable
        updated_content = re.sub(r'const ipAddress = ".*?";', f'const ipAddress = "{ip_address}";', content)

        # Write the updated content back to the file
        with open("index.html", "w") as f:
            f.write(updated_content)

        print(f"Updated index.html with IP address: {ip_address}")
    except Exception as e:
        print(f"Error updating index.html: {e}")


def main():
    """
    Main function that runs periodically to update the local IP address.
    """
    check_interval = 5  # Check every 5 seconds

    while True:
        try:
            ip_address = get_local_ipv4_address()
            if ip_address != "Could not resolve hostname to IP address.":
                update_index_html(ip_address)
            else:
                print("Could not determine local IP address")

            time.sleep(check_interval)

        except KeyboardInterrupt:
            print("\nStopping IP monitor...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(check_interval)


if __name__ == "__main__":
    main()
