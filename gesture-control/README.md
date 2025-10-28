# Network Traffic Visualizer

This project is a real-time network traffic visualizer that captures network packets from your machine and displays a summary of the protocol distribution in a web-based interface.

## Features

*   **Real-time Packet Sniffing:** Captures network packets on the local machine.
*   **Protocol Analysis:** Identifies the protocol of each captured packet (TCP, UDP, ICMP, or other).
*   **Web-Based Visualization:** Displays a pie chart of the protocol distribution that updates every minute.
*   **Modern Tech Stack:** Built with Python, FastAPI, and Chart.js.

## How It Works

The project consists of two main parts: a backend server and a frontend web interface.

### Backend

The backend is a Python application built with the **FastAPI** framework. It has two main responsibilities:

1.  **Packet Sniffing:** The application uses the **Scapy** library to capture network packets in a background thread. For each captured packet, it identifies the protocol and updates a counter for that protocol.

2.  **API Server:** The FastAPI server exposes a single API endpoint, `/data`, which returns a JSON object containing the latest protocol counts. For example:

    ```json
    {
        "TCP": 120,
        "UDP": 80,
        "ICMP": 10,
        "OTHER": 25
    }
    ```

### Frontend

The frontend is a single-page web application built with HTML, CSS, and JavaScript.

*   **HTML:** The `index.html` file provides the basic structure of the web page, including a `<canvas>` element where the chart is rendered.
*   **JavaScript:** The `script.js` file contains the logic for the frontend. It uses the **Chart.js** library to create a pie chart. Every minute, it sends a request to the `/data` endpoint of the backend to get the latest protocol counts and updates the chart with the new data.

## Networking Concepts

This project visualizes the distribution of different network protocols. Here's a brief explanation of the protocols that are being tracked:

### TCP (Transmission Control Protocol)

TCP is one of the main protocols of the Internet protocol suite. It is a **connection-oriented** protocol, which means that it establishes a connection between two devices before sending data. TCP guarantees that all data will be delivered in the correct order and without errors. It is used for applications that require high reliability, such as web browsing, email, and file transfer.

### UDP (User Datagram Protocol)

UDP is another common protocol in the Internet protocol suite. Unlike TCP, it is a **connectionless** protocol. This means that it sends data without establishing a connection first. UDP is faster than TCP but does not guarantee that data will be delivered or that it will be in the correct order. It is used for applications that are sensitive to delay, such as video streaming, online gaming, and DNS.

### ICMP (Internet Control Message Protocol)

ICMP is a network protocol used by network devices, like routers, to send error messages and operational information. For example, when you use the `ping` command to check if a server is online, your computer sends ICMP messages to the server. ICMP is not typically used to exchange data between applications.

## Setup and Usage

Follow these steps to set up and run the project on your local machine.

### Prerequisites

*   **Python 3:** Make sure you have Python 3 installed on your machine.
*   **Npcap:** This is a library for packet capturing on Windows. Download and install it from the [official Npcap website](https://npcap.com/#download). During installation, make sure to check the box that says **"Install Npcap in WinPcap API-compatible Mode"**.

### Installation

1.  **Clone the repository or download the source code.**

2.  **Navigate to the project directory:**

    ```
    cd path\to\project
    ```

3.  **Install the required Python libraries:**

    ```
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Open a command prompt or terminal as an administrator.** This is required for packet sniffing.

2.  **Navigate to the project directory.**

3.  **Run the application:**

    ```
    python app.py
    ```

4.  **View the visualization:**

    Open your web browser and go to `http://127.0.0.1:5000`.

## File Structure

```

├── app.py               # The main FastAPI application
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # The HTML for the frontend
└── static/
    ├── style.css         # CSS styles for the frontend
    └── script.js         # JavaScript for the frontend

```