#! /usr/bin/python3
import sys, socket, pickle, hashlib
from cryptography.fernet import Fernet
import wolframalpha
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
# Pin red
GPIO.setup(4, GPIO.OUT)
# Pin green
GPIO.setup(17, GPIO.OUT)
# Pin blue
GPIO.setup(27, GPIO.OUT)

def main():

    host = ''
    port = 5000
    size = 1024
    backlog = 1
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(backlog)
    server_address = socket.gethostbyname(socket.gethostname())
    print("Server IP Address: ", server_address)
    print("Server Port: ", port)
    wclient = wolframalpha.Client('V76GGA-6VAXGW25UP')

    while 1:
        print("Waiting for client to connect.")
        # turn led red
        time.sleep(2)
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(17, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)

        client, address = s.accept()
        print("Client Connected: ", address)
        print("\nWaiting for client to send payload")
        data = client.recv(size)
        print("Received payload from client.")
        time.sleep(2)
        # turn led yellow
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(17, GPIO.HIGH)
        GPIO.output(27, GPIO.LOW)
        if data:
            # Load the data into a tuple
            questionpayload = pickle.loads(data)
            print("Question Payload: ", questionpayload)

            if len(questionpayload) != 4:
                print('Error: Invalid payload packet detected.')
                client.end(b'Error: Invalid payload packet detected.')
                client.close()
                continue

            # Compute the MD5 Hash
            computedchecksum = checksum(questionpayload[1])
            print("Computed question checksum: ", computedchecksum)

            # Compare computed MD5 Hash with received hash
            if computedchecksum != questionpayload[2]:
                # If we compute a different MD5 Hash then we send an error message back
                # to the client and close the client connection
                print('Error: Computed question checksum does not match with passed checksum!')
                client.send(b'Error: Computed question checksum does not match with passed checksum!')
                client.close()
                continue
            print("Question payload checksum OK.")
            # Otherwise send the question to wolfram alpha

            encrypted_question = questionpayload[1]
            print("Encrypted question: ", encrypted_question)

            # Decrypt question here
            print("Decrypting Question")
            fernet_key = questionpayload[0]
            f = Fernet(fernet_key)
            question = f.decrypt(encrypted_question)
            print("Question Asked: ", question)
            time.sleep(2)
            # turn led cyan
            GPIO.output(4, GPIO.LOW)
            GPIO.output(17, GPIO.HIGH)
            GPIO.output(27, GPIO.HIGH)
            print("Sending question to wolframalpha")
            res = wclient.query(question)
            resultText = ""
            time.sleep(2)
            # turn led magenta
            GPIO.output(4, GPIO.HIGH)
            GPIO.output(17, GPIO.LOW)
            GPIO.output(27, GPIO.HIGH)
            print("Received result from wolframalpha")
            try:
                resultText = (next(res.results).text)
            except:
                resultText = "Unknown question."

            print("Response from WolframAlpha: ", resultText)

            # Encrypt response here
            print("Encrypting Response")
            encrypted_response = f.encrypt(resultText.encode('utf-8'))

            result_m5hash = checksum(encrypted_response)
            print("Computed response checksum: ", result_m5hash)

            response = (encrypted_response, result_m5hash)
            print("Encrypted response: ", encrypted_response)

            pickledresponse = pickle.dumps(response)
            print("Pickled: ", pickledresponse)
            print("Sending response to client.")
            time.sleep(2)
            # turn led white
            GPIO.output(4, GPIO.HIGH)
            GPIO.output(17, GPIO.HIGH)
            GPIO.output(27, GPIO.HIGH)
            client.send(pickledresponse)
            print("Response sent to client")
        client.close()


def checksum(val):
    hasher = hashlib.md5()
    hasher.update(str(val).encode('utf-8'))
    return hasher.hexdigest()

if __name__ == "__main__" : main()
