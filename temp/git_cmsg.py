import re
import os


def update_novel_title_version(url, title_file="novel_title.txt"):
    """Extract the title from the given URL and update the version in title_file."""
    url_pattern = re.compile(r'url\s*=\s*"https?://[^/]+/b/([^"#]+)')
    title_match = url_pattern.search(f'url = "{url}"')
    if not title_match:
        print("❌ Could not extract title from the URL.")
        return

    title = title_match.group(1)
    new_version = "v1.0"

    if os.path.exists(title_file):
        with open(title_file, "r") as nt:
            existing_line = nt.read().strip()
        match = re.match(r"(.+?)\s*\((v\d+(?:\.\d+)?)\)", existing_line)

        if match:
            existing_title, existing_version = match.groups()
            if existing_title == title:
                version_num = [int(x) for x in existing_version.lstrip("v").split(".")]
                if len(version_num) == 1:
                    version_num.append(1)  # v1 -> v1.1
                else:
                    version_num[-1] += 1
                new_version = "v" + ".".join(map(str, version_num))
            else:
                new_version = "v1.0"

    with open(title_file, "w") as nt:
        nt.write(f"{title} ({new_version})")

    print(f"✅ Done! Updated {title_file} with: {title} ({new_version})")

