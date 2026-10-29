import socket

# ==========================================
# Main Server Configuration
# ==========================================

# Main server listens for clients on port 3500
HOST = "0.0.0.0"
PORT = 3500

# Size of data received at a time
BUFFER_SIZE = 1024


# ==========================================
# Worker Server Configuration
# ==========================================

# Each operation is handled by a different
# worker server running on a different port.
#
# The Main Server will forward the client's
# request to the appropriate worker.

WORKERS = {
    "ADD": ("localhost", 3501),
    "SUB": ("localhost", 3502),
    "MUL": ("localhost", 3503),
    "DIV": ("localhost", 3504),
    "MOD": ("localhost", 3505),
    "POW": ("localhost", 3506)
}


# ==========================================
# Function to Communicate with Worker
# ==========================================

def send_to_worker(operation, numbers):
    """
    Sends the operation and numbers to the
    appropriate worker server.

    Returns the response received from
    the worker.
    """

    # Check whether the requested operation
    # has a corresponding worker server
    if operation not in WORKERS:
        return "ERROR: Invalid operation."

    # Get worker IP address and port
    worker_host, worker_port = WORKERS[operation]

    # Create a TCP socket for communication
    # between Main Server and Worker Server
    worker_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:

        # Connect to the appropriate worker
        worker_socket.connect(
            (worker_host, worker_port)
        )

        # Create the request that will be
        # sent to the worker.
        #
        # Example:
        # ADD 10 20 30
        request = operation + " " + " ".join(
            map(str, numbers)
        )

        # Send request to worker
        worker_socket.send(
            request.encode()
        )

        # Receive worker's response
        response = worker_socket.recv(
            BUFFER_SIZE
        ).decode()

        # Return response to the Main Server
        return response

    except ConnectionRefusedError:

        # This happens if the worker server
        # is not running
        return (
            f"ERROR: {operation} worker is "
            "not available."
        )

    except TimeoutError:

        # Handle worker timeout
        return (
            f"ERROR: {operation} worker "
            "timed out."
        )

    except Exception as error:

        # Handle any unexpected worker error
        return f"ERROR: Worker communication failed - {error}"

    finally:

        # Close the connection to the worker
        worker_socket.close()


# ==========================================
# Function to Validate Client Request
# ==========================================

def process_request(data):
    """
    Validates the request received from the
    client and forwards it to the correct
    worker server.
    """

    # Remove unnecessary spaces
    data = data.strip()

    # Check for empty request
    if not data:
        return "ERROR: Empty request."

    # Split request into parts
    parts = data.split()

    # The request must contain:
    #
    # operation + at least two numbers
    #
    # Example:
    # ADD 10 20
    if len(parts) < 3:
        return (
            "ERROR: Invalid request. "
            "At least two numbers are required."
        )

    # Extract operation
    operation = parts[0].upper()

    # Check whether operation is supported
    if operation not in WORKERS:
        return (
            "ERROR: Invalid operation. "
            "Supported operations are "
            "ADD, SUB, MUL, DIV, MOD and POW."
        )

    numbers = []

    # Convert each operand into an integer
    for value in parts[1:]:

        try:

            # Convert string to integer
            number = int(value)

            numbers.append(number)

        except ValueError:

            # Handle invalid numbers
            return (
                f"ERROR: '{value}' is not "
                "a valid integer."
            )

    # Forward the request to the
    # appropriate worker server
    return send_to_worker(
        operation,
        numbers
    )


# ==========================================
# Create Main Server Socket
# ==========================================

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

# Allow the server to reuse the port
# immediately after being stopped
server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

# Bind Main Server to port 3500
server.bind(
    (HOST, PORT)
)

# Start listening for client connections
server.listen(5)

# Set timeout so Ctrl + C can be detected
# even while the server is waiting for clients
server.settimeout(1)


# ==========================================
# Start Main Server
# ==========================================

print("=" * 60)
print("           DISTRIBUTED CALCULATOR")
print("              MAIN SERVER")
print("=" * 60)

print(f"Main Server listening on port {PORT}")

print("\nWorker Servers:")
print("Addition       -> 3501")
print("Subtraction    -> 3502")
print("Multiplication -> 3503")
print("Division       -> 3504")
print("Modulus        -> 3505")
print("Power          -> 3506")

print("\nWaiting for clients...")
print("Press Ctrl + C to stop the Main Server.\n")


# ==========================================
# Main Server Loop
# ==========================================

try:

    while True:

        try:

            # Wait for a client connection
            client_socket, client_address = (
                server.accept()
            )

        except socket.timeout:

            # Timeout allows the loop to continue
            # and detect Ctrl + C
            continue

        print(
            f"[CONNECTED] Client: "
            f"{client_address}"
        )

        try:

            # Keep the client connected
            # until it sends "exit"
            while True:

                # Receive request from client
                data = client_socket.recv(
                    BUFFER_SIZE
                ).decode()

                # Empty data means the client
                # disconnected
                if not data:

                    print(
                        f"[DISCONNECTED] "
                        f"{client_address}"
                    )

                    break

                # Remove unnecessary spaces
                data = data.strip()

                # Check for exit command
                if data.lower() == "exit":

                    print(
                        f"[DISCONNECTED] "
                        f"{client_address}"
                    )

                    break

                # Display the received request
                print(
                    f"[REQUEST] "
                    f"{client_address}: {data}"
                )

                # Process the request
                # and communicate with worker
                response = process_request(
                    data
                )

                # Send worker's response back
                # to the client
                client_socket.send(
                    response.encode()
                )

                # Display result on Main Server
                print(
                    f"[RESPONSE] {response}\n"
                )

        except ConnectionResetError:

            # Handle unexpected client
            # disconnection
            print(
                f"[ERROR] Client "
                f"{client_address} disconnected "
                "unexpectedly."
            )

        except BrokenPipeError:

            # Handle broken connection
            print(
                "[ERROR] Connection to client "
                "was lost."
            )

        finally:

            # Close the client connection
            client_socket.close()

            print(
                f"[CONNECTION CLOSED] "
                f"{client_address}\n"
            )


# ==========================================
# Handle Ctrl + C
# ==========================================

except KeyboardInterrupt:

    print("\n")
    print("Keyboard Interrupt detected.")
    print("Stopping Main Server...")


# ==========================================
# Shutdown
# ==========================================

finally:

    # Close the Main Server socket
    server.close()

    print("Main Server stopped successfully.")