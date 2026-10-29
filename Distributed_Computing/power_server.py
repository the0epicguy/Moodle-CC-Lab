import socket

# ==========================================
# Server Configuration
# ==========================================

HOST = "0.0.0.0"

# Port assigned to Power Worker
PORT = 3506

BUFFER_SIZE = 1024


# ==========================================
# Power Function
# ==========================================

def calculate(numbers):
    """
    Performs power operation from left
    to right.

    Example:

    2 3 2

    becomes:

    2 ^ 3 ^ 2

    calculated as:

    (2 ^ 3) ^ 2 = 64
    """

    # Start with the first number
    result = numbers[0]

    # Create equation
    equation = str(numbers[0])

    # Process remaining numbers
    for number in numbers[1:]:

        # Perform power operation
        result **= number

        # Add operation to equation
        equation += f" ^ {number}"

    return f"{equation} = {result}"


# ==========================================
# Create Server
# ==========================================

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind((HOST, PORT))

server.listen(5)

server.settimeout(1)


# ==========================================
# Start Server
# ==========================================

print("=" * 50)
print("          POWER WORKER SERVER")
print("=" * 50)

print(f"Listening on port {PORT}")
print("Press Ctrl + C to stop.\n")


# ==========================================
# Server Loop
# ==========================================

try:

    while True:

        try:

            client_socket, address = server.accept()

        except socket.timeout:

            continue

        print(f"[CONNECTED] {address}")

        try:

            data = client_socket.recv(
                BUFFER_SIZE
            ).decode().strip()

            print(f"[REQUEST] {data}")

            parts = data.split()

            if len(parts) < 3:

                response = (
                    "ERROR: At least two numbers "
                    "are required."
                )

            else:

                numbers = []

                try:

                    for value in parts[1:]:
                        numbers.append(int(value))

                    response = calculate(numbers)

                except ValueError:

                    response = (
                        "ERROR: Invalid integer."
                    )

            client_socket.send(
                response.encode()
            )

            print(f"[RESPONSE] {response}\n")

        except ConnectionResetError:

            print(
                "[ERROR] Main Server disconnected."
            )

        finally:

            client_socket.close()


except KeyboardInterrupt:

    print("\nStopping Power Worker...")


finally:

    server.close()

    print("Power Worker stopped.")