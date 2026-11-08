<?php
// Genera los iconos de marca a partir de branding/source/icon.png (PNG cuadrado, >=512px).
// Uso: php scripts/generate-assets.php
// Requiere la extension GD. Los archivos resultantes se commitean en branding/theme/.
// Re-ejecutar solo si cambia el logo.

$root   = dirname(__DIR__);
$src    = "$root/branding/source/icon.png";
$out    = "$root/branding/theme/colored";
$name   = 'InteliworksCloud';            // = APPLICATION_ICON_NAME (ver scripts/apply_branding.py)
$exe    = 'inteliworkscloud';            // = APPLICATION_EXECUTABLE
$brand  = '#1E90D6';

if (!is_dir($out)) mkdir($out, 0755, true);
$img = imagecreatefrompng($src) or die("no se pudo leer $src\n");

function resized($img, int $w, int $h) {
    $dst = imagecreatetruecolor($w, $h);
    imagealphablending($dst, false);
    imagesavealpha($dst, true);
    imagefill($dst, 0, 0, imagecolorallocatealpha($dst, 0, 0, 0, 127));
    imagecopyresampled($dst, $img, 0, 0, 0, 0, $w, $h, imagesx($img), imagesy($img));
    return $dst;
}
function png($img, string $path) { imagepng($img, $path, 9); echo "  $path\n"; }
function svgEmbed(string $pngPath, int $size): string {
    $b64 = base64_encode(file_get_contents($pngPath));
    return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
         . "<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" width=\"$size\" height=\"$size\" viewBox=\"0 0 $size $size\">"
         . "<image width=\"$size\" height=\"$size\" xlink:href=\"data:image/png;base64,$b64\" href=\"data:image/png;base64,$b64\"/></svg>\n";
}

echo "Generando iconos en $out\n";
// Icono de la aplicacion: tamanos que el CMake de upstream espera (si existen, no los regenera con inkscape)
foreach ([16, 20, 24, 32, 40, 48, 64, 128, 256, 512, 1024] as $s) {
    png(resized($img, $s, $s), "$out/$s-$name-icon.png");
}
file_put_contents("$out/$name-icon.svg", svgEmbed("$out/512-$name-icon.png", 512));
file_put_contents("$out/$name-w10startmenu.svg", svgEmbed("$out/512-$name-icon.png", 512));
// Tiles del menu Inicio de Windows (VisualElements)
foreach ([70, 150] as $s) {
    png(resized($img, $s, $s), "$out/$s-$name-w10startmenu.png");
}
// Logo del asistente (cabecera y pantalla de bienvenida)
png(resized($img, 63, 63), "$out/wizard_logo.png");
png(resized($img, 126, 126), "$out/wizard_logo@2x.png");
file_put_contents("$out/wizard_logo.svg", svgEmbed("$out/wizard_logo@2x.png", 126));
// Manifest de Windows para los tiles
file_put_contents(dirname($out) . "/$exe.VisualElementsManifest.xml",
"<Application xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <VisualElements
    BackgroundColor=\"$brand\"
    ForegroundText=\"light\"
    ShowNameOnSquare150x150Logo=\"on\"
    Square150x150Logo=\"visualelements\\150-$name-w10startmenu.png\"
    Square70x70Logo=\"visualelements\\70-$name-w10startmenu.png\"/>
</Application>
");
echo "OK\n";
