from click._termui_impl import ProgressBar


def create_bar(label: str, iterable_data, length: int):
    return ProgressBar(iterable_data, length=length, label=label, fill_char="*", empty_char="-",
                       bar_template="%(label)s [%(bar)s] %(info)s", color="blue")
