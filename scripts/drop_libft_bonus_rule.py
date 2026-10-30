#!/usr/bin/env python3
"""Stop war-machine from requiring a libft bonus Makefile rule."""

from pathlib import Path
import sys

PATH = Path("/francinette/tests/libft/war-machine/srcs/compil_lib.sh")

OLD = """\t\trm -f \"${PATH_LIBFT}\"/ft_*.o
\t\trm -f \"${PATH_LIBFT}\"/libft.a
\t\tprintf \"\\n$> make bonus\\n\" >> \"${PATH_DEEPTHOUGHT}\"/deepthought
\t\tmake --no-print-directory -C \"${PATH_LIBFT}\" bonus>>\"${PATH_DEEPTHOUGHT}\"/deepthought 2>&1
\t\tresult_bonus=1
\t\tif [ -z \"$(grep -w bonus \"${PATH_LIBFT}\"/${MAKEFILE_VAR} | tr -d ' ' | tr -d '\\t' | cut -d ':' -f 1 | grep -w bonus)\" ]
\t\t\tthen
\t\t\t\tprintf \"\\033[64G${COLOR_FAIL}missing${DEFAULT}\"
\t\t\t\tresult_bonus=0
\t\t\telse
\t\t\t\tif [ -e \"${PATH_LIBFT}\"/libft.a ]
\t\t\t\tthen
\t\t\t\t\tprintf \"\\033[64G${COLOR_OK}ok${DEFAULT}\"
\t\t\t\telse
\t\t\t\t\tprintf \"\\033[64G${COLOR_FAIL}fail${DEFAULT}\"
\t\t\t\t\tresult_bonus=0
\t\t\t\tfi
\t\t\tfi
\t\tif [ $result_bonus -eq 0 ]; then
\t\t\tmake --no-print-directory -C \"${PATH_LIBFT}\" all>>\"${PATH_DEEPTHOUGHT}\"/deepthought 2>&1
\t\tfi
"""

NEW = """\t\trm -f \"${PATH_LIBFT}\"/ft_*.o
\t\trm -f \"${PATH_LIBFT}\"/libft.a
\t\tprintf \"\\n$> make all (lists are mandatory, no bonus rule)\\n\" >> \"${PATH_DEEPTHOUGHT}\"/deepthought
\t\tmake --no-print-directory -C \"${PATH_LIBFT}\" all>>\"${PATH_DEEPTHOUGHT}\"/deepthought 2>&1
\t\tprintf \"\\033[64G${COLOR_OK}n/a${DEFAULT}\"
"""


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else PATH
    text = target.read_text()
    if OLD not in text:
        if NEW in text and 'printf "\\033[64Glists"' in text:
            print(f"already updated {target}")
            return
        sys.exit(f"bonus block not found in {target}")
    text = text.replace(OLD, NEW, 1)
    text = text.replace('printf "\\033[64Gbonus"', 'printf "\\033[64Glists"', 1)
    target.write_text(text)
    print(f"updated {target}")


if __name__ == "__main__":
    main()
