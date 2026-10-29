import socket

# ==========================================
# Server Configuration
# ==========================================

HOST = "0.0.0.0"

# Port assigned to Subtraction Worker
PORT = 3502

BUFFER_SIZE = 1024


# ==========================================
# Subtraction Function
# ==========================================

def calculate(numbers):
    """
    Subtracts every number from the first
    number from left to right.
    """

    # Start with the first number
    result = numbers[0]

    # Create equation
    equation = str(numbers[0])

    # Subtract remaining numbers
    for number in numbers[1:]:

        result -= number

        equation += f" - {number}"

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
print("      SUBTRACTION WORKER SERVER")
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

    print("\nStopping Subtraction Worker...")


finally:

    server.close()

    print("Subtraction Worker stopped.")