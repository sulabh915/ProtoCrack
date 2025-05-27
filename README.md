
# 🛡️ ProtoCrack

ProtoCrack is a robust brute-force authentication toolkit that supports both SSH and FTP protocols. Designed for cybersecurity professionals and ethical hackers, it allows for high-speed, multi-threaded authentication testing using dictionaries or on-the-fly password generation.



## Features

✅ Protocol support: SSH and FTP

✅ Multi-threaded brute-force engine

✅ Support for both username and password lists

✅ Password generation with custom charset and length range

✅ Optional immediate exit on first successful login (--exit-on-success)

✅ Logging of successful credentials to disk

✅ Logging of all connection attempts for audit purposes

✅ Customizable target port support for each protocol





## 📁 Project Structure



```bash
ProtoCrack/
├── ssh_brute.py              # SSH brute-forcer script
├── ftp_cracker.py            # FTP brute-forcer script
├── README.md                 # This file
└── wordlists/                # Custom or downloaded password/user lists
```
    
## Installation

Python 3.6 or newer

```bash
git clone https://github.com/sulabh915/ProtoCrack.git
cd ProtoCrack
pip install -r requirements.txt
python3 ssh_brute.py
python3 ftp_cracker.py
```


## Usage/Examples

🚀 Usage Examples

🔐 SSH Brute-Force Example

```javascript
python3 ssh_brute.py 192.168.0.150 -u root -P /usr/share/wordlists/rockyou.txt --exit-on-success
```


🔐 FTP Brute-Force with Wordlist

```javascript
python3 ftp_cracker.py --host 127.0.0.1 -u admin -w /usr/share/wordlists/rockyou.txt --exit-on-success
```
🔐 FTP Brute-Force with Password Generation

```javascript
python3 ftp_cracker.py --host 127.0.0.1 -u admin -g --min_length 3 --max_length 4 --chars abc123
```


## Output

Found credentials are stored in ftp_credentials.txt and ssh_credentials.txt

Every login attempt for FTP is stored in ftp_attempts.log


##  Legal Disclaimer

This tool is intended for educational purposes and authorized penetration testing only.
Unauthorized use of this software against systems without explicit permission is illegal and unethical.Use responsibly and only in environments where you have permission to test.




## License

[MIT](https://choosealicense.com/licenses/mit/)

