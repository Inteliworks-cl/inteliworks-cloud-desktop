# Inteliworks Cloud — cliente de escritorio

Cliente de sincronización de escritorio **Inteliworks Cloud** para Windows y macOS.
Es el [cliente oficial de Nextcloud](https://github.com/nextcloud/desktop) con la marca
de Inteliworks aplicada en tiempo de compilación (nombre, iconos, colores, sin
auto-actualizaciones de Nextcloud).

Cada empresa cliente tiene su propio servidor (`https://cloud.<empresa>.cl`). El asistente
de primera conexión viene pre-llenado con `https://cloud.` y el usuario completa su dominio.

## Descargas

Los instaladores se publican en **Releases** de este repositorio
(y como *artifacts* de cada ejecución de *Actions*):

| Sistema | Archivo | Notas |
|---|---|---|
| Windows 10/11 x64 | `InteliworksCloud-<versión>-x64.msi` | Recomendado (instalación silenciosa / GPO) |
| Windows 10/11 x64 | `InteliworksCloud-<versión>-x64-setup.exe` | Instalador NSIS alternativo |
| macOS 13+ (Apple Silicon) | `InteliworksCloud-<versión>-macos-arm64.dmg` | |

**Los instaladores no están firmados** (decisión vigente, sin certificados de firma):

- **Windows**: SmartScreen mostrará "Windows protegió su PC" → *Más información* → *Ejecutar de todas formas*.
- **macOS**: la primera vez, clic derecho sobre la app → *Abrir* → *Abrir*.
  Si macOS dice que "está dañada": `xattr -cr "/Applications/Inteliworks Cloud.app"`.

Instalación silenciosa en Windows (MSI): `msiexec /i InteliworksCloud-<versión>-x64.msi /qn`.

## Cómo está armado este repo

Este repo **no** contiene una copia del código de Nextcloud. Contiene solo la capa de marca:

```
UPSTREAM_VERSION              tag de nextcloud/desktop que se compila (ej. v35.0.3)
branding/source/icon.png      logo fuente (512x512)
branding/theme/               iconos y logos generados (se copian sobre theme/ de upstream)
scripts/generate-assets.php   genera branding/theme/ desde icon.png (PHP + GD)
scripts/apply_branding.py     aplica la marca: NEXTCLOUD.cmake, theme/, blueprint de Craft
.github/workflows/build.yml   compila Windows (Craft + NSIS + WiX) y macOS (mac-crafter)
```

El workflow:

1. Clona `nextcloud/desktop` en el tag de `UPSTREAM_VERSION`.
2. Ejecuta `scripts/apply_branding.py source` (nombre, ejecutable `inteliworkscloud.exe`,
   vendor, color `#1E90D6`, GUIDs propios de MSI/extensiones de shell, updater desactivado,
   URL de ayuda, servidor pre-llenado editable, sin lista de proveedores de Nextcloud).
3. Instala las dependencias con KDE Craft usando la caché binaria de Nextcloud (igual que el CI de upstream).
4. Compila y empaqueta: Windows `.exe` (NSIS) + `.msi` (WiX 3.14); macOS `.app` → `.dmg` con firma ad-hoc.
5. En un tag `v*` crea el Release **"Inteliworks Cloud &lt;versión&gt;"** con los instaladores.

Toda la configuración de marca está al principio de `scripts/apply_branding.py`.
Si upstream cambia algún archivo y un reemplazo deja de calzar, el script **falla a propósito**
(nunca se publica un binario a medio marcar): hay que ajustar el patrón correspondiente.

## Actualizar a una nueva versión de Nextcloud

1. Ver la última versión estable en <https://github.com/nextcloud/desktop/releases> (ej. `v35.0.4`).
2. Editar `UPSTREAM_VERSION` con ese tag, commit y push a `main`:
   el workflow compila y deja los instaladores como *artifacts* para probar.
3. Probar el instalador (instalar, conectar a `https://cloud.inteliworks.cl`, sincronizar).
4. Publicar: crear un tag `v<versión-upstream>` (o `v<versión>-<n>` si es una re-compilación
   de la misma versión, ej. `v35.0.4-2`) y hacer push del tag:
   ```bash
   git tag v35.0.4 && git push origin v35.0.4
   ```
   Esto genera el Release con los instaladores adjuntos.

Si cambia la rama de Craft en upstream (`craftmaster.ini`), la caché se reconstruye sola
(la primera compilación tarda más).

Para cambiar el logo: reemplazar `branding/source/icon.png` (PNG cuadrado ≥ 512 px) y ejecutar
`php scripts/generate-assets.php`; commitear los archivos generados.

## Pendiente / limitaciones

- **Firma de código**: sin certificado, Windows/macOS muestran advertencias. Para quitarlas hace falta
  un certificado Authenticode (Windows, idealmente EV/OV) y una cuenta Apple Developer (USD 99/año)
  para firmar y notarizar. Se cargarían como *secrets* del repo.
- **macOS Intel (x86_64)**: el build actual es solo Apple Silicon (arm64).
- **Actualizaciones automáticas**: desactivadas. Las nuevas versiones se descargan desde Releases.

## Licencia y atribución

Este proyecto es una compilación con marca de **Nextcloud Desktop Client**,
© Nextcloud GmbH y colaboradores, © ownCloud GmbH, distribuido bajo
**GNU GPL v2.0 o posterior** (ver [`LICENSE`](LICENSE)). El código fuente correspondiente a
cada binario es el tag de <https://github.com/nextcloud/desktop> indicado en `UPSTREAM_VERSION`
más las modificaciones de este repositorio (`scripts/apply_branding.py`).

"Nextcloud" es una marca registrada de Nextcloud GmbH. Inteliworks Cloud no está afiliado
ni respaldado por Nextcloud GmbH. Logo e identidad "Inteliworks" © Inversiones Tecnológicas JPC SpA.

Soporte: soporte@inteliworks.cl · <https://inteliworks.cl>
