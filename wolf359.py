import sys, socket, pickle, hashlib
import wolframalpha

def main():
    host = ''
    port = 5000
    size = 1024
    backlog = 1
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host,port))
    s.listen(backlog)
    wclient = wolframalpha.Client('V76GGA-6VAXGW25UP')
    # res = wclient.query('temperature in Washington, DC on October 3, 2012')
    # for pod in res.pods:
    #    for sub in pod.subpods:
    #        print(sub.text)
    while 1:
        hasher = hashlib.md5()
        client, address = s.accept()
        print("Client Connected: ", address)
        data = client.recv(size)
        if data:
            # Load the data into a tuple
            questionpayload = pickle.loads(data)
            print("Question Payload: ", questionpayload)

            if len(questionpayload) != 4:
                client.end(b'Error: Invalid payload packet.')
                client.close()
                continue;

            # Compute the MD5 Hash
            hasher.update(str(questionpayload[1]).encode('utf-8'))
            computedchecksum = hasher.digest()
            print("Computed Checksum: ", computedchecksum)

            # Compare computed MD5 Hash with received hash
            if computedchecksum != questionpayload[2]:
                #If we compute a different MD5 Hash then we send an error message back to the client and close the client connection
                print('Invalid Check Sum Detected!')
                client.send(b'Error: Invalid question checksum.')
                client.close()
                continue;

            # Otherwise send the question to wolfram alpha
            question = questionpayload[1]
            print("Question: ", question)

            res = wclient.query(question)
            resultText = ""
            try:
                resultText = (next(res.results).text)
            except:
                resultText = "Unknown question."

            print("Response from WolframAlpha: ", resultText)

            hasher = hashlib.md5()
            hasher.update(str(resultText).encode('utf-8'))
            md5hash = hasher.digest()
            print("Computed Response MD5 Hash: ", md5hash)

            response = (resultText, md5hash)
            print("Response: ", response)

            pickledresponse = pickle.dumps(response)
            print("Pickled: ", pickledresponse)
            client.send(pickledresponse)

        client.close()

if __name__ == "__main__" : main()