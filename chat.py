import sys #to take command line arguments
import json #to send dictionary to clients
import select #event loops to send and receive messages at the same time
import datetime #for timestamp
from socket import *

def sendTables(tabl, ssock):
	for client in tabl:
		if tabl[client][1] == "online":
			cliAddr = table[client][0]
			ssock.sendto((json.dumps(table)).encode(), cliAddr)

def sendSaveReq(csock, saddr, tonick, fromnick, saveMsg, timestamp):
	splittedSave = saveMsg.split(" ", 2)
	sendSaveMsg = tonick + " " + fromnick + ": " + timestamp + " " + splittedSave[2]
	csock.sendto(sendSaveMsg, saddr)

if sys.argv[1] == "-s" and len(sys.argv) == 3:
	servPort = int(sys.argv[2])
	servSocket = socket(AF_INET, SOCK_DGRAM)
	servSocket.bind(('', servPort))
	#make table (dictionary) to hold nicknames, IPaddrs, ports
	table = {}
	#make dictionary to hold offline messages
	offlineMsgs = {}
	while True:
		#receive client info, send welcome to new client and send updated table to all clients
		servRecvMsg, cliAddr = servSocket.recvfrom(2048)	
		servSplitted = servRecvMsg.split(" ", 1)
		if servSplitted[0] == "reg":
			if servSplitted[1] not in table:
				#send welcome, send out tables
				table[servSplitted[1]] = (cliAddr, "online")
				welcomeMsg = "[Welcome. You have been registered.]"
				servSocket.sendto(welcomeMsg.encode(), cliAddr)
				sendTables(table, servSocket)
			elif servSplitted[1] in offlineMsgs:
				#send client their saved messages, send out tables
				table[servSplitted[1]] = (cliAddr, "online")
				haveMailMsg = "[You have messages.]" + "\n" + offlineMsgs[servSplitted[1]]
				servSocket.sendto(haveMailMsg.encode(), cliAddr)
				sendTables(table, servSocket)
		if servSplitted[0] == "dereg":
			#update table, send bye, send out tables
			table[servSplitted[1].strip()] = (cliAddr, "offline")
			byeMsg = "[You are offline. Bye.]"
			servSocket.sendto(byeMsg.encode(), cliAddr)
			sendTables(table, servSocket)
		if servSplitted[0] in table:
			#add message to offlineMsgs
			recipient = servSplitted[0]
			if recipient in offlineMsgs:
				offlineMsgs[recipient] = offlineMsgs[recipient] + servSplitted[1]
			else:
				offlineMsgs[recipient] = servSplitted[1]
elif sys.argv[1] == "-c" and len(sys.argv) == 6:
	#send server nickname
	serverAddr = (sys.argv[3], int(sys.argv[4]))
	clientSocket = socket(AF_INET, SOCK_DGRAM)
	myNick = sys.argv[2]
	regMsg = "reg " + myNick
	clientSocket.sendto(regMsg.encode(), serverAddr)
	#receive welcome
	recvMsg, serverAddr = clientSocket.recvfrom(2048)
	print recvMsg.decode()
	#receive table
	recvMsg, serverAaddr = clientSocket.recvfrom(2048)
	myTable = json.loads(recvMsg.decode())
	print "[Client table updated.]"

	#list to be used in select()
	readFroms = [clientSocket, sys.stdin]

	#forever loop that prints messages received to stdout and reads stdin to send messages to other clients
	while True:
		#use select so that readline() and recvfrom() don't block each other 
		readable, writable, exceptional = select.select(readFroms, [], [])
		if sys.stdin in readable:
			line = sys.stdin.readline()
			if line:
				#case: sending a message to another client
				splitted = line.split(" ", 2)
				if splitted[0] == "send":
					nick = splitted[1]
					if nick in myTable:
						if myTable[nick][1] == "online":
							myMsg = myNick + ": " + splitted[2]
							clientSocket.sendto(myMsg.encode(), (myTable[nick][0][0], myTable[nick][0][1]))
						else:
							#send save-message request automatically
							time = str(datetime.datetime.now())
							sendSaveReq(clientSocket, serverAddr, nick, myNick, line, time)
				#case: deregistering
				if line.strip() == "dereg " + myNick:
					clientSocket.sendto(line.encode(), serverAddr)
					recvMsg, addr = clientSocket.recvfrom(2048)
					print recvMsg.decode()
					#hang until client registers again
					rereg = "reg " + myNick + "\n"
					while sys.stdin.readline() != rereg:
						pass
					#if the same terminal window registers again with reg <myNick>
					clientSocket.sendto(regMsg.encode(), serverAddr)
		elif clientSocket in readable:
			#receive messages from server and clients
			recvMsg, addr = clientSocket.recvfrom(2048)
			recvMsg = recvMsg.decode()
			#case: message is from server
			if addr == serverAddr:
				#try to unpack dict, if it's not a dict just print
				try:
					myTable = json.loads(recvMsg)
					print [Client table updated.]"
				except ValueError: 
					print recvMsg,
			#case: message is from another client
			else:
				print recvMsg,

else:
	print "Use the correct command line arguments."
