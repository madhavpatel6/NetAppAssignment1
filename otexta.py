import socket, sys, hashlib, pickle
from cryptography.fernet import Fernet


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

    fernet_key = Fernet.generate_key()
    print("Encryption Key: ", fernet_key)
    f = Fernet(fernet_key)
    encrypted_question = f.encrypt(str(question).encode('utf-8'))
    print("Encrypted Question: ", encrypted_question)

    #compute MD5 Hash (Checksum)
    questionchecksum = checksum(encrypted_question)
    print("MD5 Hash: ", questionchecksum)

    #Create a question payload
    questionpayload = (fernet_key, encrypted_question, questionchecksum, host)
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
        if len(response) != 2:
            print('Invalid response payload.')
            s.close()
        print("Response: ", response)

        computedresponsechecksum = checksum(response[0])
        print("Computed Checksum: ", computedresponsechecksum)

        decrypted_response = f.decrypt(response[0])
        print("Decrypted response: ", decrypted_response)

        # Compare computed MD5 Hash with received hash
        if computedresponsechecksum != response[1]:
            print('Invalid response checksum.')
            s.close()
        print("Response payload checksum OK.")
        responsetext = decrypted_response
        print('Result: ', responsetext)
    s.close()


def checksum(val):
    hasher = hashlib.md5()
    hasher.update(str(val).encode('utf-8'))
    return hasher.hexdigest()

if __name__ == "__main__":
    main()