import socket

# ===========================
# Server Configuration
# ===========================

HOST = "localhost"
PORT = 3000
BUFFER_SIZE = 1024

# Maximum numbers allowed in one request
MAX_NUMBERS = 100

# ===========================
# Function to validate numbers
# ===========================

def validate_numbers(tokens):

    numbers = []

    if len(tokens) < 2:
        return False, "Error: Enter at least two numbers."

    if len(tokens) > MAX_NUMBERS:
        return False, f"Error: Maximum {MAX_NUMBERS} numbers allowed."

    for token in tokens:

        # Reject decimal numbers
        if "." in token:
            return False, "Error: Decimal numbers are not allowed."

        try:
            number = int(token)

        except ValueError:
            return False, "Error: Enter only integers."

        # Prevent extremely large integers
        if abs(number) > 1_000_000_000:
            return False, "Error: Number too large."

        numbers.append(number)

    return True, numbers


# ===========================
# Perform requested operation
# ===========================

def calculate(operation, numbers):

    result = numbers[0]

    equation = str(numbers[0])

    # Addition
    if operation == "ADD":

        for number in numbers[1:]:
            result += number
            equation += f" + {number}"

    # Subtraction
    elif operation == "SUB":

        for number in numbers[1:]:
            result -= number
            equation += f" - {number}"

    # Multiplication
    elif operation == "MUL":

        for number in numbers[1:]:
            result *= number
            equation += f" * {number}"

    # Division
    elif operation == "DIV":

        for number in numbers[1:]:

            if number == 0:
                return False, "Error: Division by zero."

            result /= number
            equation += f" / {number}"

    # Modulus
    elif operation == "MOD":

        for number in numbers[1:]:

            if number == 0:
                return False, "Error: Modulus by zero."

            result %= number
            equation += f" % {number}"

    # Power
    elif operation == "POW":

        for number in numbers[1:]:

            result **= number
            equation += f" ^ {number}"

    else:

        return False, "Error: Invalid operation."

    return True, f"{equation} = {result}"


# ===========================
# Create Server Socket
# ===========================

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))

server.listen(5)

# Timeout allows Ctrl+C while waiting for clients
server.settimeout(1)

print("=" * 50)
print(" CENTRALIZED CALCULATOR SERVER")
print("=" * 50)
print(f"Listening on {HOST}:{PORT}")
print("Press Ctrl + C to stop the server.\n")

# ===========================
# Main Server Loop
# ===========================

try:

    while True:

        try:
            client_socket, address = server.accept()

        except socket.timeout:
            continue

        print(f"[CONNECTED] {address}")

        try:

            while True:

                # Receive data
                data = client_socket.recv(BUFFER_SIZE).decode().strip()

                # Client disconnected unexpectedly
                if not data:
                    print(f"[DISCONNECTED] {address}\n")
                    break

                # Client requested disconnect
                if data.lower() == "exit":
                    print(f"[DISCONNECTED] {address}\n")
                    break

                print(f"[REQUEST] {data}")

                # Split request
                parts = data.split()

                if len(parts) < 3:

                    client_socket.send(
                        "Error: Invalid request.".encode()
                    )

                    continue

                operation = parts[0]

                valid, result = validate_numbers(parts[1:])

                if not valid:

                    client_socket.send(result.encode())

                    print("[ERROR]", result)

                    continue

                numbers = result

                success, response = calculate(operation, numbers)

                client_socket.send(response.encode())

                if success:
                    print("[RESULT]", response)
                else:
                    print("[ERROR]", response)

                print()

        except ConnectionResetError:

            print(f"[ERROR] Client {address} disconnected unexpectedly.\n")

        finally:

            client_socket.close()

except KeyboardInterrupt:

    print("\nStopping server...")

finally:

    server.close()

    print("Server stopped successfully.")