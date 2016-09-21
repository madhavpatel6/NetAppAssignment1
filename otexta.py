import socket, sys, hashlib, pickle


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: otexta \"Question\" \"ip_address_server\"")
    question = sys.argv[1]
    print("Question Asked: ", question)
    host = sys.argv[2]
    #Should port be a command line argument?
    port = 5000
    print("Server IP Address: ", host)
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host,port))
    except ConnectionRefusedError:
        sys.exit('Error: Invalid IP Address or Port. ')
    #compute MD5 Hash (Checksum)
    m = hashlib.md5()
    m.update(str(question).encode('utf-8'))
    checksum = m.digest()
    print("MD5 Hash: ", checksum)

    #Create a question payload
    questionpayload = ('Key Goes Here' ,question, checksum, host)
    print("Question Payload: ", questionpayload)

    #Pickle the tuple to a string
    questionpayloadstring = pickle.dumps(questionpayload)
    print("Question Payload String: ", questionpayloadstring)

    #Send the question
    s.send(questionpayloadstring)

    #Wait for a Response
    data = s.recv(size)
    if data:
        response = pickle.loads(data)
        if(len(response) != 2):
            print('Invalid response payload.')
            s.close()
        print("Response: ", response)

        m = hashlib.md5()
        m.update(str(response[0]).encode('utf-8'))
        computedresponsechecksum = m.digest()
        print("Computed Checksum: ", computedresponsechecksum)

        # Compare computed MD5 Hash with received hash
        if computedresponsechecksum != response[1]:
            print('Invalid response checksum.')
            s.close()

        responsetext = response[0]
        print('Result: ', responsetext)
    s.close()

if __name__ == "__main__":
    main()