# c-c-chat-client

A simple peer-to-peer chat client implented with UDP sockets.

Run  
`python chat.py -s <port>` to start the server
`python chat.py -c <nickname> <server-ip> <server-port> <client-port> to join the chat

Inside the chat,  
The command `dereg <your nickname>` will mark you as offline to the other users in the chat. They will still be able send you messages, and those messages will be saved by the server and displayed to you when you come back online with the command `reg <your nickname>`.  
If you close the program and re-enter the same chatroom, your offline messages will be displayed to you. (Yes, if someone snipes your nick they'll see your old messages.)

Note: Although this program uses UDP sockets, it does not use ACKs to check if messages were lost.
