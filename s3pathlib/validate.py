# -*- coding: utf-8 -*-

import string

valid_bucket_charset: set = set(string.ascii_lowercase + string.digits + ".-")
letter_and_number: set = set(string.ascii_lowercase + string.digits)

safe_key_charset: set = set(string.ascii_letters + string.digits + "/!-_.*'()")
req_special_handling_key_charset: set = set("&$@=;:+ ,?")
to_avoid_key_charset: set = set("\\{}^&`[]\"<>#|~%")
valid_key_charset: set = set.union(safe_key_charset, req_special_handling_key_charset)

def validate_s3_bucket(bucket: str) -> None:
    """
    Raise exception if validation not passed.

    Ref:

    - `Bucket naming rules <https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html>`_
    """
    if not (3 <= len(bucket) <= 63):
        raise ValueError("Bucket names must be between 3 and 63 characters long.")

    invalid_chars = set(bucket).difference(valid_bucket_charset)
    if len(invalid_chars) != 0:
        raise ValueError((
            "Bucket names can consist only of lowercase letters, numbers, "
            "dots (.), and hyphens (-). invalid char found {}"
        ).format(invalid_chars))

    if (bucket[0] not in letter_and_number) or (bucket[-1] not in letter_and_number):
        raise ValueError("Bucket names must begin and end with a letter or number.")

    # raise ValueError("Bucket names must not be formatted as an IP address (for example, 192.168.5.4).")
    # raise ValueError("Bucket names must not start with the prefix xn--.")
    # raise ValueError("Bucket names must not end with the suffix -s3alias. This suffix is reserved for access point alias names.")
    # raise ValueError("Buckets used with Amazon S3 Transfer Acceleration can't have dots (.) in their names.")


def validate_s3_key(key: str) -> None:
    """
    Raise exception if validation not passed.

    Ref:

    - `Key naming rules <https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html#object-key-guidelines>`_
    """
    if len(key) > 1024:
        raise ValueError(
            "S3 key must be less that 1024 chars "
            "to construct the S3 console url!"
        )

    invalid_chars = set(key).difference(valid_key_charset)
    if len(invalid_chars) != 0:
        raise ValueError((
            "Invalid char found {}, "
            "read https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html#object-key-guidelines "
            "for more info"
        ).format(invalid_chars))


def validate_s3_uri(uri: str) -> None:
    if not uri.startswith("s3://"):
        raise ValueError("s3 uri must starts with 's3://'")

    if uri.count("/") < 3:
        raise ValueError(
            "s3 uri must have at least three '/', "
            "for example: s3://bucket/"
        )

    parts = uri.split("/", 3)
    bucket = parts[2]
    key = parts[3]
    validate_s3_bucket(bucket)
    validate_s3_key(key)

