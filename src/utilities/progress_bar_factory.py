from click._termui_impl import ProgressBar


def create_loading_bar(label: str, iterable_generator, length: int):
    return ProgressBar(
        iterable_generator,
        length=length,
        label=label,
        fill_char="*",
        empty_char="-",
        bar_template="%(label)s [%(bar)s] %(info)s",
        color="blue",
    )
