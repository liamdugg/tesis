# Choose TeX engine for PDF generation. Options are:
# 1: PDFLaTeX
# 2: Postscript Conversion
# 3: DVI Conversion
# 4: LuaLaTeX
# 5: XeLaTeX
$pdf_mode = 5;
# Main TeX file.
$root_filename = 'IPLeiriaMain.tex';
# Additional flags for the TeX engine.
set_tex_cmds("--shell-escape --synctex=1 --file-line-error --halt-on-error %O %S");
# Extra extensions of files to remove in a clean-up.
$clean_ext = 'aux bbl blg brf idx ilg ind lof log lot out toc fdb_latexmk fls synctex.gz';
# Modify the default 'biber' call to improve error detection and clarity.
$biber = "biber --validate-datamodel %O %S";
# Delete the .bbl file during clean-up if the bibliography file is present.
$bibtex_use = 1.5;
# Show used CPU time.
$show_time = 1;
# Write all auxiliary files in a separate directory
$aux_dir = '.aux';
add_cus_dep('glo', 'gls', 0, 'run_makeglossaries');
add_cus_dep('acn', 'acr', 0, 'run_makeglossaries');
sub run_makeglossaries {
    my ($base_name, $path) = fileparse($_[0]);
    pushd $path;
    if ($silent) {
        #system "makeglossaries -q '$base_name'";        # For Unix-based systems.
        system "makeglossaries", "-q", "$base_name";  # For Windows-based systems.
    } else {
        #system "makeglossaries '$base_name'";           # For Unix-based systems.
        system "makeglossaries", "$base_name";        # For Windows-based systems.
    };
    popd;
}
$success_cmd = "echo '[ OK ] Compilation of $root_filename successful!'";

# Crear automáticamente, dentro de $aux_dir, la misma jerarquía de
# carpetas que contienen archivos .tex en el proyecto. Esto es necesario
# porque \include escribe un .aux por cada archivo incluido, en la misma
# subcarpeta relativa dentro de $aux_dir, y LaTeX no crea esas subcarpetas
# por si solo. La version anterior usaba find/sed/xargs (shell Unix), lo
# cual no funciona en Windows. Este bloque usa solo Perl puro y es
# portable entre Windows, Mac y Linux.
use File::Path qw(make_path);
use File::Find;
use File::Spec;

my %dirs_to_make;
find(sub {
    return unless -f $_ && /\.tex$/;
    my $reldir = File::Spec->abs2rel($File::Find::dir, '.');
    $dirs_to_make{$reldir} = 1 unless $reldir eq '.';
}, '.');

for my $d (keys %dirs_to_make) {
    make_path("$aux_dir/$d");
}

# La libreria tikz externalization escribe los .md5/.dpth/.pdf de cada
# figura en una carpeta "tikz" relativa a $aux_dir (por ejemplo
# tikz/IPLeiriaMain-figure0.md5). Esa carpeta no necesariamente contiene
# archivos .tex, asi que el bloque anterior no la detecta. Se crea aca
# de forma explicita para evitar el mismo error con \tikzpicture.
make_path("$aux_dir/tikz");
