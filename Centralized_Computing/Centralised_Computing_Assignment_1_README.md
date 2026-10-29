# Centralised Computing – Assignment 1

## 1. Overview

This project demonstrates **centralised computing** using a calculator application built with Python TCP sockets.

The application has two programs:

- `Server(1).py` — the central server. It receives calculation requests, validates the input, performs the requested operation, and sends the result back.
- `Client(1).py` — the client program. It displays a menu, accepts numbers from the user, sends the request to the server, and displays the server's response.

Both programs currently use `localhost` and port `3000`. This means the client and server run on the same computer. The same design can be adapted to run across computers by configuring the server's network address and allowing the connection through the relevant firewall.

## 2. Requirements

- Python 3
- A terminal or command prompt
- Port `3000` available on the computer

The programs use Python's built-in `socket` module, so no third-party Python packages are required.

## 3. How to run the files

### Step 1: Keep both files together

Place `Server(1).py` and `Client(1).py` in the same folder. Open a terminal or command prompt in that folder.

### Step 2: Start the server first

Run:

```bash
python "Server(1).py"
```

On some systems, use `python3` instead of `python`:

```bash
python3 "Server(1).py"
```

The server should display a message indicating that it is listening on `localhost:3000`. Keep this terminal open while using the client.

### Step 3: Open a second terminal and start the client

In a second terminal, navigate to the same folder and run:

```bash
python "Client(1).py"
```

Or, where required:

```bash
python3 "Client(1).py"
```

The client should report that it connected successfully and display the calculator menu.

### Step 4: Perform a calculation

Choose an operation by entering its menu number. Then enter at least two integers separated by spaces.

Example:

```text
Enter your choice : 1
Enter numbers separated by spaces : 10 20 30
```

The client should display a server response similar to:

```text
10 + 20 + 30 = 60
```

### Step 5: Exit

Enter `7` in the client menu to disconnect. To stop the server, press `Ctrl+C` in the server terminal.

### Troubleshooting

- **Unable to connect:** Start the server before starting the client.
- **Address already in use:** Another process may be using port `3000`; stop that process or change `PORT` in both files to the same unused port.
- **Command not found:** Check that Python 3 is installed and available on your PATH; try `python3` if `python` does not work.
- **Invalid input:** Enter at least two integers separated by spaces. Decimal values are not accepted.
- **Server and client use different ports:** Ensure `PORT` has the same value in both files.

## 4. What the files contain

### `Server(1).py`

1. **Configuration:** Defines the host, port, buffer size, and maximum number of integers accepted in one request.
2. **Input validation (`validate_numbers`):** Checks that at least two integers are provided, limits the request to 100 numbers, rejects decimal notation and non-integer input, and rejects individual numbers whose absolute value exceeds 1,000,000,000.
3. **Calculation (`calculate`):** Implements addition (`ADD`), subtraction (`SUB`), multiplication (`MUL`), division (`DIV`), modulus (`MOD`), and power (`POW`).
4. **Socket setup:** Creates a TCP socket, binds it to `localhost:3000`, and listens for incoming connections.
5. **Request handling:** Receives a request, separates the operation from the numbers, validates the numbers, calculates the result, and sends a response to the client.
6. **Error handling and cleanup:** Handles common disconnects and `Ctrl+C`, then closes the sockets.

### `Client(1).py`

1. **Configuration:** Uses the same host, port, and buffer size as the server.
2. **Operation mapping:** Maps menu choices 1–6 to the server operations.
3. **Menu:** Displays the supported operations and an exit option.
4. **Connection:** Connects to the server over TCP.
5. **Request creation:** Accepts numbers and builds a request such as `ADD 10 20 30`.
6. **Communication:** Sends the request to the server, receives the response, and displays it.
7. **Cleanup:** Closes the client socket when the program exits.

## 5. What these files are used for

The files demonstrate the client-server model:

- The **client** is the interface used to submit a request.
- The **server** is the central point where calculations and validation take place.
- TCP sockets provide communication between the two programs.
- The client receives the result rather than performing the calculation itself.

This is an example of centralised computing because the processing logic is located on the server. In this version, both programs run on one computer using `localhost`, so the project demonstrates the architecture locally rather than across multiple physical computers.

## 6. Operations and sample tests

| Menu choice | Operation | Example input | Expected result |
|---|---|---|---|
| 1 | Addition | `10 20 30` | `10 + 20 + 30 = 60` |
| 2 | Subtraction | `20 5 3` | `20 - 5 - 3 = 12` |
| 3 | Multiplication | `2 3 4` | `2 * 3 * 4 = 24` |
| 4 | Division | `100 2 5` | `100 / 2 / 5 = 10.0` |
| 5 | Modulus | `17 5` | `17 % 5 = 2` |
| 6 | Power | `2 3` | `2 ^ 3 = 8` |

For division and modulus, test a zero in a divisor position to verify that the server returns an error instead of performing the operation.

## 7. Notes and limitations

- The server handles connected clients sequentially; it does not process multiple clients concurrently.
- The program uses simple `send` and `recv` calls and assumes each request/response is received in one exchange. TCP does not guarantee message boundaries, so this is a simplified demonstration rather than a robust production protocol.
- The power operation can create very large results for some inputs. Use small numbers for demonstrations.
- `localhost` means the server is reachable from the same computer. For a multi-computer demonstration, the server host configuration and network/firewall settings would need to be changed appropriately.
- The division operation may return a floating-point result.

## 8. Conclusion

The project demonstrates centralised computing through a Python TCP client-server calculator. The client collects user input and displays the response, while the server validates requests, performs calculations, and returns results. The two terminals provide visible evidence of the request and response flow for the lab assignment.
