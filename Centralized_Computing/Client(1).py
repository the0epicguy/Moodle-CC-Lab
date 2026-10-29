import socket

# ===========================
# Client Configuration
# ===========================

HOST = "localhost"
PORT = 3000
BUFFER_SIZE = 1024

# Dictionary to map menu choice to server operation
OPERATIONS = {
    "1": "ADD",
    "2": "SUB",
    "3": "MUL",
    "4": "DIV",
    "5": "MOD",
    "6": "POW"
}


# ===========================
# Display Calculator Menu
# ===========================

def display_menu():

    print("\n" + "=" * 50)
    print("      CENTRALIZED CALCULATOR CLIENT")
    print("=" * 50)

    print("1. Addition (+)")
    print("2. Subtraction (-)")
    print("3. Multiplication (*)")
    print("4. Division (/)")
    print("5. Modulus (%)")
    print("6. Power (^)")
    print("7. Exit")

    print("=" * 50)


# ===========================
# Connect to Server
# ===========================

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:

    client.connect((HOST, PORT))

except ConnectionRefusedError:

    print("Unable to connect to the server.")
    print("Please start the server first.")

    exit()

print("\nConnected to Server Successfully!")

# ===========================
# Main Program Loop
# ===========================

try:

    while True:

        display_menu()

        # Get user's menu choice
        choice = input("Enter your choice : ").strip()

        # Exit option
        if choice == "7":

            client.send("exit".encode())

            print("\nDisconnecting from server...")

            break

        # Invalid menu option
        if choice not in OPERATIONS:

            print("\nInvalid Choice!\n")

            continue

        # Take numbers as input
        numbers = input(
            "\nEnter numbers separated by spaces : "
        ).strip()

        # Prevent empty input
        if numbers == "":

            print("\nInput cannot be empty.\n")

            continue

        # Build request

        # Example:
        #
        # ADD 10 20 30
        #
        request = OPERATIONS[choice] + " " + numbers

        # Send request to server
        client.send(request.encode())

        # Receive response
        response = client.recv(BUFFER_SIZE).decode()

        # Display server response
        print("\nServer Response")
        print("-" * 50)
        print(response)
        print("-" * 50)

except KeyboardInterrupt:

    print("\n\nClosing Client...")

except ConnectionResetError:

    print("\nConnection lost.")

finally:

    client.close()

    print("Client closed successfully.")