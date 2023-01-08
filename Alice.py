#client: Alice
#!/usr/bin/python3
import random
import subprocess
import re
import socket ,os , sys


#create socket ad get port number and server adress
server_adress = socket.gethostbyname('localhost')
port_number = 8790
ma_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connction
try:
    ma_socket.connect((server_adress, port_number))
except Exception as e :
   print("Erreur de connexion",e.args)
   sys.exit(1)

def GeneratePrimeNumber():
    random.seed()
    commande = "openssl prime"
    n_0 = random.choice('1379')
    n_i = [random.choice('0123456789') for i in range (0 , 11)]
    n_max = random.choice('123456789')
    Liste = list(n_max)
    Liste.extend(n_i)
    Liste.append(n_0)
    q = int(''.join(Liste))
    while True:
        n_a = random.choice('0123456789')
        n_b = random.choice('1379')
        n_i.append(n_a)
        n_i.append(n_b)
        p = int(''.join(n_i))
        r = subprocess.run("{} {}".format(commande, p), shell=True, stdout=subprocess.PIPE)
        resultat_openssl = r.stdout
        v = re.compile(r'is prime')
        p_resultats = v.search(str(resultat_openssl))
        n_i.pop()
        n_i.pop()
        if p_resultats != None:
            break
    pfinal = p  
    return(pfinal)


def lpowmod(x, y, n):
    """puissance modulaire: (x**y)%n avec x, y et n entiers"""
    result = 1
    while y>0:
        if y&1>0:
            result = (result*x)%n
        y >>= 1
        x = (x*x)%n
    return result

def egcd(a, b):
    x,y, u,v = 0,1, 1,0
    while a != 0:
        q, r = b//a, b%a
        m, n = x-u*q, y-v*q
        b,a, x,y, u,v = a,r, u,v, m,n
    gcd = b
    return gcd, x, y



def modinv(a, m):
    gcd, x, y = egcd(a, m)
    if gcd != 1:
        return None
    return x % m


e = 65537
P = GeneratePrimeNumber()
Q = GeneratePrimeNumber()
Phi_N = (int(P)-1) * (int(Q)-1)
N_alice = int(P)*int(Q)
d_alice = modinv(e,Phi_N)


#server=bob
N_bob = int(ma_socket.recv(1024))
while 1:
    message = input("message?")
    if message:
            re_separateur = re.compile(r"['']+")
            liste = re_separateur.split(str(message))
            liste_en_hex = [bytes(u,'utf8').hex() for u in liste]
            conv_to_int =[int(x,16) for x in liste_en_hex] 
            message_chiffré_par_mot = [str(lpowmod(x,e,N_bob)) for x in conv_to_int]
            message_chiffré = ''.join(message_chiffré_par_mot) 
            message_chiffré_envoyé = message_chiffré + ' ' + str(N_alice)
            print("Voilà le message chiffré envoyé:",message_chiffré_envoyé)
            ma_socket.sendall(bytes(message_chiffré_envoyé, 'utf8'))
            if message == "fin":
                break  # Sort de la boucle si le message est "fin"
    # Ajout de la condition pour terminer la boucle lorsque aucun message n'est envoyé
    if not message:
        break

while 1:
    message_chiffré_reçu = ma_socket.recv(1024)
    if message_chiffré_reçu:
        re_separateur = re.compile(r"['']+")
        print("message chiffré reçu: ",message_chiffré_reçu)
        message_chiffré_reçu_en_utf8 =message_chiffré_reçu.decode('utf8') 
        liste= re_separateur.split(str(message_chiffré_reçu_en_utf8))
        message_chiffré_reçu_en_int = [int(x) for x in liste]
        message_déchiffré_en_int = [lpowmod(x,d_alice,N_alice) for x in message_chiffré_reçu_en_int]
        message_déchiffré_hex = [ hex(x) for x in message_déchiffré_en_int]
        message_déchiffré_en_bytes = [bytes.fromhex(x[2:])for x in message_déchiffré_hex ]
        message_déchiffré_utf8 = [x.decode('utf8') for x in message_déchiffré_en_bytes]
        message_déchiffré = ''.join(message_déchiffré_utf8)
        print("Voilà le message reçu déchiffré :",message_déchiffré)
        if not message_chiffré_reçu:
            break  # Sort de la boucle si aucun message n'est reçu

        
ma_socket.close()
	

