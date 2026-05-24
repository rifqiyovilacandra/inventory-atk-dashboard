import os
import hashlib

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.png')
DEFAULT_ADMIN_USERNAME = 'fam_admin'
DEFAULT_ADMIN_PASSWORD_HASH = hashlib.sha256('Fam@Inventory2026'.encode()).hexdigest()
ADMIN_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin_config.json')

REQUIRED_COLS = ['Tanggal_Persetujuan', 'Tanggal_Permintaan', 'Jenis_ATK', 'Divisi', 'Jumlah', 'Unit']

MONTH_NAMES = {
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mei', 6: 'Jun',
    7: 'Jul', 8: 'Agu', 9: 'Sep', 10: 'Okt', 11: 'Nov', 12: 'Des'
}

PALETTE = {
    'bg':             '#1565C0',
    'bg_dark':        '#0D47A1',
    'accent':         '#F57C00',
    'accent_light':   '#FFB74D',
    'secondary':      '#42A5F5',
    'surface':        '#F5F7FA',
    'card':           '#FFFFFF',
    'text':           '#FFFFFF',
    'text_dark':      '#212121',
    'border':         '#E0E0E0',
    'cluster_colors': ['#2E7D32', '#FBC02D', '#D32F2F', '#6A1B9A'],
    'nav_bg':         '#0D47A1',
}

LABEL_COLORS = {
    'Rendah':          '#2E7D32',
    'Sedang':          '#FBC02D',
    'Tinggi':          '#D32F2F',
    'Slow Moving':     '#2E7D32',
    'Medium Moving':   '#FBC02D',
    'Fast Moving':     '#D32F2F',
    'Prioritas Rendah':'#2E7D32',
    'Prioritas Sedang':'#FBC02D',
    'Prioritas Tinggi':'#6A1B9A',
}
