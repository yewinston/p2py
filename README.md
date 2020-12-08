# p2py
 Peer2Peer File-Sharing (BitTorrent) implemented in Python

DETAILS:
[project synopsis here]

ENVIRONMENT:
Python 3.7+
Linux Ubuntu OS / Windows OS

SETUP:
1. Ensure you have the necessary environment requirements (including pip3)

2. In the 'p2py' directory, run the command 'pip3 install -e ./' which will setup the python package and requirements.

3. cd to the 'src' directory, and to start the server & clients:

- Start the tracker (server) by running the command 
    'tracker.py [src_ip] [src_port]'

- Create as many peers as needed by running the command (in new terminals)
    'client_handler.py [src_ip] [src_port] [tracker_ip] [tracker_port]'

4. Use the 'help' feature in client_handler for specific command details

TESTS:
1. In the 'test' directory, run the command 'pytest run_tests.py'

EXAMPLE UPLOAD & DOWNLOAD WORKFLOW:
[steps here]