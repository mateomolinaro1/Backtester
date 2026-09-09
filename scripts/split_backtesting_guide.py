from __future__ import annotations

import re
import shutil
from pathlib import Path


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

SOURCE_FILE = Path("docs/BACKTESTING_GUIDE.md")
OUTPUT_DIR = Path("docs/backtesting")

# Split the guide whenever we encounter this Markdown heading level.
#
# ## Chapter
# ^ level 2
SPLIT_HEADING_LEVEL = 3

INDEX_FILENAME = "INDEX.md"


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def slugify(title: str) -> str:
    """
    Convert a Markdown heading into a filesystem-friendly slug.

    Example
    -------
    "3. Point-in-Time Data"
        -> "03_point_in_time_data"
    """

    title = title.strip()

    # Detect an optional leading chapter number.
    match = re.match(r"^(\d+)[.\-\s:]+(.+)$", title)

    if match:
        number = int(match.group(1))
        text = match.group(2)
        prefix = f"{number:02d}_"
    else:
        text = title
        prefix = ""

    # Normalize common characters.
    text = text.lower()
    text = text.replace("&", "and")

    # Keep only letters, numbers, spaces, hyphens, underscores.
    text = re.sub(r"[^\w\s-]", "", text)

    # Replace whitespace / hyphens by underscores.
    text = re.sub(r"[\s-]+", "_", text)

    # Remove duplicate underscores.
    text = re.sub(r"_+", "_", text)

    text = text.strip("_")

    return f"{prefix}{text}"


def extract_heading_title(line: str, level: int) -> str | None:
    """
    Return the heading text if `line` is a Markdown heading
    of exactly the requested level.
    """

    prefix = "#" * level

    match = re.match(
        rf"^{re.escape(prefix)}\s+(.+?)\s*$",
        line,
    )

    if not match:
        return None

    return match.group(1).strip()


def extract_subheadings(
    content: list[str],
    min_level: int = 3,
    max_level: int = 4,
) -> list[tuple[int, str]]:
    """
    Extract Markdown subheadings from a chapter.

    Returns
    -------
    [
        (3, "2.1 Publication dates"),
        (3, "2.2 Survivorship bias"),
        (4, "2.2.1 Example"),
    ]
    """

    headings: list[tuple[int, str]] = []

    pattern = re.compile(
        rf"^(#{{{min_level},{max_level}}})\s+(.+?)\s*$"
    )

    for line in content:
        match = pattern.match(line)

        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            headings.append((level, title))

    return headings


# ---------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------

def parse_guide(
    text: str,
) -> tuple[list[str], list[dict]]:
    """
    Split the complete Markdown document into:

    - preamble: everything before the first chapter;
    - chapters: each level-2 section.
    """

    lines = text.splitlines(keepends=True)

    preamble: list[str] = []
    chapters: list[dict] = []

    current_chapter: dict | None = None

    for line in lines:
        title = extract_heading_title(
            line,
            SPLIT_HEADING_LEVEL,
        )

        if title is not None:
            if current_chapter is not None:
                chapters.append(current_chapter)

            current_chapter = {
                "title": title,
                "content": [line],
            }

        elif current_chapter is None:
            preamble.append(line)

        else:
            current_chapter["content"].append(line)

    if current_chapter is not None:
        chapters.append(current_chapter)

    return preamble, chapters


# ---------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------

def write_chapters(chapters: list[dict]) -> list[dict]:
    """
    Write each chapter into its own Markdown file.

    Returns metadata used later to generate INDEX.md.
    """

    metadata: list[dict] = []

    for position, chapter in enumerate(chapters, start=1):
        title = chapter["title"]
        content = chapter["content"]

        slug = slugify(title)

        # Fallback when chapter headings are not numbered.
        if not re.match(r"^\d{2}_", slug):
            slug = f"{position:02d}_{slug}"

        filename = f"{slug}.md"
        filepath = OUTPUT_DIR / filename

        filepath.write_text(
            "".join(content),
            encoding="utf-8",
        )

        subheadings = extract_subheadings(content)

        metadata.append(
            {
                "title": title,
                "filename": filename,
                "subheadings": subheadings,
            }
        )

        print(f"Created: {filepath}")

    return metadata


def create_index(
    preamble: list[str],
    chapters: list[dict],
) -> None:
    """
    Generate a lightweight routing index for Claude.
    """

    output: list[str] = []

    output.append("# Backtesting Methodology Index\n\n")

    output.append(
        "This file is the routing table for the backtesting methodology.\n\n"
    )

    output.append(
        "**Do not read the complete `BACKTESTING_GUIDE.md` during normal "
        "development.**\n\n"
    )

    output.append(
        "Identify the methodological topic affected by the task and read "
        "only the corresponding files below.\n\n"
    )

    output.append(
        "The complete original specification remains available at:\n\n"
    )

    output.append(
        "`docs/BACKTESTING_GUIDE.md`\n\n"
    )

    output.append("---\n\n")

    output.append("## Methodology Map\n\n")

    output.append("| Topic | Specification |\n")
    output.append("|---|---|\n")

    for chapter in chapters:
        title = chapter["title"]
        filename = chapter["filename"]

        output.append(
            f"| {title} | [`{filename}`](./{filename}) |\n"
        )

    output.append("\n---\n\n")

    output.append("## Detailed Contents\n\n")

    for chapter in chapters:
        title = chapter["title"]
        filename = chapter["filename"]
        subheadings = chapter["subheadings"]

        output.append(
            f"### [{title}](./{filename})\n\n"
        )

        if not subheadings:
            output.append(
                "_No lower-level headings detected._\n\n"
            )
            continue

        for level, subtitle in subheadings:
            indent = "  " * max(level - 3, 0)
            output.append(
                f"{indent}- {subtitle}\n"
            )

        output.append("\n")

    index_path = OUTPUT_DIR / INDEX_FILENAME

    index_path.write_text(
        "".join(output),
        encoding="utf-8",
    )

    print(f"Created: {index_path}")


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Cannot find source guide: {SOURCE_FILE}"
        )

    source_text = SOURCE_FILE.read_text(
        encoding="utf-8",
    )

    preamble, chapters = parse_guide(source_text)

    if not chapters:
        raise RuntimeError(
            f"No level-{SPLIT_HEADING_LEVEL} headings found in "
            f"{SOURCE_FILE}."
        )

    # Rebuild output directory from scratch.
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    chapter_metadata = write_chapters(chapters)

    create_index(
        preamble=preamble,
        chapters=chapter_metadata,
    )

    print()
    print(
        f"Done: {len(chapter_metadata)} chapters generated."
    )


if __name__ == "__main__":
    main()