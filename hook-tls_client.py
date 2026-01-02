# PyInstaller hook for tls_client
# Ensures the native DLLs are bundled in the correct location

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# Collect the dependencies folder with its DLLs/SOs
datas = collect_data_files('tls_client', subdir='dependencies')

# Also collect any dynamic libraries
binaries = collect_dynamic_libs('tls_client')
