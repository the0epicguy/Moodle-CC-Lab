# Distributed Computing – Assignment 1

## 1. Overview

This project demonstrates a distributed-style calculator using Python TCP sockets. Instead of performing every calculation in one server, the application uses a **main server** to route requests to separate **worker servers**.

The project contains eight Python files:

- `Client(2).py` — provides the calculator menu and sends requests to the main server.
- `main_server.py` — receives client requests, validates them, chooses the correct worker, forwards the request, and sends the worker's response back to the client.
- `addition_server.py` — addition worker, port `3501`.
- `subtraction_server.py` — subtraction worker, port `3502`.
- `multiplication_server.py` — multiplication worker, port `3503`.
- `division_server.py` — division worker, port `3504`.
- `modulus_server.py` — modulus worker, port `3505`.
- `power_server.py` — power worker, port `3506`.

The client connects to the main server on port `3500`. The main server communicates with the appropriate worker over TCP.

**Important:** As currently configured, the main server connects to workers using `localhost`. Therefore, the files can demonstrate the main-server/worker architecture with separate processes on one computer. To run the workers on separate computers, update the worker addresses in `main_server.py` to their actual network IP addresses and configure the network/firewall appropriately.

## 2. Requirements

- Python 3
- A terminal or command prompt
- Ports `3500` through `3506` available
- All eight Python files in the same project folder (or use the correct path when launching each file)

The programs use Python's built-in `socket` module. No third-party packages are required.

## 3. How to run the files

Start each server in its own terminal window and leave it running. You need six worker-server terminals, one main-server terminal, and one client terminal.

### Step 1: Open a terminal in the project folder

Make sure all eight files are present in the folder. On Windows, open PowerShell or Command Prompt in that folder.

### Step 2: Start all six worker servers

Open a separate terminal for each worker and run these commands:

**Terminal 1 — Addition worker**

```bash
python addition_server.py
```

**Terminal 2 — Subtraction worker**

```bash
python subtraction_server.py
```

**Terminal 3 — Multiplication worker**

```bash
python multiplication_server.py
```

**Terminal 4 — Division worker**

```bash
python division_server.py
```

**Terminal 5 — Modulus worker**

```bash
python modulus_server.py
```

**Terminal 6 — Power worker**

```bash
python power_server.py
```

If your system uses `python3` rather than `python`, replace `python` with `python3`.

Each terminal should display the worker name and the port on which it is listening. Keep all six terminals open.

### Step 3: Start the main server

Open another terminal in the project folder and run:

```bash
python main_server.py
```

It should indicate that the main server is listening on port `3500` and list the worker ports. Keep this terminal open.

### Step 4: Start the client

Open one more terminal in the project folder and run:

```bash
python "Client(2).py"
```

The client should connect to the main server and display the distributed calculator menu.

### Step 5: Perform calculations

Choose an operation from the menu and enter at least two integers separated by spaces.

Example: choose `1` for addition and enter `10 20 30`. The client should display a response similar to:

```text
10 + 20 + 30 = 60
```

The main-server terminal should show the incoming request and the response. The corresponding worker terminal should show the request it received and the result it returned.

### Step 6: Exit and stop the servers

- Enter `7` in the client menu to disconnect.
- Press `Ctrl+C` in the main-server terminal.
- Press `Ctrl+C` in each worker-server terminal to stop the workers.

## 4. What each file contains

### `Client(2).py`

- Defines the main server address (`localhost`) and port (`3500`).
- Displays a menu for addition, subtraction, multiplication, division, modulus, power, and exit.
- Maps menu choices to operation names such as `ADD`, `SUB`, and `MUL`.
- Sends a request such as `ADD 10 20 30` to the main server.
- Receives and displays the response.

### `main_server.py`

- Listens for client connections on port `3500`.
- Defines a mapping from each operation to its worker host and port.
- Checks that a request has an operation and at least two integer operands.
- Sends the request to the selected worker server.
- Receives the worker's response and returns it to the client.
- Reports errors such as an invalid operation or an unavailable worker.
- Closes client and server sockets when connections end or the program is stopped.

### Worker-server files

Each worker server creates a TCP listening socket, accepts a connection from the main server, reads a request, performs its assigned calculation, sends a response, and closes the connection.

| File | Port | Function |
|---|---:|---|
| `addition_server.py` | 3501 | Adds the numbers from left to right. |
| `subtraction_server.py` | 3502 | Subtracts each later number from the running result. |
| `multiplication_server.py` | 3503 | Multiplies the numbers from left to right. |
| `division_server.py` | 3504 | Divides from left to right and checks for a zero divisor. |
| `modulus_server.py` | 3505 | Applies modulus from left to right and checks for a zero divisor. |
| `power_server.py` | 3506 | Applies exponentiation from left to right. |

## 5. Example tests

| Menu choice | Operation | Example input | Expected response |
|---|---|---|---|
| 1 | Addition | `10 20 30` | `10 + 20 + 30 = 60` |
| 2 | Subtraction | `20 5 3` | `20 - 5 - 3 = 12` |
| 3 | Multiplication | `2 3 4` | `2 * 3 * 4 = 24` |
| 4 | Division | `100 2 5` | `100 / 2 / 5 = 10.0` |
| 5 | Modulus | `17 5` | `17 % 5 = 2` |
| 6 | Power | `2 3` | `2 ^ 3 = 8` |

Also test division and modulus with a zero in a divisor position to check the error response.

## 6. What these files are used for

The project illustrates a main-server/worker architecture:

1. The client submits a calculation request.
2. The main server receives and validates the request.
3. The main server routes the request to the worker assigned to that operation.
4. The worker performs the calculation and sends the result to the main server.
5. The main server returns the result to the client.

The design separates responsibilities between multiple worker services. It illustrates how a task can be divided among different service processes rather than being handled entirely by one calculation server.

In the current configuration, all processes can run on one computer, which is useful for a lab demonstration. A demonstration across multiple physical computers requires configuring the worker addresses in `main_server.py` with the appropriate network IP addresses.

## 7. Limitations and notes

- The main server's worker map uses `localhost`, so the workers must be reachable on the same computer unless the map is changed.
- Each server handles connections sequentially; concurrency is not implemented.
- The code assumes each request and response fits into one TCP `recv()` call. TCP does not guarantee message boundaries, so this is a simplified lab protocol.
- The power worker can produce very large results for some inputs. Use small numbers during testing.
- The worker programs rely on the main server to route the correct operation to the correct worker.

## 8. Conclusion

This project demonstrates a distributed-style calculator in which a main server coordinates six operation-specific worker servers over TCP. The client sends a request to the main server, the main server forwards it to the appropriate worker, and the response is returned to the client. Running the components in separate terminals makes the communication flow visible for the lab demonstration.
