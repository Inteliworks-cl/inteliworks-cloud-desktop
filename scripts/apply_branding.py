#!/usr/bin/env python3
"""Aplica la marca "Inteliworks Cloud" sobre un checkout de nextcloud/desktop.

Uso:
  python apply_branding.py source    <dir-checkout-upstream>
  python apply_branding.py blueprint <dir-raiz-craft>   (despues de 'craft --install-deps')

Cada reemplazo debe calzar EXACTAMENTE una vez: si upstream cambia el archivo,
el script falla en voz alta (no se genera un binario a medio marcar).
"""
import os
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRANDING = HERE.parent / "branding"

# ---- Valores de marca (unica fuente de verdad) -------------------------------
NAME = "Inteliworks Cloud"          # nombre visible (ventanas, menu Inicio, .app)
SHORTNAME = "InteliworksCloud"      # sin espacios: iconos, MSI, carpetas internas
EXECUTABLE = "inteliworkscloud"     # inteliworkscloud.exe / inteliworkscloudcmd.exe
VENDOR = "Inteliworks"
DOMAIN = "inteliworks.cl"
HELP_URL = "https://inteliworks.cl"
SERVER_URL_HINT = "https://cloud."  # pre-llenado editable; cada empresa escribe el suyo
REV_DOMAIN = "cl.inteliworks.cloud"
BRAND_COLOR = "#1E90D6"
UPDATE_URL = "https://github.com/Inteliworks-cl/inteliworks-cloud-desktop/releases"
# GUIDs propios (NO reutilizar los de Nextcloud: chocarian si ambos estan instalados)
GUIDS = {
    "WIN_SHELLEXT_CONTEXT_MENU_GUID": "{9A6A41F8-1C19-4DBA-9B68-4090549FB3AD}",
    "WIN_SHELLEXT_OVERLAY_GUID_ERROR": "{4717D942-B3FF-4522-A2A8-40345F00021C}",
    "WIN_SHELLEXT_OVERLAY_GUID_OK": "{DD5A7581-B214-48E9-89AF-643BCFAED59B}",
    "WIN_SHELLEXT_OVERLAY_GUID_OK_SHARED": "{1202765B-5B79-42A8-A872-27CCCA5ECDEE}",
    "WIN_SHELLEXT_OVERLAY_GUID_SYNC": "{4251C410-3930-447A-8643-133BCB8E4081}",
    "WIN_SHELLEXT_OVERLAY_GUID_WARNING": "{ADF6DFD6-B99A-4B03-B157-CA6C3D1FBBE7}",
    "WIN_MSI_UPGRADE_CODE": "7A3E9CEC-1982-4135-8A43-DE5016F75EA2",
}


def sub_once(text: str, pattern: str, repl: str, where: str) -> str:
    new, n = re.subn(pattern, lambda _m: repl, text, flags=re.M)
    if n != 1:
        sys.exit(f"ERROR [{where}]: el patron {pattern!r} calzo {n} veces (se esperaba 1). "
                 "Upstream cambio: revisar scripts/apply_branding.py")
    return new


def set_var(text: str, var: str, value: str, where: str) -> str:
    """Reemplaza 'set( VAR  "..." ...)' (fuera del bloque NEXTCLOUD_DEV) por el valor de marca."""
    pattern = rf'^(\s*)set\(\s*{var}\s+"[^"]*"(.*)\)[ \t]*$'
    hits = [m for m in re.finditer(pattern, text, flags=re.M)]
    # El bloque if(NEXTCLOUD_DEV) tiene una copia "Dev"; nos quedamos con la ultima (rama else / global)
    if not hits:
        sys.exit(f"ERROR [{where}]: no se encontro set({var} ...)")
    m = hits[-1]
    line = f'{m.group(1)}set( {var} "{value}"{m.group(2)})'
    return text[:m.start()] + line + text[m.end():]


def brand_source(src: Path) -> None:
    cm = src / "NEXTCLOUD.cmake"
    t = cm.read_text(encoding="utf-8")
    w = "NEXTCLOUD.cmake"
    t = set_var(t, "APPLICATION_NAME", NAME, w)
    t = set_var(t, "APPLICATION_SHORTNAME", SHORTNAME, w)
    t = set_var(t, "APPLICATION_EXECUTABLE", EXECUTABLE, w)
    # APPLICATION_ICON_NAME queda = "${APPLICATION_SHORTNAME}" (rama no-dev de upstream)
    t = set_var(t, "APPLICATION_DOMAIN", DOMAIN, w)
    t = set_var(t, "APPLICATION_VENDOR", VENDOR, w)
    # Sin actualizaciones de Nextcloud sobre la app con marca: updater desactivado y la URL
    # (que theme.cpp exige definida) apunta a nuestros Releases, nunca a updates.nextcloud.org
    t = set_var(t, "APPLICATION_UPDATE_URL", UPDATE_URL, w)
    t = sub_once(t, r'^option\(\s*BUILD_UPDATER\s+"Build updater"\s+ON\s*\)',
                 'option( BUILD_UPDATER "Build updater" OFF )', w)
    t = set_var(t, "APPLICATION_HELP_URL", HELP_URL, w)
    t = set_var(t, "APPLICATION_SERVER_URL", SERVER_URL_HINT, w)
    t = sub_once(t, r'^set\(\s*APPLICATION_SERVER_URL_ENFORCE\s+ON\s*\)',
                 'set( APPLICATION_SERVER_URL_ENFORCE OFF )', w)
    t = set_var(t, "APPLICATION_REV_DOMAIN", REV_DOMAIN, w)
    t = set_var(t, "APPLICATION_REV_DOMAIN_DBUS", "cloud.inteliworks.cl", w)
    t = set_var(t, "APPLICATION_VIRTUALFILE_SUFFIX", EXECUTABLE, w)
    t = set_var(t, "LINUX_PACKAGE_SHORTNAME", EXECUTABLE, w)
    t = set_var(t, "NEXTCLOUD_BACKGROUND_COLOR", BRAND_COLOR, w)
    # Lista de proveedores de Nextcloud (registro en terceros): fuera
    t = sub_once(t, r'^option\(\s*WITH_PROVIDERS\s+"Build with providers list"\s+ON\s*\)',
                 'option( WITH_PROVIDERS "Build with providers list" OFF )', w)
    # Construye los scripts MSI (admin/win/msi) para generar el instalador .msi
    t = sub_once(t, r'^(\s*)option\(\s*BUILD_WIN_MSI\s+"Build MSI scripts and helper DLL"\s+OFF\s*\)',
                 '    option( BUILD_WIN_MSI "Build MSI scripts and helper DLL" ON )', w)
    for var, guid in GUIDS.items():
        t = set_var(t, var, guid, w)
    cm.write_text(t, encoding="utf-8")
    print(f"  {w}: marca aplicada")

    # Archivos de marca (iconos, logo del asistente, tiles, imagenes MSI): branding/<ruta> -> <upstream>/<ruta>
    for f in BRANDING.rglob("*"):
        rel = f.relative_to(BRANDING)
        if f.is_file() and rel.parts[0] != "source":
            dst = src / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
            print(f"  {rel.as_posix()}")

    # No compilar la suite de tests en el build de release (ahorra ~30-40 min)
    ini = src / "craftmaster.ini"
    t = ini.read_text(encoding="utf-8")
    t = sub_once(t, r'^nextcloud-client\.buildTests\s*=\s*True\s*$',
                 'nextcloud-client.buildTests = False', "craftmaster.ini")
    ini.write_text(t, encoding="utf-8")
    print("  craftmaster.ini: buildTests=False")


def brand_blueprint(craft_root: Path) -> None:
    candidates = list(craft_root.rglob("craft-blueprints-nextcloud/nextcloud-client/nextcloud-client.py"))
    if len(candidates) != 1:
        sys.exit(f"ERROR: se esperaba 1 blueprint nextcloud-client.py bajo {craft_root}, hay {candidates}")
    bp = candidates[0]
    t = bp.read_text(encoding="utf-8")
    w = "nextcloud-client.py"
    t = sub_once(t, r'self\.displayName = "Nextcloud"', f'self.displayName = "{NAME}"', w)
    t = sub_once(t, r'self\.webpage = "https://nextcloud.com"', f'self.webpage = "{HELP_URL}"', w)
    t = sub_once(t, r'self\.defines\["appname"\] = "nextcloud"',
                 # macOS: nombre del .app ; Windows: datos del instalador NSIS
                 f'self.defines["appname"] = "{NAME}"\n'
                 f'        self.defines["productname"] = "{NAME}"\n'
                 f'        self.defines["display_name"] = "{NAME}"\n'
                 f'        self.defines["website"] = "{HELP_URL}"\n'
                 f'        self.defines["executable"] = r"bin\\{EXECUTABLE}.exe"\n'
                 f'        self.defines["icon"] = os.path.join(self.buildDir(), "src", "gui", "{SHORTNAME}.ico")\n'
                 f'        if os.environ.get("IW_VERSION"): self.defines["version"] = os.environ["IW_VERSION"]', w)
    t = sub_once(t, r'self\.defines\["company"\] = "Nextcloud GmbH"', f'self.defines["company"] = "{VENDOR}"', w)
    t = sub_once(t, r'self\.applicationExecutable = "nextcloud"',
                 f'self.applicationExecutable = "{EXECUTABLE}"', w)
    if not re.search(r"^import os\b", t, re.M):   # el bloque de marca usa os.* (el blueprint upstream no lo importa)
        t = "import os\n" + t
    bp.write_text(t, encoding="utf-8")
    print(f"  {bp}: marca aplicada")

    bl = bp.parent / "blacklist.txt"
    t = bl.read_text(encoding="utf-8")
    t = sub_once(t, r'^bin/\(\?!\(nextcloud\|nextcloudcmd\|',
                 f'bin/(?!({EXECUTABLE}|{EXECUTABLE}cmd|', "blacklist.txt")
    bl.write_text(t, encoding="utf-8")
    print(f"  {bl}: ejecutables de marca preservados")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("source", "blueprint"):
        sys.exit(__doc__)
    target = Path(sys.argv[2]).resolve()
    if sys.argv[1] == "source":
        brand_source(target)
    else:
        brand_blueprint(target)
