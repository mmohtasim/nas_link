import socket
import re
import subprocess
import os


def get_local_ipv4_address():
    """
    Retrieves the local IPv4 address of the machine.
    """
    try:
        # Get all network interfaces
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        # If we got a localhost address, try to find the actual local IP
        if ip_address.startswith("127.") or ip_address == "0.0.0.0":
            import netifaces

            interfaces = netifaces.interfaces()
            for interface in interfaces:
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr_info in addrs[netifaces.AF_INET]:
                        ip = addr_info.get("addr")
                        if (
                            ip
                            and not ip.startswith("127.")
                            and not ip.startswith("169.254")
                        ):
                            return ip

        return ip_address
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return "Could not resolve hostname to IP address."


def update_index_html(ip_address):
    """
    Updates the index.html file with the current local IP address.
    """
    try:
        # Read the file content
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()

        # Replace the IP address in the JavaScript variable
        updated_content = re.sub(
            r'const ipAddress = ".*?";', f'const ipAddress = "{ip_address}";', content
        )

        # Write the updated content back to the file
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(updated_content)

        print(f"Updated index.html with IP address: {ip_address}")
    except FileNotFoundError:
        print("Error: index.html file not found")
    except PermissionError:
        print("Error: Permission denied when trying to write to index.html")
    except Exception as e:
        print(f"Error updating index.html: {e}")


def git_push():
    """
    Pushes the updated index.html to GitHub repository.
    Skips commit and push if no changes detected.
    """
    try:
        # Check if git is available
        subprocess.run(["git", "--version"], check=True, capture_output=True)

        # Add the changed file
        subprocess.run(["git", "add", "index.html"], check=True)

        # Check if there are any actual changes to commit
        diff_result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )
        if diff_result.returncode == 0:
            print("No changes detected, skipping commit and push")
            return

        # Commit with a message
        subprocess.run(["git", "commit", "-m", f"Update IP address"], check=True)

        # Push to remote repository
        subprocess.run(["git", "push", "origin", "master"], check=True)
        print("Successfully pushed changes to GitHub")
    except subprocess.CalledProcessError as e:
        if e.returncode == 128:  # No git repository
            print("Error: Not a git repository or git not installed")
        else:
            print(f"Git error: {e}")
    except Exception as e:
        print(f"Error during git push: {e}")


def main():
    """
    Main function that updates the local IP address and pushes to GitHub.
    """
    try:
        ip_address = get_local_ipv4_address()
        if ip_address != "Could not resolve hostname to IP address.":
            update_index_html(ip_address)
            git_push()
        else:
            print("Could not determine local IP address")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
