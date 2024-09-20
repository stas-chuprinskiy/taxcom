from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path
import re
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).parent.resolve()
FILES_DIR = BASE_DIR.joinpath("docs").resolve()
OUTPUT_PATH = BASE_DIR.joinpath("result.json").resolve()
OUTPUT_ENCODING = "utf-8"


@dataclass
class FileCfg:
    file_path: Path
    file_encoding: str
    row_pattern: str


@dataclass
class Item:
    item_id: int
    item_name: str


class ItemEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Item):
            return {"item_id": obj.item_id, "item_name": obj.item_name}

        return super().default(obj)


def parse_item(line: str, row_pattern: str) -> Item:
    parsed_item = re.match(row_pattern, line)

    if not parsed_item:
        raise Exception(f"Item not parsed using a pattern `{row_pattern}`, {line=}")

    item_id = int(parsed_item.group("item_id"))
    item_name = str(parsed_item.group("item_name"))

    return Item(item_id, item_name)


def parse_file(file_cfg: FileCfg) -> list[Item]:
    if not file_cfg.file_path.is_file():
        raise Exception(f"File not found at `{file_cfg.file_path}`")

    if not os.access(file_cfg.file_path, os.R_OK):
        raise Exception(f"File at `{file_cfg.file_path}` not readable")

    parsed_items = []
    with open(file_cfg.file_path, "r", encoding=file_cfg.file_encoding) as file:
        for line_number, line in enumerate(file, start=1):
            try:
                item = parse_item(line.strip(), file_cfg.row_pattern)
                parsed_items.append(item)
            except Exception:
                logger.error(
                    f"Item not parsed: pattern={file_cfg.row_pattern}, {line_number=}, {line=}"
                )

    return parsed_items


def sort_items(items: list[Item]) -> list[Item]:
    return sorted(items, key=lambda x: x.item_name)


def save_items_in_json(
    items: list[Item],
    output_path: Path = OUTPUT_PATH,
    output_encoding: str = OUTPUT_ENCODING,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    output_dir = output_path.parent.resolve()

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path.touch(exist_ok=True)
    except Exception as ex:
        raise Exception(f"Error occured while creating `{output_path}`, {ex=}")

    if not os.access(output_path, os.W_OK):
        raise Exception(f"Output path `{output_path}` is not writtable")

    with open(output_path, "w", encoding=output_encoding) as file:
        json.dump(
            items, file, cls=ItemEncoder, indent=indent, ensure_ascii=ensure_ascii
        )

    logger.info(f"Successfully saved {len(items)} items at `{output_path}`")


def main():
    # Определяем конфиги input-файлов
    file_cfg_list = [
        FileCfg(
            file_path=FILES_DIR.joinpath("Тестовый файл1.txt").resolve(),
            file_encoding="utf-8",
            row_pattern=r"(?P<item_id>\d+),\s*(?P<item_name>.+)",
        ),
        FileCfg(
            file_path=FILES_DIR.joinpath("Тестовый файл2.txt").resolve(),
            file_encoding="windows-1251",
            row_pattern=r'"(?P<item_name>[^"]+)";\s*"(?P<item_id>\d+)"',
        ),
    ]

    logger.info("Started parsing process")

    # Парсим данные
    items: list[Item] = []
    for file_cfg in file_cfg_list:
        logger.info(f"Started parsing file `{file_cfg.file_path.name}`")

        try:
            parsed_items = parse_file(file_cfg)
            items += parsed_items
        except Exception as ex:
            logger.error(ex)
        else:
            logger.info(
                f"Successfully finished parsing file `{file_cfg.file_path.name}`"
            )

    # Сортируем данные
    sorted_items = sort_items(items)

    # Сохраняем данные в json
    try:
        save_items_in_json(sorted_items)
    except Exception as ex:
        logger.error(ex)

    logger.info("Finished parsing process")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
