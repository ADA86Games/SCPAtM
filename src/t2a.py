from lxml import etree
from typing import Dict
from argparse import ArgumentParser
import re


def get_texts(file_name) -> Dict[str, str]:
    """
    Get the texts of passages from the given file name

    :param file_name:  Name of the file to use.
    :return: The texts in a dictionary with their titles as keys.
    """
    html_parser = etree.HTMLParser()
    tree = etree.parse(file_name, html_parser)
    root = tree.getroot()
    texts = {}
    for game_text in root.iter('tw-passagedata'):
        texts[game_text.attrib['name']] = game_text.text
    return texts


def convert_harlowe_to_plain(text: str) -> str:
    """
    Harlowe by default shows choices as [[choiceText->branch]],
        we are only interested in the text section, and we want
        to replace the [[ part with enumeration, let us go!.
    :param text: Text to scan and replace.
    :return: the replaced version.
    """
    text = re.sub(r'->(.*?)\]]', '', text)
    count = 1
    text = text.replace('[[auto', '')
    while text.find('[[') != -1:
        text = text.replace('[[', f"({count}) ", 1)
        count += 1
    return text


def convert_to_fasm(texts: Dict[str, str]) -> str:
    """
    Convert the Harlowe passage texts to the format suitable
        for 16 Bit DOS FASM x86_64 Assembly.

    :param texts: Texts to convert, as dictionary.
    :return: The output string.
    """
    output_str = ""
    for title, value in texts.items():
        value = value.replace("\"", "\\\"")  # Escape the quotes.
        value = value.replace("\n", "\", lf, cr, \"")  # Replace new lines with line feed and cr.
        title = title.strip() # Strip the generated extra space by twine, why is it there, I don't know.
        value = convert_harlowe_to_plain(value)
        output_str += f"{title}\tdb\t\"{value}\", '$'\n"
    return output_str


if __name__ == '__main__':
    parser = ArgumentParser(prog='Twine2Assembler', description='Convert the Twine HTML to Assembler data segment.')
    parser.add_argument('--file', type=str, help='The file to convert from.')
    parser.add_argument('--fasm', action='store_true')
    args = parser.parse_args()
    file_name = args.file
    is_fasm = args.fasm
    texts = get_texts(file_name)
    if is_fasm:
        output = convert_to_fasm(texts)
    with open('out.asm', 'w') as file:
        file.write(output)
