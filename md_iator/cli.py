"""Command-line entry point for md_iator."""

import argparse
import os
import sys
from importlib import metadata
from pathlib import Path

import md_iator


def version() -> str:
    try:
        return f"md-iator {metadata.version('md-iator')}"
    except metadata.PackageNotFoundError:
        return "md-iator (version inconnue : paquet non installé)"


def format_summary(summary: md_iator.Summary) -> str:
    def count(n: int, word: str) -> str:
        # French plural: singular for 0 and 1.
        return f"{n} {word}{'s' if n > 1 else ''}"

    parts = [count(summary.converted, "converti")]
    if summary.empty:
        parts.append(count(summary.empty, "vide"))
    if summary.skipped:
        parts.append(count(summary.skipped, "ignoré"))
    if summary.errors:
        parts.append(count(summary.errors, "erreur"))
    return " · ".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="md-iator",
        description="Convertit des fichiers DOCX et PDF en Markdown.",
        # Replaced below so its help line reads in French.
        add_help=False,
    )
    parser.add_argument(
        "-h", "--help", action="help",
        help="afficher cette aide et quitter",
    )
    parser.add_argument(
        "--version", action="version", version=version(),
        help="afficher la version et quitter",
    )
    parser.add_argument("input", metavar="SOURCE", help="fichier ou dossier source")
    parser.add_argument(
        "-o", "--output",
        metavar="SORTIE",
        help="fichier .md de sortie (mode fichier unique) ou dossier de sortie (mode batch)",
        default=None,
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="ne pas reconvertir une source dont le .md existe déjà "
        "(reprise après interruption)",
    )
    args = parser.parse_args()

    src = Path(args.input)
    output = Path(args.output) if args.output else None

    if not src.exists():
        parser.error(f"chemin introuvable : {src}")

    # Path() drops the trailing separator, so "-o out/" must be created here
    # for convert_file to see a directory rather than a file name.
    if args.output and args.output.endswith(("/", os.sep)):
        output.mkdir(parents=True, exist_ok=True)

    try:
        if src.is_dir():
            summary = md_iator.batch_convert(src, output, args.skip_existing)
            if summary == md_iator.Summary():
                extensions = " ou ".join(sorted(md_iator.SUPPORTED_EXTENSIONS))
                print(f"aucun fichier {extensions} dans {src}")
            else:
                print(f"\n{format_summary(summary)}")
            sys.exit(1 if summary.errors else 0)
        else:
            dest = md_iator.output_path(src, output)
            if args.skip_existing and dest.exists():
                print(f"ignoré : {dest} existe déjà", file=sys.stderr)
                return
            try:
                dest = md_iator.convert_file(src, output)
                print(f"converti : {dest}")
            except md_iator.EmptyDocumentError as exc:
                print(f"vide : {src} — {exc}", file=sys.stderr)
            except Exception as exc:
                print(f"erreur : {exc}", file=sys.stderr)
                sys.exit(1)
    except md_iator.BatchInterrupted as exc:
        print(f"\n{format_summary(exc.summary)}")
        print(
            f"interrompu — {exc.summary.processed}/{exc.total} fichiers traités, "
            "aucun fichier partiel. Relancer avec --skip-existing pour reprendre.",
            file=sys.stderr,
        )
        sys.exit(130)
    except KeyboardInterrupt:
        print("\ninterrompu — aucun fichier partiel.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
