# autozippy

## Description
AutoZippy is an easy to use automatic (non-interactive) archival software, designed to help you automate backups. Archive creation is configured with a simple and intuitive .YAML preset. 

For creating archives built-in library tarfile and 3rd-party library py7zr are used.

### Limitations
Currently AutoZippy supports only 7z and tar archives as 2 most popular formats. Tar archives currently do not support encryption due to a lack of non-interactive GnuPG assymetric encryption in python. However, nothing prevents you from encrypting a tar archive inside a 7z one.

## YAML Preset
YAML presets consist of archives and their settings. Every setting can be specified either on a file-wide level or overriden for specific archive with the notable exclusion of timestamps - they currently can only be specified on a preset-wide level. Aside from universal settings, like output directory, every format has its own specific settings, like algorithms, header encryption and compression level.

Archives and their settings are specified under `archives`. There they are listed by their filenames and each has to contain at least one file under its own `files` section. If you want to backup all files from directory but not subdirectories you can specify '*' as a filename.

### Usage Examples
> autozippy cloud.yaml photos.yaml example.yaml

As many configs as you want can be provided. `-v`/`--verbose` can be provided for debugging information and time per preset.

Example config is provided under filename example.yaml 

### Settings

* `mode` - **must be specified** - archive format, can be either `7z` or `tar`
* `outdir` - directory where archives are going to be saved. Default is working directory.
* `root` - directory from which to start path inside of an archive. For example, /etc/nginx/sites-available/yoursite with the root specified as /etc/nginx is going to be saved as sites-available/yoursite in the archive. Default is start of file paths you specify in config.
* `pass` - password

#### File-wide Settings
* `timestamp` - (true/false) whether to add timestamp to a filename of the archive. False by default.
* `custom_timestamp` - specify custom format for a timestamp. Default: %Y-%md-%d. See details [here](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)

#### 7z Specific Settings
* `algo` - compression algorithm. Can be either `lzma2`, `lzma`, `bzip2`, `ppmd`, `deflate` or `store` if no compression needed. LZMA2 by default.
* `lvl` - **supported only with LZMA2** - compression effort level
* `crypt_h` - **can only be used if pass is specified** - whether to encrypt file headers (names of files inside of the archive)
* `native` - whether to use 7z program installed on your computer instead of python library. **The only way to enable multi-threading**. Requires 7z in your PATH.

#### TAR Specific Settings
* `algo` - compression algorithm. Can be either `xz` (lzma), `gz` (gunzip) or `bz2` (bzip2). No compression by default.
* `lvl` - **supported only with LZMA** - compression effort level

## Contributing
Program is far from complete and all help is welcome. You may also report bugs or submit feature requests but I can't guarantee timely responses or fixes. 