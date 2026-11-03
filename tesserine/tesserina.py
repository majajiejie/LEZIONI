#!/usr/bin/env python3
"""Legge e aggiorna i dati cifrati di una tesserina.

Uso:
  python3 tesserina.py leggi  FILE.html PIN            -> stampa i dati (JSON)
  python3 tesserina.py scrivi FILE.html PIN dati.json  -> salva i nuovi dati
"""
import base64, json, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 250000
BLOCCO = re.compile(r'/\*DATI-INIZIO\*/.*?/\*DATI-FINE\*/', re.S)


def _chiave(pin, sale):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=sale, iterations=ITER).derive(pin.encode())


def cifra(dati, pin):
    sale, iv = os.urandom(16), os.urandom(12)
    ct = AESGCM(_chiave(pin, sale)).encrypt(iv, json.dumps(dati, ensure_ascii=False).encode(), None)
    return ".".join(base64.b64encode(x).decode() for x in (sale, iv, ct))


def decifra(testo, pin):
    sale, iv, ct = (base64.b64decode(x) for x in testo.split("."))
    return json.loads(AESGCM(_chiave(pin, sale)).decrypt(iv, ct, None))


def blocco(testo_cifrato):
    return '/*DATI-INIZIO*/\nconst CIFRATO = "%s";\n/*DATI-FINE*/' % testo_cifrato


def leggi(file, pin):
    html = open(file, encoding="utf-8").read()
    m = re.search(r'const CIFRATO = "([^"]+)"', html)
    return decifra(m.group(1), pin)


def scrivi(file, pin, dati):
    html = open(file, encoding="utf-8").read()
    html = BLOCCO.sub(lambda _: blocco(cifra(dati, pin)), html, count=1)
    open(file, "w", encoding="utf-8").write(html)


if __name__ == "__main__":
    cmd, file, pin = sys.argv[1:4]
    if cmd == "leggi":
        print(json.dumps(leggi(file, pin), ensure_ascii=False, indent=1))
    elif cmd == "scrivi":
        scrivi(file, pin, json.load(open(sys.argv[4], encoding="utf-8")))
        print("ok")
