# Memloader

Memloader is an IDA plugin with two file loaders. Both bring a file into the IDA database without writing that file to disk.

- **Memloader ZIP** opens a ZIP archive, lets you pick one member, decrypts it when needed, and hands the bytes to IDA's regular file format loaders.
- **Memloader URL** downloads a file from a URL and loads the bytes the same way.

Only the IDA database is written. The sample stays inside the archive or on the remote server, which keeps it away from antivirus software that scans files on disk. When no IDA loader recognizes the bytes, Memloader maps them as raw x86 shellcode at address 0.

The loaders are a Python port of the C++ Memloader plugin by [Kasif Dekel](https://twitter.com/kasifdekel) at SentinelLabs.

## Installation

```
hcli plugin install memloader
```

IDA 9.2 or later is required. The plugin uses only the Python standard library.


## Loading a file in IDA

Open a ZIP file as you would open any other file. The loader list shows "Memloader ZIP" next to IDA's built-in archive loader. Choose it, pick the member when the archive holds more than one file, and enter the password when the member is encrypted. The default password is `infected`. The database takes the member's name. For example, `sample.zip` with the member `sample.exe` produces `sample.exe.i64` next to the archive.

To load from a URL, open any file, choose "Memloader URL" in the loader list, and enter the URL. The file you opened is ignored. The database is named after the SHA-256 of the downloaded bytes.

When IDA does not recognize the extracted file, Memloader asks whether to load it as shellcode, and whether it is 32-bit or 64-bit.

A ZIP member that is itself an archive is rejected. Nested archives are not supported.

## Headless use

Both loaders work with `idat` and idalib. Select the loader with `-T` and pass options with `-Omemloader:`. Options are `key=value` pairs separated by `;`.

```
idat -A -T"Memloader ZIP" -Omemloader:member=payload.exe;password=s3cret sample.zip
idat -A -T"Memloader URL" -Omemloader:url=https://example.com/sample.bin placeholder.bin
idat -A -T"Memloader ZIP" -Omemloader:bitness=64 shellcode.zip
```

| Option     | Meaning                                                   | Default    |
|------------|-----------------------------------------------------------|------------|
| `member`   | Name or path of the ZIP member to load                    | first file |
| `password` | Password for encrypted members                            | `infected` |
| `url`      | URL to download (URL loader only)                         | none       |
| `bitness`  | `32` or `64`, used when the bytes are loaded as shellcode | `32`       |

Without `-T`, IDA's own archive loader takes ZIP files in batch mode. Without a `url` option, the URL loader does not offer itself in batch mode, so plain files load as usual.

## How IDA finds the loaders

IDA only looks for loaders in its `loaders/` directories. At startup the plugin creates two symbolic links, `memloader_zip_loader.py` and `memloader_url_loader.py`, in the `loaders/` folder of your IDA user directory. They point at the loader entry files in the plugin directory. Each link names the plugin it belongs to, so you can always see where a loader comes from. When the plugin is upgraded or moved, the links are retargeted at the next start.

On Windows, symbolic links need Developer Mode or an elevated IDA. Without either, the plugin creates hard links instead. These work the same way but do not show the plugin path.

After you uninstall the plugin, the links stay behind. IDA ignores a dangling symbolic link. On Windows, a hard link keeps the small entry file, which then does nothing except print a message that names the file to delete. Both can be removed from the `loaders/` folder by hand.

## Development

```
uv run --group dev pytest tests -v
uvx --with ida-hcli hcli plugin install -e .
```

`tests/data/pma-lab01-01.zip` holds the Lab 01-01 executable and DLL from Practical Malware Analysis, encrypted with the password `infected`. It serves as a realistic sample for the loader tests and for trying the plugin by hand. The pure Python tests run anywhere. The idalib tests run when an IDA installation is available through `IDADIR` or `~/.idapro/ida-config.json`, and are skipped otherwise. The behavior is specified in `docs/plans/spec.md` and the implementation is described in `docs/plans/design.md`.
