"""Pass media workers only environment settings relevant to local processing."""
import os

_ALLOWED = {
    'PATH', 'HOME', 'USERPROFILE', 'SYSTEMROOT', 'SYSTEMDRIVE', 'WINDIR', 'COMSPEC',
    'PATHEXT', 'TEMP', 'TMP', 'TMPDIR', 'HOMEDRIVE', 'HOMEPATH', 'APPDATA', 'LOCALAPPDATA',
    'PROGRAMDATA', 'PROGRAMFILES', 'PROGRAMFILES(X86)', 'NUMBER_OF_PROCESSORS',
    'PROCESSOR_ARCHITECTURE', 'LANG', 'LC_ALL', 'DISPLAY', 'XAUTHORITY',
    'TORCH_HOME', 'HF_HOME', 'HUGGINGFACE_HUB_CACHE', 'XDG_CACHE_HOME',
    'NUMBA_CACHE_DIR', 'MPLCONFIGDIR', 'PTK_CACHE_DIR', 'SSL_CERT_FILE', 'SSL_CERT_DIR',
    'REQUESTS_CA_BUNDLE', 'CUDA_PATH', 'CUDA_VISIBLE_DEVICES', 'OMP_NUM_THREADS',
    'MKL_NUM_THREADS', 'PYTORCH_ENABLE_MPS_FALLBACK', 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH',
}


def process_environment():
    environment = {key: value for key, value in os.environ.items() if key.upper() in _ALLOWED}
    environment.update(PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    return environment
