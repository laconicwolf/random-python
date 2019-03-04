import subprocess
import xml.etree.ElementTree as etree
import zipfile
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

def send_mail(send_from, send_to, subject, message, files=[],
              username='', password='', server="localhost", port=587, 
              use_tls=True):
    """Compose and send email with provided info and attachments.

    Args:
        send_from (str): from name
        send_to (str): to name
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
        server (str): mail server host name
        port (int): port number
        username (str): server auth username
        password (str): server auth password
        use_tls (bool): use TLS mode
    
    https://stackoverflow.com/questions/3362600/how-to-send-email-attachments
    """
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="{}"'.format(os.path.basename(path)))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    if use_tls:
        smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()

def run_discovery_scan() -> None:
    """Runs an Nmap discovery scan and saves
    the output to a file.
    """
    subprocess.run(["nmap", "-sn", "192.168.1.0/24", "-oX", "scan.xml"])

def run_full_scan(addresses: list) -> None:
    """Runs an Nmap scan of specified hosts.
    nmap -iL <addresses> -oA rogues
    """
    temp_filename = 'temp_addrs'
    with open(temp_filename, 'w') as fh:
        for addr in addresses:
            fh.write(addr + '\n')
    subprocess.run(["nmap", '-' '-iL', temp_filename, "-oA", "rogues"])
    os.remove(temp_filename)

def parse_up_hosts(xml_scan_file_name: str) -> list:
    """Parses an Nmap XML file and returns a list of 
    'Up' hosts.
    """
    try:
        tree = etree.parse(xml_scan_file_name)
    except Exception as error:
        print("[-] A an error occurred. The XML may not be well formed. "
              "Please review the error and try again: {}".format(error))
        exit()
    root = tree.getroot()

    up_hosts = []
    hosts = root.findall('host')
    for host in hosts:

        # Ignore hosts that are not 'up'
        if not host.find('status').attrib.get('state') == 'up':
            continue
        
        # Get IP address
        ip_address = host.find('address').attrib.get('addr')
        up_hosts.append(ip_address)
    
    return up_hosts

def zip_nmap_files(filenames: list) -> None:
    """Zips the nmap output files.
    """
    with zipfile.ZipFile('rogue_devices.zip', 'w') as zf:
        for f in filenames:   
            zf.write(f)

def main():
    """Compates an existing baseline scan file (baseline.xml)
    with a new scan. Sends an email if any hosts are found in
    the new scan that were not a part of the baseline.
    """
    run_discovery_scan()

    # Get lists of up hosts
    baseline_up_hosts = parse_up_hosts('baseline.xml')
    current_up_hosts = parse_up_hosts('scan.xml')

    # Compare the list of hosts from the scans
    unknown_hosts = [host for host in current_up_hosts if host not in baseline_up_hosts]
    
    # If the no unknown hosts are found, exit the program
    if not unknown_hosts:
        exit()
    run_full_scan(unknown_hosts)

    # Gather and sort the Nmap files
    nmap_files = [file for file in os.listdir() if file.startswith('rogues')]
    zip_nmap_files(nmap_files)

    # Populate the required variables and send the email
    username = ''
    password = ''
    from_address = 'Scanner'
    to_address = ''
    subject = 'Rogue Devices Discovered'
    rogues = '\n'.join(unknown_hosts)
    body = 'The following devices were discovered:\n{}\nSee attached scan report.\n\n-Scanner'.format(rogues)
    send_mail(from_address, to_address, subject, body, files=['rogue_devices.zip'],
              username=username, password=password, server="smtp.gmail.com")

if __name__ == '__main__':
    main()
