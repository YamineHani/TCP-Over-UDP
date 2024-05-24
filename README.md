# TCP Over UDP

## Introduction
This project is an implementation of a Reliable Data Transfer Protocol using Python's socket programming. The protocol ensures reliable transmission of data over an unreliable network, handling packet loss and corruption.

## Description

### 3-Way Handshake
The protocol employs a 3-way handshake for connection establishment between the client and server. This ensures synchronization of sequence numbers and acknowledgment numbers.

- The server waits for SYN packets from the client, responds with SYN-ACK, and awaits the final ACK from the client to complete the handshake.
  

### Data Transmission
Reliable data transmission is achieved through sequence numbers and acknowledgments. Each packet includes a sequence number and its checksum is calculated and appended to the existing packet. The receiver sends acknowledgments with the expected sequence number for the next packet.

- To simulate real-world network conditions, the protocol incorporates mechanisms to induce packet loss and corruption. Random packet loss and corruption probabilities are defined to mimic unreliable network behavior. The `lose_packet()` and `corrupt_packet()` functions determine whether a packet should be lost or corrupted based on predefined probabilities.
- Stop-and-wait algorithm is applied in data transmission.

### HTTP Protocol

#### Database Integration with HTTP Protocol
This section covers the integration of a MySQL database with an HTTP server implemented in Python. The server handles HTTP GET and POST requests to retrieve and manipulate student data stored in the database.

#### Database Setup
- A MySQL database named "student" is created to store student information. The database contains a table named "students" with columns for student ID (primary key) and name.

#### HTTP Server Functions

1. **Handle GET Request**
   - The `handle_get_request` function extracts the student ID from the HTTP request URL and queries the database for the corresponding student name.
   - If the student is found, the server responds with an HTTP 200 OK status code and the student's name. Otherwise, it returns a 404 Not Found status code.

2. **Handle POST Request**
   - The `handle_post_request` function extracts the student name from the HTTP request payload and inserts it into the database.
   - Upon successful insertion, the server responds with an HTTP 201 Created status code. In case of a database error, it returns a 500 Internal Server Error status code.

#### Integration with HTTP Server
The HTTP server implemented in Python utilizes the `mysql.connector` module to establish a connection to the MySQL database.

- Upon receiving a GET or POST request, the server invokes the respective handler function to retrieve or manipulate student data.

#### HTTP Response
The server provides appropriate HTTP status codes to indicate the success or failure of each request, ensuring effective communication between clients and the database-backed server.

### Termination
The protocol utilizes a 2-way handshake for connection termination. Either party can initiate the termination process by sending a FIN packet.

- Upon receiving a FIN packet, the receiver acknowledges it and responds with its own FIN packet to initiate the termination process.

## Conclusion
The implementation of the Reliable Data Transfer Protocol demonstrates robust error detection and recovery mechanisms to ensure reliable communication over unreliable networks. By simulating packet loss and corruption and incorporating timeout mechanisms, the protocol achieves reliable data transmission while maintaining protocol simplicity. Further optimizations and enhancements can be explored to adapt the protocol for specific network environments and requirements.

## Setup and Usage

### Prerequisites
- Python 3.x
- MySQL server
- `mysql.connector` module

### Installation

1. Install the required Python packages:
    ```bash
    pip install mysql-connector-python
    ```

2. Set up the MySQL database with your credentials.
   

### Running the Server
1. Start the server:
    ```bash
    python server.py
    ```

### Running the Client
1. Start the client:
    ```bash
    python client.py
    ```
