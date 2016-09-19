
import sys, socket, pickle, hashlib

def main():
    host = ''
    port = 5000
    size = 1024
    backlog = 1
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host,port))
    s.listen(backlog)
    while 1:
        hasher = hashlib.md5()
        client, address = s.accept()
        print("Client Connected: ", address)
        data = client.recv(size)
        if data:
            #Load the data into a tuple
            questionpayload = pickle.loads(data)
            print("Question Payload: ", questionpayload)

            #Compute the MD5 Hash
            hasher.update(str(questionpayload[1]).encode('utf-8'))
            computedchecksum = hasher.digest()
            print("Computed Checksum: ", computedchecksum)

            #Compare computed MD5 Hash with received hash
            if(computedchecksum != questionpayload[2]):
                #If we compute a different MD5 Hash then we send an error message back to the client and close the client connection
                print('Invalid Check Sum Detected!')
                client.send(b'What the hell man. That was a jank message.')
                client.close()
                continue;
            #Otherwise send the question to wolfram alpha


            #Send response back
            client.send(data)
        client.close()

if __name__ == "__main__" : main()