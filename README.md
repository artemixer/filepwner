# filepwner
**filepwner** is an exploitation tool which automates testing file payloads on upload forms.


![filepwner_demo](https://github.com/artemixer/filepwner/assets/109953672/8c75a49f-0e55-483c-9a9a-4fc046c507d3)

## Installation
```
git clone https://github.com/artemixer/filepwner
cd filepwner
pip3 install -r requirements.txt
```
  
## Usage
```
python3 '/var/filepwner/filepwner.py' -r req.txt -t "File uploaded successfully" -d "/uploads/"
```
You need 3 things to get this tool running: a request file, a true/false condition regex and the upload directory

- filepwner works with HTTP request files, which can be obtained from other tools such as Burp Suite or ZAP. 
Once you have saved the request to a file, replace the file name with `*filename*` and the content with `*content*`
The final result should look something like this:

<img width="537" alt="Screenshot 2023-11-10 at 15 39 51" src="https://github.com/artemixer/filepwner/assets/109953672/f7f17891-0175-4f75-9e29-7420a7e12c3e">  
  
- The true/false regex can be obtained by manually making a request and seeing what kind of response the server gives.  
The entire response body will be scanned using the regex provided and if it matches, the upload will be counted as successful.  
  
- The upload directory has to be specified relative to the website root, so if the full file url would be `https://example.com/images/test.png`, the upload directory would be `-d "/images/"`

<details>
  <summary>Parameters</summary>

    -r REQUEST_FILE, --request-file REQUEST_FILE
                          Required - Read from a HTTP/S request file (replace the file content with the string *content* and filename extension with the string *filename*)
    -t TRUE_REGEX, --true-regex TRUE_REGEX
                          Required - Provide the success message when a file is uploaded
                          Usage: -s /--success 'File uploaded successfully.'
    -f FALSE_REGEX, --false-regex FALSE_REGEX
                          Required - Provide a failure message when a file is uploaded
                          Usage: -f /--failure 'File is not allowed!'
    -d UPLOAD_DIR, --upload-dir UPLOAD_DIR
                          Provide a remote path where the WebShell will be uploaded (won't work if the file will be uploaded with a UUID).
                          Usage: -l / --location /uploads/
    --rate-limit RATE_LIMIT
                          Set rate-limiting with seconds between each request.
                          Usage: --rate-limit 
    -v GLOBAL_VERBOSITY, --verbose GLOBAL_VERBOSITY
                          If set, details about the test will be printed on the screen
                          Usage: -v / --verbose
    --timeout             Number of seconds the request will wait before timing out (Default: 20)
                          Usage: -t / --timeout
    --print-response      If set, HTTP response will be printed on the screen
                          Usage: --print-response
</details>                  
  
## Customisation
When creating this tool I had customisations in mind, so I did my best to keep everything as cookie-cutter as possible. 
You are able to add your own modules/rules for running tests as well as adding new file extensions.

To add a module simply add a function with your desired functionality to `modules.py` then add the function by name into the list "active_modules" in `variations.py`

To add a new file extension add the sample.{ext} file to `assets/sample_files`, then add the extension and its mimetype/magic bytes to `variations.py`

## Test targets
For testing purposes I also included sample .php scripts (`/test_targets`) to emulate the behaviour of upload forms. If you wish to gain a better understanding of the soft or simply want to test if it works, feel free to run tests against them.  

<br/>
<br/>
<b>Feel free to open pull requests and issues, I will do my best to resolve or at least answer all of them</b>
