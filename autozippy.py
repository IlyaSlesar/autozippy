import argparse
import subprocess
from pathlib import Path
import tarfile
import datetime
import os
import time
import yaml
import py7zr

algos_7z = {
    'lzma2:': py7zr.FILTER_LZMA2,
    'lzma': py7zr.FILTER_LZMA,
    'bzip2': py7zr.FILTER_BZIP2,
    'ppmd': py7zr.FILTER_PPMD,
    'deflate': py7zr.FILTER_DEFLATE,
    'copy': py7zr.FILTER_COPY
}

verbose = False

def encrypt_7z(archive_name, files, password = None, sp_args = None):
    filters = list()
    if verbose:
        print('Encrypt 7z', archive_name, list(files), password, sp_args)
    if sp_args and 'algo' in sp_args:
        filters.append({'id': algos_7z[sp_args['algo']]})
    else:
        filters.append({'id': py7zr.FILTER_LZMA2})
    if sp_args and 'lvl' in sp_args:
        filters[-1]['preset'] = sp_args['lvl']
    
    if sp_args and 'native' in sp_args:
        args = ['7z', 'a']
        if password:
            args.append('-p' + password)
        if 'crypt_h' in sp_args:
            args.append('-mhe=on')
        if 'lvl' in sp_args:
            args.append('-mx=' + str(sp_args['lvl']))
        args.extend([archive_name] + files)
        if verbose:
            print('7Z Args:', args)
            subprocess.run(args)
        else:
            subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        with py7zr.SevenZipFile(archive_name, 'w', password=str(password), filters=filters) as arch:
            if sp_args and 'crypt_h' in sp_args:
                arch.set_encrypted_header(True)
            for file in files:
                if Path(file).name == '*':
                    for sub_file in Path(file).parent.iterdir():
                        if sub_file.is_file():
                            arch.write(sub_file)
                elif Path(file).is_dir():
                    arch.writeall(file)
                elif Path(file).exists():
                    arch.write(file)
                else:
                    raise RuntimeError(f'File {file} does not exist')


def encrypt_tar(archive_name, files, password = None, sp_args = None):
    if verbose:
        print('Encrypt TAR', archive_name, list(files), password, sp_args)
    if 'algo' in sp_args:
        if sp_args['algo'] == 'lzma':
            sp_args['algo'] = 'xz'
        mode = 'w:' + sp_args['algo']
        archive_name = archive_name.with_suffix('.tar.' + sp_args['algo'])
    else:
        mode = 'w'
    
    arch = tarfile.open(archive_name, mode=mode, preset=sp_args['lvl'] if 'lvl' in sp_args 
                                                        and sp_args['algo'] == 'xz' else None)
    for file in files:
        if Path(file).name == '*':
            for sub_file in Path(file).parent.iterdir():
                if sub_file.is_file():
                    arch.add(sub_file)
        elif Path(file).exists():
            arch.add(file)
        else:
            raise RuntimeError(f'File {file} does not exist')
    arch.close()


def process_preset(preset):
    for archive_name in preset['archives'].keys():
        archive = preset['archives'][archive_name]
        archive_path = Path(archive_name)

        if 'mode' in archive:
            mode = archive['mode']
        elif 'mode' in preset:
            mode = preset['mode']
        else:
            raise RuntimeError('Archival mode not specified')

        if 'pass' in archive:
            password = archive['pass']
        elif 'pass' in preset:
            password = preset['pass']
        else:
            password = None

        if 'outdir' in archive:
            archive_path = Path(Path(archive['outdir']).resolve(), archive_path)
        elif 'outdir' in preset:
            archive_path = Path(Path(preset['outdir']).resolve(), archive_path)

        if 'root' in archive:
            t_dir = os.getcwd()
            os.chdir(archive['root'])
            archive['files'] = list(map(lambda path: Path(Path.resolve(Path(path).parent).relative_to(os.getcwd()), Path(path).name), archive['files']))
        elif 'root' in preset:
            t_dir = os.getcwd()
            os.chdir(preset['root'])
            archive['files'] = list(map(lambda path: Path(Path.resolve(Path(path).parent).relative_to(os.getcwd()), Path(path).name), archive['files']))

        if 'timestamp' in preset:
            if 'custom_timestamp' in preset and preset['custom_timestamp']:
                archive_path = archive_path.with_name({archive_path.name} + ' ' +
                                                      {datetime.datetime.now().strftime(preset['custom_timestamp'])})
            else:
                archive_path = archive_path.with_name(archive_path.name + ' ' +
                                                      datetime.datetime.now().strftime('%Y-%m-%d'))

        if mode == '7z':
            encrypt_7z(archive_path.with_suffix('.7z'), archive['files'],
                       password=password, sp_args=archive['7z'] if '7z' in archive
                                                  else preset['7z'] if '7z' in preset
                                                  else None)
        elif mode == 'tar':
            encrypt_tar(archive_path.with_suffix('.tar'), archive['files'],
                       password=password, sp_args=archive['tar'] if 'tar' in archive
                                                  else preset['tar'] if 'tar' in preset
                                                  else None)
        else:
            raise RuntimeError('Unknown mode in config')
        
        if 't_dir' in locals():
            os.chdir(t_dir)
            del t_dir


def main():
    parser = argparse.ArgumentParser(description='Create archives as described in YAML preset')
    parser.add_argument('preset', nargs='+')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    global verbose
    verbose = args.verbose
    
        
    for preset in args.preset:
        if verbose:
            tic = time.perf_counter()
        with open(preset, 'r') as f:
            process_preset(yaml.safe_load(f))
        if verbose:
            print(time.perf_counter() - tic)
    
    

main()
