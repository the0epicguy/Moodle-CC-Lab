import socket

# ==========================================
# Server Configuration
# ==========================================

# Listen on all network interfaces
HOST = "0.0.0.0"

# Port assigned to the Addition Worker
PORT = 3501

# Maximum amount of data received at once
BUFFER_SIZE = 1024


# ==========================================
# Addition Function
# ==========================================

def calculate(numbers):
    """
    Adds all numbers received from the
    Main Server.
    """

    # Start with the first number
    result = numbers[0]

    # Create the equation using the first number
    equation = str(numbers[0])

    # Add each remaining number
    for number in numbers[1:]:
        result += number
        equation += f" + {number}"

    # Return equation and result
    return f"{equation} = {result}"


# ==========================================
# Create Server Socket
# ==========================================

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

# Allow the port to be reused immediately
server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

# Bind the worker to port 3501
server.bind((HOST, PORT))

# Listen for connections from Main Server
server.listen(5)

# Timeout allows Ctrl+C to work
server.settimeout(1)


# ==========================================
# Start Server
# ==========================================

print("=" * 50)
print("       ADDITION WORKER SERVER")
print("=" * 50)
print(f"Listening on port {PORT}")
print("Press Ctrl + C to stop.\n")


# ==========================================
# Main Server Loop
# ==========================================

try:

    while True:

        try:

            # Wait for Main Server connection
            client_socket, address = server.accept()

        except socket.timeout:

            # Continue checking for Ctrl+C
            continue

        print(f"[CONNECTED] {address}")

        try:

            # Receive request
            data = client_socket.recv(
                BUFFER_SIZE
            ).decode().strip()

            print(f"[REQUEST] {data}")

            # Split request
            parts = data.split()

            # Make sure operation and at least
            # two numbers were received
            if len(parts) < 3:

                response = (
                    "ERROR: At least two numbers "
                    "are required."
                )

            else:

                # Ignore the operation name
                # because this worker only performs ADD
                numbers = []

                try:

                    for value in parts[1:]:
                        numbers.append(int(value))

                    # Calculate result
                    response = calculate(numbers)

                except ValueError:

                    response = (
                        "ERROR: Invalid integer."
                    )

            # Send result to Main Server
            client_socket.send(
                response.encode()
            )

            print(f"[RESPONSE] {response}\n")

        except ConnectionResetError:

            print(
                "[ERROR] Main Server disconnected."
            )

        finally:

            # Close connection with Main Server
            client_socket.close()


except KeyboardInterrupt:

    print("\nStopping Addition Worker...")


finally:

    server.close()

    print("Addition Worker stopped.")