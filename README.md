# P2PY - Peer to Peer File Sharing with (BitTorrent)

This project implements an emulated peer to peer file sharing service, based on the [BitTorrent](https://wiki.theory.org/BitTorrentSpecification) specification. The purpose of the project is to learn how to build a peer to peer application using socket programming to solve file sharing bottlenecks in client-server models, in which multiple clients would download files hosted on a single server. The goal is to implement a decentralized process that allows clients to share (upload & download) files in segments (pieces) from other various clients purely through peer to peer TCP connections.

> **Contributors:**
>  - Richard Dong  
>  - Winston Ye   
>  - Leon Trieu

## ENVIRONMENT
- Python 3.8+, pip3 installed
- OS: Linux Ubuntu, Windows 10

## SETUP
1. Ensure you meet the necessary environment requires above

2. In the project root directory 'p2py', run the setup.py script by: 

		pip3 install -e ./

3. In the directory 'src', you can start the start the server (tracker):

		python3 tracker.py [src_port]
4. Start as many clients (peers) by opening a new terminal and run: 

		python3 client_handler.py [src_ip] [src_port] [tracker_ip] [tracker_port]
	* tracker_ip and port is visible in the tracker's command line window



## EXAMPLE TEST WORKFLOWS

### [Uploading a file]

*In the SRC directory..*

1. Start the tracker: `python3 tracker.py 8888` and note the IP address being served.
2. Start a client on a new terminal by: `python3 client_handler.py 127.0.0.1 8881 [tracker_ip] 8888`

**Assert the client connected successfully and the Command Line Interface is presented.**

3. Use the CLI to enter [3] and upload a file
4. Type to enter the provided sample file: `input/music.mp3`

**Assert the tracker received the request payload to start uploading a file**

**Assert the client is now seeding the file**

	...

### [Downloading a file]

*Continuing from uploading..*

1. With the tracker and current seeder terminal still active, start a new client: 
`python3 client_handler.py 127.0.0.2 8882 [tracker_ip] 8888`
2. Use the CLI to enter '1' to retrieve the latest list of torrents

**Assert the file 'music.mp3' is available in the list of torrents, and the list contains the seeder's id**

3. Use the CLI to enter '2' to download the torrent and enter its torrent id: '0'

**Assert the client is now downloading the file from the seeder**

4. After the download is successful, assert the newly downloaded file was written to the /output folder. The 
program prepends the client's peer id to the filename for distinguishing downloads.

**Assert the client started seeding automatically after the download was complete**

	...

### [Downloading from more than one peer]

*Continuing from downloading a file..*

1. Repeat the steps from [Downloading a file] with a different client ip & port

**Assert the list of torrents contains the additional seeder, and during the download it retrieves data from both available seeders.**

	...

### [Updating seeding status]

*Continuing from downloading from more than one peer...*

1. Choose two of the clients that are seeding, and enter 'CTRL+C' to stop seeding for both.
2. Start a new unique client_handler.py
3. Use the CLI to enter '1' to get the list of torrents. 
**Assert that the two seeders have left, and that the last seeder is the only one left seeding in the list**

## NON-LOCAL USAGE (OVER THE NETWORK)
p2py requires the specified the source port for the tracker/client to be a open port (through port forwarding) if you wish to host a tracker server/seed torrents. By default, the peer and tracker will use the 8888 port. For testing purposes on a single machine, you can host a tracker server and connect/seed/leech with other clients without port forwarding.
