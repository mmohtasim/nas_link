import socket
import re
import subprocess
import sys
from datetime import datetime, timezone


def get_local_ipv4_address():
    """
    Retrieves the local IPv4 address of the machine.
    Returns the IP as a string, or None if detection fails.
    """
    try:
        # Get all network interfaces
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        # If we got a localhost address, try to find the actual local IP from eth3
        if ip_address.startswith("127.") or ip_address == "0.0.0.0":
            result = subprocess.run(
                ["ip", "-4", "addr", "show", "eth3"],
                capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                match = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", line)
                if match:
                    ip = match.group(1)
                    if not ip.startswith("127.") and not ip.startswith("169.254"):
                        return ip

        return ip_address
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return None


def update_index_html(ip_address):
    """
    Updates the index.html file with the current local IP address
    and the current timestamp.
    """
    try:
        # Read the file content
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()

        # Replace the IP address in the JavaScript variable
        updated_content = re.sub(
            r'const ipAddress = ".*?";', f'const ipAddress = "{ip_address}";', content
        )

        # Replace the lastUpdated timestamp
        now = datetime.now(timezone.utc).astimezone().isoformat()
        updated_content = re.sub(
            r'const lastUpdated = ".*?";', f'const lastUpdated = "{now}";', updated_content
        )

        # Write the updated content back to the file
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(updated_content)

        print(f"Updated index.html with IP address: {ip_address}")
    except FileNotFoundError:
        print("Error: index.html file not found")
        sys.exit(1)
    except PermissionError:
        print("Error: Permission denied when trying to write to index.html")
        sys.exit(1)
    except Exception as e:
        print(f"Error updating index.html: {e}")
        sys.exit(1)


def git_push(ip_address):
    """
    Pushes the updated index.html to GitHub repository.
    Skips commit and push if no changes detected.
    """
    try:
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

        # Commit with a descriptive message including the IP
        subprocess.run(
            ["git", "commit", "-m", f"Update IP to {ip_address}"],
            check=True
        )

        # Push to remote repository
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Successfully pushed changes to GitHub")
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during git push: {e}")
        sys.exit(1)


def main():
    """
    Main function that updates the local IP address and pushes to GitHub.
    """
    ip_address = get_local_ipv4_address()
    if ip_address is None:
        print("Could not determine local IP address")
        sys.exit(1)

    update_index_html(ip_address)
    git_push(ip_address)


if __name__ == "__main__":
    main()
