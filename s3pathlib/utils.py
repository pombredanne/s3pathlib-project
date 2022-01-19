# -*- coding: utf-8 -*-

import hashlib
from typing import Tuple, List, Iterable, Optional
from pathlib_mate import Path

try:
    import botocore.exceptions
except ImportError:  # pragma: no cover
    pass
except:  # pragma: no cover
    raise


def split_s3_uri(
    s3_uri: str,
) -> Tuple[str, str]:
    """
    Split AWS S3 URI, returns bucket and key.

    :param s3_uri: example, ``"s3://my-bucket/my-folder/data.json"``
    """
    parts = s3_uri.split("/")
    bucket = parts[2]
    key = "/".join(parts[3:])
    return bucket, key


def join_s3_uri(
    bucket: str,
    key: str,
) -> str:
    """
    Join AWS S3 URI from bucket and key.

    :param bucket: example, ``"my-bucket"``
    :param key: example, ``"my-folder/data.json"`` or ``"my-folder/"``
    """
    return "s3://{}/{}".format(bucket, key)


def split_parts(key) -> List[str]:
    """
    Split s3 key parts using "/" delimiter.

    Example::

        >>> split_parts("a/b/c")
        ["a", "b", "c"]
        >>> split_parts("//a//b//c//")
        ["a", "b", "c"]
    """
    return [part for part in key.split("/") if part]


def smart_join_s3_key(
    parts: List[str],
    is_dir: bool,
) -> str:
    """
    Note, it assume that there's no such double slack in your path. It ensure
    that there's only one consecutive "/" in the s3 key.

    :param parts: list of s3 key path parts, could have "/"
    :param is_dir: if True, the s3 key ends with "/". otherwise enforce no
        tailing "/".

    Example::

        >>> smart_join_s3_key(parts=["/a/", "b/", "/c"], is_dir=True)
        a/b/c/
        >>> smart_join_s3_key(parts=["/a/", "b/", "/c"], is_dir=False)
        a/b/c
    """
    new_parts = list()
    for part in parts:
        new_parts.extend(split_parts(part))
    key = "/".join(new_parts)
    if is_dir:
        return key + "/"
    else:
        return key


def make_s3_console_url(
    bucket: str = None,
    prefix: str = None,
    s3_uri: str = None,
) -> str:
    """
    Return an AWS Console url that you can use to open it in your browser.

    :param bucket: example, ``"my-bucket"``
    :param prefix: example, ``"my-folder/"``
    :param s3_uri: example, ``"s3://my-bucket/my-folder/data.json"``

    Example::

        >>> make_s3_console_url(s3_uri="s3://my-bucket/my-folder/data.json")
        https://s3.console.aws.amazon.com/s3/object/my-bucket?prefix=my-folder/data.json
    """
    if s3_uri is None:
        if not ((bucket is not None) and (prefix is not None)):
            raise ValueError
    else:
        if not ((bucket is None) and (prefix is None)):
            raise ValueError
        bucket, prefix = split_s3_uri(s3_uri)

    if len(prefix) == 0:
        return "https://s3.console.aws.amazon.com/s3/buckets/{}?tab=objects".format(
            bucket,
        )
    elif prefix.endswith("/"):
        s3_type = "buckets"
    else:
        s3_type = "object"
    return "https://s3.console.aws.amazon.com/s3/{s3_type}/{bucket}?prefix={prefix}".format(
        s3_type=s3_type,
        bucket=bucket,
        prefix=prefix
    )


def ensure_s3_object(
    s3_key_or_uri: str,
) -> None:
    """
    Raise exception if the string is not in valid format for a AWS S3 object
    """
    if s3_key_or_uri.endswith("/"):
        raise ValueError("'{}' doesn't represent s3 object!".format(s3_key_or_uri))


def ensure_s3_dir(
    s3_key_or_uri: str
) -> None:
    """
    Raise exception if the string is not in valid format for a AWS S3 directory
    """
    if not s3_key_or_uri.endswith("/"):
        raise ValueError("'{}' doesn't represent s3 dir!".format(s3_key_or_uri))


def validate_s3_bucket(bucket):
    """
    Ref:
    https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
    """
    pass


def validate_s3_key(key):
    """
    Ref:
    https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html#object-key-guidelines
    """
    pass


MAGNITUDE_OF_DATA = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]


def repr_data_size(
    size_in_bytes: int,
    precision: int = 2,
) -> str:  # pragma: no cover
    """
    Return human readable string represent of a file size. Doesn't support
    size greater than 1EB.

    For example:

    - 100 bytes => 100 B
    - 100,000 bytes => 97.66 KB
    - 100,000,000 bytes => 95.37 MB
    - 100,000,000,000 bytes => 93.13 GB
    - 100,000,000,000,000 bytes => 90.95 TB
    - 100,000,000,000,000,000 bytes => 88.82 PB
    ...

    Magnitude of data::

        1000         kB    kilobyte
        1000 ** 2    MB    megabyte
        1000 ** 3    GB    gigabyte
        1000 ** 4    TB    terabyte
        1000 ** 5    PB    petabyte
        1000 ** 6    EB    exabyte
        1000 ** 7    ZB    zettabyte
        1000 ** 8    YB    yottabyte
    """
    if size_in_bytes < 1024:
        return "%s B" % size_in_bytes

    index = 0
    while 1:
        index += 1
        size_in_bytes, mod = divmod(size_in_bytes, 1024)
        if size_in_bytes < 1024:
            break
    template = "{0:.%sf} {1}" % precision
    s = template.format(size_in_bytes + mod / 1024.0, MAGNITUDE_OF_DATA[index])
    return s


def hash_binary(
    b: bytes,
    hash_meth: callable,
) -> str:  # pragma: no cover
    """
    Get the hash of a binary object.

    :param b: binary object
    :param hash_meth: callable hash method, example: hashlib.md5

    :return: hash value in hex digits.
    """
    m = hash_meth()
    m.update(b)
    return m.hexdigest()


def md5_binary(
    b: bytes,
) -> str:  # pragma: no cover
    """
    Get the md5 hash of a binary object.

    :param b: binary object

    :return: hash value in hex digits.
    """
    return hash_binary(b, hashlib.md5)


def sha256_binary(
    b: bytes,
) -> str:  # pragma: no cover
    """
    Get the md5 hash of a binary object.

    :param b: binary object

    :return: hash value in hex digits.
    """
    return hash_binary(b, hashlib.sha256)


DEFAULT_CHUNK_SIZE = 1 << 6


def hash_file(
    abspath: str,
    hash_meth: callable,
    nbytes: int = 0,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> str:  # pragma: no cover
    """
    Get the hash of a file on local drive.

    :param abspath: absolute path of the file
    :param hash_meth: callable hash method, example: hashlib.md5
    :param nbytes: only hash first nbytes of the file
    :param chunk_size: internal option, stream chunk_size of the data for hash
        each time, avoid high memory usage.

    :return: hash value in hex digits.
    """
    if nbytes < 0:
        raise ValueError("nbytes cannot smaller than 0")
    if chunk_size < 1:
        raise ValueError("nbytes cannot smaller than 1")
    if (nbytes > 0) and (nbytes < chunk_size):
        chunk_size = nbytes

    m = hash_meth()
    with open(abspath, "rb") as f:
        if nbytes:  # use first n bytes
            have_reads = 0
            while True:
                have_reads += chunk_size
                if have_reads > nbytes:
                    n = nbytes - (have_reads - chunk_size)
                    if n:
                        data = f.read(n)
                        m.update(data)
                    break
                else:
                    data = f.read(chunk_size)
                    m.update(data)
        else:  # use entire content
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                m.update(data)

    return m.hexdigest()


# --------------------------------------------------------------------------
#                      boto3 s3 client enhancement
# --------------------------------------------------------------------------
def grouper_list(
    l: Iterable,
    n: int,
) -> Iterable[list]:  # pragma: no cover
    """
    Evenly divide list into fixed-length piece, no filled value if chunk
    size smaller than fixed-length.

    Example::

        >>> list(grouper_list(range(10), n=3)
        [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

    :param l: an iterable object
    :param n: number of item per list
    """
    chunk = list()
    counter = 0
    for item in l:
        counter += 1
        chunk.append(item)
        if counter == n:
            yield chunk
            chunk = list()
            counter = 0
    if len(chunk) > 0:
        yield chunk


def collect_not_null_kwargs(**kwargs) -> dict:
    """
    Collect not null key value pair from keyword arguments.
    """
    return {
        k: v
        for k, v in kwargs.items()
        if v is not None
    }


def exists(
    s3_client,
    bucket: str,
    key: str,
) -> bool:
    """
    Check if an s3 object exists or not.

    :param s3_client: ``boto3.session.Session().client("s3")`` object
    :param bucket: s3 bucket name
    :param key: s3 key. if it ends with ``"/"``, it always returns False.
        because directory is logic concept in S3 and never exists.
    """
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except botocore.exceptions.ClientError as e:
        if "Not Found" in str(e):
            return False
        else:  # pragma: no cover
            raise e
    except:  # pragma: no cover
        raise


def raise_file_exists_error(s3_uri: str) -> None:
    """
    A helper function that raise FileExistsError when try writing to an existing
    S3 object, but ``overwrite = False``.
    """
    s3_console_url = make_s3_console_url(s3_uri=s3_uri)
    msg = (
        "cannot write to {}, s3 object ALREADY EXISTS! "
        "open console for more details {}."
    ).format(s3_uri, s3_console_url)
    raise FileExistsError(msg)


def upload_dir(
    s3_client,
    bucket: str,
    prefix: str,
    local_dir: str,
    pattern: str = "**/*",
    overwrite: bool = False,
) -> int:
    """
    Recursively upload a local directory and files in its sub directory.

    :param s3_client: ``boto3.session.Session().client("s3")`` object
    :param bucket: s3 bucket name
    :param prefix: the s3 prefix (logic directory) you want to upload to
    :param local_dir: absolute path of the directory sitting on the local
        file system you want to upload
    :param pattern: linux styled glob pattern match syntax
    :param overwrite: if False, non of the file will be upload / overwritten
        if any of target s3 location already taken.

    :return: number of files uploaded

    Ref:

    - pattern: https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob
    """
    if prefix.endswith("/"):
        prefix = prefix[:-1]

    p_local_dir = Path(local_dir)

    if p_local_dir.is_file():  # pragma: no cover
        raise TypeError

    if p_local_dir.exists() is False:  # pragma: no cover
        raise FileNotFoundError

    if len(prefix):
        final_prefix = f"{prefix}/"
    else:
        final_prefix = ""

    # list of (local file path, target s3 key)
    todo: List[Tuple[str, str]] = list()
    for p in p_local_dir.glob(pattern):
        if p.is_file():
            relative_path = p.relative_to(p_local_dir)
            key = "{}{}".format(final_prefix, "/".join(relative_path.parts))
            todo.append((p.abspath, key))

    # make sure all target s3 location not exists
    if overwrite is False:
        for abspath, key in todo:
            if exists(s3_client, bucket, key) is True:
                s3_uri = join_s3_uri(bucket, key)
                raise_file_exists_error(s3_uri)

    # execute upload
    for abspath, key in todo:
        s3_client.upload_file(abspath, bucket, key)

    return len(todo)


def iter_objects(
    s3_client,
    bucket: str,
    prefix: str,
    batch_size: int = 1000,
    limit: int = None,
) -> Iterable[dict]:
    """
    Recursively iterate objects, yield python dict object described in ``response["Contents"]``
    ``s3_client.list_objects_v2``
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_objects_v2

    Example::

        >>> for dct in iter_objects(
        ...     s3_client=s3_client,
        ...     bucket="my-bucket",
        ...     prefix="my-folder",
        ... ):
        ...     print(dct)
        {"Key": "1.json", "ETag": "...", "Size": 123, "LastModified": datetime(2015, 1, 1), "StorageClass": "...", "Owner", {...}}
        {"Key": "2.json", "ETag": "...", "Size": 123, "LastModified": datetime(2015, 1, 1), "StorageClass": "...", "Owner", {...}}
        {"Key": "3.json", "ETag": "...", "Size": 123, "LastModified": datetime(2015, 1, 1), "StorageClass": "...", "Owner", {...}}
        ...

    :param s3_client: ``boto3.session.Session().client("s3")`` object
    :param bucket: s3 bucket name
    :param prefix: the s3 prefix (logic directory) you want to upload to
    :param batch_size: number of s3 object returned per paginator, valid value
        is from 1 ~ 1000. large number can reduce IO.
    :param limit: number of s3 object to return

    :return: a generator object that yield python dict

    TODO: add unix glob liked syntax for pattern matching, reference:

    - https://github.com/jazzband/pathlib2/blob/01eb405343b9ee1805d1dc6f96bc28482d29e08b/pathlib2/__init__.py#L731
    - https://github.com/jazzband/pathlib2/blob/01eb405343b9ee1805d1dc6f96bc28482d29e08b/pathlib2/__init__.py#L742
    """
    # validate arguments
    if batch_size < 1 or batch_size > 1000:
        raise ValueError("``batch_size`` has to be 1 ~ 1000.")
    if limit is None:  # set to max int if limit is not given
        limit = (1 << 31) - 1
    if batch_size > limit:
        batch_size = limit
    next_token: Optional[str] = None
    count: int = 0
    while 1:
        kwargs = dict(
            Bucket=bucket,
            Prefix=prefix,
            MaxKeys=batch_size,
        )
        if next_token is not None:
            kwargs["ContinuationToken"] = next_token
        res = s3_client.list_objects_v2(**kwargs)
        contents = res.get("Contents", [])
        n_objects = len(contents)
        count += n_objects
        if count <= limit:  # if not reach the limit
            for dct in contents:
                yield dct
            if count == limit:
                return
        else:  # if reach the limit
            first_n_only = batch_size - (count - limit)
            for dct in contents[:first_n_only]:
                yield dct
            count = limit  # set count = limit
            break
        next_token = res.get("NextContinuationToken")
        if next_token is None:  # break if not more paginator
            break


def calculate_total_size(
    s3_client,
    bucket: str,
    prefix: str,
) -> Tuple[int, int]:
    """
    Perform the "Calculate Total Size" action in AWS S3 console

    :param s3_client: ``boto3.session.Session().client("s3")`` object
    :param bucket: s3 bucket name
    :param prefix: the s3 prefix (logic directory) you want to calculate

    :return: first value is number of objects, second value is total size
        in bytes
    """
    count = 0
    total_size = 0
    for dct in iter_objects(s3_client=s3_client, bucket=bucket, prefix=prefix):
        count += 1
        total_size += dct["Size"]
    return count, total_size


def count_objects(
    s3_client,
    bucket: str,
    prefix: str,
) -> int:
    """
    Count number of objects under prefix

    :param s3_client: ``boto3.session.Session().client("s3")`` object
    :param bucket: s3 bucket name
    :param prefix: the s3 prefix (logic directory) you want to count

    :return: number of objects under prefix
    """
    i = 0
    for i, dct in enumerate(
        iter_objects(s3_client=s3_client, bucket=bucket, prefix=prefix)
    ):
        pass
    if i == 0:  # pragma: no cover
        return 0
    else:
        return i + 1


def delete_dir(
    s3_client,
    bucket: str,
    prefix: str,
    batch_size: int = 1000,
    limit: int = None,
    mfa: str = None,
    request_payer: str = None,
    bypass_governance_retention: bool = None,
    expected_bucket_owner: str = None,
) -> int:
    """
    :param s3_client: ``boto3.session.Session().client("s3")`` object
    :param bucket: s3 bucket name
    :param prefix: the s3 prefix (logic directory) you want to calculate
    :param batch_size: number of s3 object to delete per paginator, valid value
        is from 1 ~ 1000. large number can reduce IO.
    :param limit: number of s3 object to delete

    :return: number of deleted items
    """
    to_delete_keys = list()
    for dct in iter_objects(
        s3_client=s3_client,
        bucket=bucket,
        prefix=prefix,
        batch_size=batch_size,
        limit=limit,
    ):
        to_delete_keys.append(dct["Key"])

    for keys in grouper_list(to_delete_keys, 1000):
        kwargs = dict(
            Bucket=bucket,
            Delete={
                "Objects": [
                    {
                        "Key": key
                    }
                    for key in keys
                ]
            },
        )
        addtional_kwargs = collect_not_null_kwargs(
            MFA=mfa,
            RequestPayer=request_payer,
            BypassGovernanceRetention=bypass_governance_retention,
            ExpectedBucketOwner=expected_bucket_owner,
        )
        kwargs.update(addtional_kwargs)
        s3_client.delete_objects(**kwargs)

    return len(to_delete_keys)
